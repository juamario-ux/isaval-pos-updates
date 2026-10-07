import hashlib,json,os,pathlib,re,subprocess
cfg=json.loads(pathlib.Path("incoming/release.json").read_text())
apk=pathlib.Path("incoming/IsaVal-POS.apk")
if apk.stat().st_size>64*1024*1024 or hashlib.sha256(apk.read_bytes()).hexdigest()!=cfg["sha256"]:
    raise SystemExit("APK checksum mismatch")
sdk=pathlib.Path(os.environ["ANDROID_HOME"])
versions=sorted((sdk/"build-tools").iterdir(),key=lambda p:tuple(int(x) for x in re.findall(r"\d+",p.name)))
tools=versions[-1]
signatures=subprocess.check_output([str(tools/"apksigner"),"verify","--min-sdk-version","25","--print-certs",str(apk)],text=True)
digests=re.findall(r"certificate SHA-256 digest:\s*([0-9a-f]{64})",signatures,re.I)
if [d.lower() for d in digests]!=["5538ed457f4770ed14f96f626ded3c217ab969de143872c98a2f52447ab0165b"]:
    raise SystemExit("Unexpected signer")
badging=subprocess.check_output([str(tools/"aapt"),"dump","badging",str(apk)],text=True)
package=re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'",badging)
if not package or package.group(1)!="com.isaval.pos" or int(package.group(2))!=cfg["versionCode"] or package.group(3)!=cfg["versionName"]:
    raise SystemExit("Unexpected package version")
name=cfg["versionName"]
if not re.fullmatch(r"\d+\.\d+\.\d+",name) or not isinstance(cfg["versionCode"],int):
    raise SystemExit("Invalid version")
tag="v"+name+"-build"+str(cfg["versionCode"])
previous=subprocess.run(["gh","release","download","--pattern","version.json","--output","channel.json"],capture_output=True)
if previous.returncode==0 and cfg["versionCode"]<=json.loads(pathlib.Path("channel.json").read_text())["versionCode"]:
    raise SystemExit("Channel already contains this or a newer version")
view=subprocess.run(["gh","release","view",tag,"--json","isDraft"],capture_output=True,text=True)
if view.returncode==0:
    if not json.loads(view.stdout)["isDraft"]: raise SystemExit("Release already published")
else:
    subprocess.run(["gh","release","create",tag,"--draft","--title","IsaVal POS "+name,"--notes",cfg["notes"]],check=True)
subprocess.run(["gh","release","upload",tag,str(apk),"--clobber"],check=True)
apk.unlink()  # publish.py downloads and verifies the draft into this same directory

env=dict(os.environ,DRAFT_TAG=tag,RELEASE_NOTES=cfg["notes"],GITHUB_OUTPUT=str(pathlib.Path("publish-output.txt").resolve()))
subprocess.run(["python3","publish.py"],env=env,check=True)
subprocess.run(["gh","release","upload",tag,"IsaVal-POS.apk","version.json","--clobber"],check=True)
subprocess.run(["gh","release","edit",tag,"--title","IsaVal POS "+name+" build "+str(cfg["versionCode"]),"--notes-file","release-notes.txt","--draft=false","--latest"],check=True)
