from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image

from gameplay_image2_specs import SPECS


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
BASE_DIR = ASSET_DIR / "image2-generated-bases"
OUT = ASSET_DIR / "image2-precision-audit.csv"


def main() -> None:
    rows = []
    for spec in SPECS:
        stem = spec["stem"]
        final_path = ASSET_DIR / f"{stem}.png"
        base_path = BASE_DIR / f"{stem}.base.png"
        if final_path.exists():
            size = Image.open(final_path).size
        else:
            size = None
        rows.append(
            {
                "Diagram": stem,
                "Image2BaseExists": "YES" if base_path.exists() else "NO",
                "FinalPngExists": "YES" if final_path.exists() else "NO",
                "FinalSize": f"{size[0]}x{size[1]}" if size else "",
                "ReferenceGrid": "40px",
                "OverlayLabels": len(spec["labels"]),
                "Status": "PASS" if base_path.exists() and final_path.exists() and size == (1600, 900) else "RECHECK",
            }
        )
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()

