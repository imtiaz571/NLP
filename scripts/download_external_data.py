"""Download the external Kaggle corpora declared in external_sources.json.

Public datasets use Kaggle's download API and normally do not require an API
token. If Kaggle requires terms acceptance, visit the dataset page once while
signed in, then rerun this command.

Usage:
    python data/download_external_data.py
    python data/download_external_data.py --source dailydialog --force
"""

from __future__ import annotations

import argparse
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "external_sources.json"
EXTERNAL_DIR = ROOT / "data" / "external"
RAW_DIR = EXTERNAL_DIR / "raw"


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "NPC-Talk/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as stream:
        shutil.copyfileobj(response, stream)
    temporary.replace(destination)


def _safe_extract(archive: zipfile.ZipFile, target_dir: Path) -> None:
    """Extract a ZIP while rejecting absolute paths and parent traversal."""
    root = target_dir.resolve()
    for member in archive.infolist():
        destination = (target_dir / member.filename).resolve()
        if not destination.is_relative_to(root):
            raise RuntimeError(f"Unsafe path in downloaded archive: {member.filename}")
    archive.extractall(target_dir)


def download_source(source: dict, force: bool = False) -> None:
    source_id = source["id"]
    target_dir = ROOT / source["local_dir"]
    target_dir.mkdir(parents=True, exist_ok=True)
    file_name = source.get("download_file")
    suffix = Path(file_name).suffix if file_name else ".zip"
    archive_path = RAW_DIR / f"{source_id}{suffix}"

    if target_dir.exists() and any(target_dir.iterdir()) and not force:
        print(f"[skip] {source_id}: already present at {target_dir}")
        return

    dataset_ref = source["kaggle"]
    url = f"https://www.kaggle.com/api/v1/datasets/download/{dataset_ref}"
    if file_name:
        url += f"/{file_name}"
    print(f"[download] {source_id}: {url}")
    _download(url, archive_path)

    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path) as archive:
            _safe_extract(archive, target_dir)
    elif file_name:
        shutil.copy2(archive_path, target_dir / file_name)
    else:
        raise RuntimeError(f"Kaggle returned a non-ZIP response for {source_id}")
    print(f"[ok] {source_id}: {target_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", help="Source id; repeat to select several")
    parser.add_argument("--force", action="store_true", help="Download and extract again")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    selected = set(args.source or [])
    known = {source["id"] for source in manifest["sources"]}
    unknown = selected - known
    if unknown:
        parser.error(f"unknown source(s): {', '.join(sorted(unknown))}")

    for source in manifest["sources"]:
        if not selected or source["id"] in selected:
            download_source(source, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
