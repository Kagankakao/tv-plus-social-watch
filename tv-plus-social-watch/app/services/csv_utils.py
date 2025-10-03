import csv
from pathlib import Path
import os
from typing import List, Dict


DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parents[1] / "data"))


def read_csv(filename: str) -> List[Dict[str, str]]:
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def append_csv(filename: str, row: Dict[str, str]) -> None:
    path = DATA_DIR / filename
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not exists:
            writer.writeheader()
        writer.writerow(row)


