import hashlib, json, os, pathlib, re, subprocess
tag = os.environ["DRAFT_TAG"]
if not re.fullmatch(r"v\d+\.\d+\.\d+-build\d+", tag):
    raise SystemExit("Unexpected release tag.")
# Recover a saved draft when GitHub's tag picker could not validate a new tag.
releases = json.loads(subprocess.check_output(["gh", "api", "repos/" + os.environ["GITHUB_REPOSITORY"] + "/releases"], text=True))
if not any(r["tag_name"] == tag for r in releases):
    expected_title = "IsaVal POS " + tag[1:].split("-build")[0]
    drafts = [r for r in releases if r["draft"] and not r["tag_name"] and r["name"] == expected_title]
    if len(drafts) != 1:
        raise SystemExit("Expected exactly one untagged draft with the requested version title.")
    draft = drafts[0]
    subprocess.run(["gh", "api", "--method", "PATCH", "repos/" + os.environ["GITHUB_REPOSITORY"] + "/releases/" + str(draft["id"]), "-f", "tag_name=" + tag], check=True, stdout=subprocess.DEVNULL)
release = json.loads(subprocess.check_output(["gh", "release", "view", tag, "--repo", os.environ["GITHUB_REPOSITORY"], "--json", "isDraft,tagName"], text=True))
if not release["isDraft"]:
    raise SystemExit("Only draft releases can be promoted.")
subprocess.run(["gh", "release", "download", tag, "--repo", os.environ["GITHUB_REPOSITORY"], "--pattern", "*.apk", "--dir", "incoming"], check=True)
apks = list(pathlib.Path("incoming").glob("*.apk"))
if len(apks) != 1 or apks[0].stat().st_size > 64 * 1024 * 1024:
    raise SystemExit("Expected exactly one APK, no larger than 64 MiB.")
pathlib.Path("IsaVal-POS.apk").write_bytes(apks[0].read_bytes())
sdk = pathlib.Path(os.environ["ANDROID_HOME"])
versions = sorted((sdk / "build-tools").iterdir(), key=lambda p: tuple(int(x) for x in re.findall(r"\d+", p.name)))
tools = versions[-1]
verification = subprocess.check_output([str(tools/"apksigner"), "verify", "--min-sdk-version", "25", "--verbose", "--print-certs", "IsaVal-POS.apk"], text=True)
print(verification)
digests = [value.lower() for value in re.findall(r"certificate SHA-256 digest:\s*([0-9a-f]{64})", verification, re.IGNORECASE)]
if digests != ["5538ed457f4770ed14f96f626ded3c217ab969de143872c98a2f52447ab0165b"]:
    raise SystemExit("Signing certificate does not match IsaVal POS.")
badging = subprocess.check_output([str(tools/"aapt"), "dump", "badging", "IsaVal-POS.apk"], text=True)
package = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", badging)
if not package or package.group(1) != "com.isaval.pos":
    raise SystemExit("Unexpected applicationId.")
code = int(package.group(2))
name = package.group(3)
if not re.fullmatch(r"\d+\.\d+\.\d+", name):
    raise SystemExit("Expected semantic version.")
previous = subprocess.run(["gh", "release", "download", "--repo", os.environ["GITHUB_REPOSITORY"], "--pattern", "version.json", "--output", "previous-version.json"], capture_output=True)
if previous.returncode == 0 and code <= json.loads(pathlib.Path("previous-version.json").read_text())["versionCode"]:
    raise SystemExit("Only versions newer than the published channel can be promoted.")
expected_tag = "v" + name + "-build" + str(code)
if tag != expected_tag:
    raise SystemExit("Draft tag does not match the APK version.")
notes = os.environ.get("RELEASE_NOTES", "Nueva versión de IsaVal POS.")
manifest = {"versionCode": code, "versionName": name,
    "apkUrl": "https://github.com/" + os.environ["GITHUB_REPOSITORY"] + "/releases/download/" + tag + "/IsaVal-POS.apk",
    "sha256": hashlib.sha256(pathlib.Path("IsaVal-POS.apk").read_bytes()).hexdigest(), "notes": notes}
pathlib.Path("version.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
pathlib.Path("release-notes.txt").write_text(notes + "\n\nVersionCode: " + str(code) + "\nSHA-256: " + manifest["sha256"] + "\n")
with open(os.environ["GITHUB_OUTPUT"], "a") as output:
    output.write("tag=" + tag + "\n")
    output.write("name=" + name + "\n")
