"""Download the Olist archive from its publisher and verify its SHA-256."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
manifest = json.loads((DATA / "source-manifest.json").read_text(encoding="utf-8"))
target = DATA / manifest["archive_location"]
expected = manifest["zip_sha256"]

if target.exists():
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError("Existing archive has a different SHA-256; preserve it and investigate.")
    print("Official archive already present and verified:", target)
else:
    partial = DATA / (target.name + ".partial")
    if partial.exists():
        raise ValueError("A partial download already exists; inspect or remove that file before retrying.")
    digest = hashlib.sha256()
    try:
        with urlopen(manifest["url"], timeout=60) as response, partial.open("xb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                digest.update(chunk)
            output.flush()
            os.fsync(output.fileno())
        if digest.hexdigest() != expected:
            raise ValueError("Downloaded archive SHA-256 differs from the recorded Olist v2 archive.")
        os.replace(partial, target)
        print("Downloaded and verified:", target)
    except Exception:
        # A known partial file in the data directory is never treated as source data.
        partial.unlink(missing_ok=True)
        raise
