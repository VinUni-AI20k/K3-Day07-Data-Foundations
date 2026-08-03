"""Validate the K3 corpus and its sources.csv manifest."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest import parse_front_matter  # noqa: E402

DATA_DIR = ROOT / "data" / "k3_university"
REQUIRED = {
    "doc_id",
    "title",
    "source_url",
    "retrieved_at",
    "document_version",
    "audience",
    "category",
    "language",
}
ALLOWED_AUDIENCES = {"student", "faculty", "staff", "all"}


def valid_url(value: object) -> bool:
    parsed = urlparse(str(value or ""))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    files = sorted([*DATA_DIR.glob("*.md"), *DATA_DIR.glob("*.txt")])
    errors: list[str] = []
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in files:
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"{path.name}: invalid UTF-8 ({error})")
            continue
        metadata, body = parse_front_matter(raw)
        missing = sorted(key for key in REQUIRED if metadata.get(key) in {None, ""})
        doc_id = str(metadata.get("doc_id") or "")
        if missing:
            errors.append(f"{path.name}: missing metadata {missing}")
        if doc_id in seen:
            errors.append(f"{path.name}: duplicate doc_id {doc_id}")
        seen.add(doc_id)
        if not body.strip():
            errors.append(f"{path.name}: empty content")
        if not valid_url(metadata.get("source_url")):
            errors.append(f"{path.name}: invalid source_url")
        if metadata.get("audience") not in ALLOWED_AUDIENCES:
            errors.append(f"{path.name}: invalid audience {metadata.get('audience')!r}")
        records.append(
            {
                "file": path.name,
                "doc_id": doc_id,
                "category": metadata.get("category"),
                "source_url": metadata.get("source_url"),
                "characters": len(body),
                "metadata_complete": not missing,
            }
        )

    manifest_path = DATA_DIR / "sources.csv"
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    manifest_ids = {row.get("doc_id", "") for row in manifest}
    if manifest_ids != seen:
        errors.append(
            "sources.csv mismatch: "
            f"missing={sorted(seen - manifest_ids)}, extra={sorted(manifest_ids - seen)}"
        )
    for row in manifest:
        if not valid_url(row.get("source_url")):
            errors.append(f"sources.csv: invalid source_url for {row.get('doc_id')}")
        if not row.get("license_or_permission"):
            errors.append(f"sources.csv: missing permission for {row.get('doc_id')}")

    result = {
        "document_count": len(files),
        "valid_document_count": len(files) if not errors else len(files) - len({e.split(':', 1)[0] for e in errors}),
        "categories": sorted({str(item["category"]) for item in records}),
        "records": records,
        "errors": errors,
        "valid": 5 <= len(files) <= 10 and not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
