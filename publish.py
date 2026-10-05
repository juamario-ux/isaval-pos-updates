import hashlib, json, os, pathlib, re, subprocess, urllib.parse, urllib.request, zipfile
source = os.environ["SOURCE_URL"]
parsed = urllib.parse.urlparse(source)
if parsed.scheme != "https" or not (parsed.hostname or "").endswith(".oaiusercontent.com"):
    raise SystemExit("Use the temporary artifact download URL returned by the GitHub connector.")
with urllib.request.urlopen(source, timeout=30) as response:
    if not response.geturl().startswith("https://"):
        raise SystemExit("HTTPS required.")
    archive = response.read(16 * 1024 * 1024 + 1)
if len(archive) > 16 * 1024 * 1024:
    raise SystemExit("Artifact is too large.")
pathlib.Path("artifact.zip").write_bytes(archive)
with zipfile.ZipFile("artifact.zip") as bundle:
    entries = [entry for entry in bundle.infolist() if entry.filename.endswith(".apk")]
    if len(entries) != 1 or entries[0].file_size > 64 * 1024 * 1024:
        raise SystemExit("Expected one APK, no larger than 64 MiB.")
    pathlib.Path("IsaVal-POS.apk").write_bytes(bundle.read(entries[0]))
sdk = pathlib.Path(os.environ["ANDROID_HOME"])
versions = sorted((sdk / "build-tools").iterdir(), key=lambda p: tuple(int(x) for x in re.findall(r"\d+", p.name)))
tools = versions[-1]
verification = subprocess.check_output([str(tools/"apksigner"), "verify", "--min-sdk-version", "25", "--verbose", "--print-certs", "IsaVal-POS.apk"], text=True)
digests = re.findall(r"Signer #\d+ certificate SHA-256 digest: ([0-9a-f]+)", verification)
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
tag = "v" + name + "-build" + str(code)
notes = os.environ.get("RELEASE_NOTES", "Nueva versión de IsaVal POS.")
manifest = {"versionCode": code, "versionName": name,
    "apkUrl": "https://github.com/" + os.environ["GITHUB_REPOSITORY"] + "/releases/download/" + tag + "/IsaVal-POS.apk",
    "sha256": hashlib.sha256(pathlib.Path("IsaVal-POS.apk").read_bytes()).hexdigest(), "notes": notes}
pathlib.Path("version.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
pathlib.Path("release-notes.txt").write_text(notes + "\n\nVersionCode: " + str(code) + "\nSHA-256: " + manifest["sha256"] + "\n")
with open(os.environ["GITHUB_OUTPUT"], "a") as output:
    output.write("tag=" + tag + "\n")
    output.write("name=" + name + "\n")
