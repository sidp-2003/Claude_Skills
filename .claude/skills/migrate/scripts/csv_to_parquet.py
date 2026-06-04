"""
Convert CSVs from the latest dated folder in fetchAPI/data to Parquet files,
saving them under migrate/data/<same-date-folder>/.
"""

import sys
from pathlib import Path

import pandas as pd

FETCH_DATA = Path(__file__).parents[2] / "fetchAPI" / "data"
MIGRATE_DATA = Path(__file__).parent.parent / "data"


def latest_folder(base: Path) -> Path:
    dated = sorted(
        (d for d in base.iterdir() if d.is_dir()),
        key=lambda d: d.name,
    )
    if not dated:
        print(f"No dated folders found in {base}", file=sys.stderr)
        sys.exit(1)
    return dated[-1]


def convert(src_folder: Path, dst_folder: Path) -> None:
    dst_folder.mkdir(parents=True, exist_ok=True)
    csv_files = list(src_folder.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {src_folder}", file=sys.stderr)
        sys.exit(1)

    for csv_path in sorted(csv_files):
        df = pd.read_csv(csv_path)
        out_path = dst_folder / (csv_path.stem + ".parquet")
        df.to_parquet(out_path, index=False)
        print(f"  {csv_path.name} → {out_path.relative_to(MIGRATE_DATA.parent.parent)}")


def main() -> None:
    src = latest_folder(FETCH_DATA)
    dst = MIGRATE_DATA / src.name
    print(f"Source : {src}")
    print(f"Output : {dst}")
    convert(src, dst)
    print("Done.")


if __name__ == "__main__":
    main()
