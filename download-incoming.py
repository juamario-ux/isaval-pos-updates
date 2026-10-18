import io, json, pathlib, urllib.request, zipfile, hashlib
cfg=json.loads(pathlib.Path("incoming/release.json").read_text())
url=cfg.get("artifactUrl","")
if url:
    if not url.startswith("https://sdmntpr") or ".oaiusercontent.com/" not in url.split("?")[0]:
        raise SystemExit("Unexpected artifact host")
    with urllib.request.urlopen(url,timeout=45) as response:
        data=response.read(64*1024*1024+1)
    if len(data)>64*1024*1024: raise SystemExit("Artifact exceeds limit")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names=[n for n in archive.namelist() if n.endswith(".apk")]
        if len(names)!=1 or archive.getinfo(names[0]).file_size>64*1024*1024:
            raise SystemExit("Expected one APK")
        apk=archive.read(names[0])
    if hashlib.sha256(apk).hexdigest()!=cfg["sha256"]: raise SystemExit("Artifact checksum mismatch")
    pathlib.Path("incoming/IsaVal-POS.apk").write_bytes(apk)
