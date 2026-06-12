from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image

from gameplay_image2_layouts import ANNOTATION_BOXES, EXTRA_CALLOUTS, LAYOUTS
from gameplay_image2_specs import SPECS


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
BASE_DIR = ASSET_DIR / "image2-generated-bases"
EN_ASSET_DIR = ASSET_DIR / "en"
OUT = ASSET_DIR / "image2-precision-audit.csv"
EXPECTED_SIZE = (1672, 941)


def main() -> None:
    rows = []
    for spec in SPECS:
        stem = spec["stem"]
        zh_path = ASSET_DIR / f"{stem}.png"
        en_path = EN_ASSET_DIR / f"{stem}.png"
        base_path = BASE_DIR / f"{stem}.base.png"
        zh_size = Image.open(zh_path).size if zh_path.exists() else None
        en_size = Image.open(en_path).size if en_path.exists() else None
        layout = LAYOUTS[stem]
        ok = (
            base_path.exists()
            and zh_path.exists()
            and en_path.exists()
            and zh_size == EXPECTED_SIZE
            and en_size == EXPECTED_SIZE
        )
        rows.append(
            {
                "Diagram": stem,
                "Image2BaseExists": "YES" if base_path.exists() else "NO",
                "ChinesePngExists": "YES" if zh_path.exists() else "NO",
                "EnglishPngExists": "YES" if en_path.exists() else "NO",
                "ChineseSize": f"{zh_size[0]}x{zh_size[1]}" if zh_size else "",
                "EnglishSize": f"{en_size[0]}x{en_size[1]}" if en_size else "",
                "ReferenceGrid": "40px",
                "OverlayLabels": len(spec["labels"]),
                "TextPlacement": "in_artwork_callouts",
                "CalloutBoxes": len(ANNOTATION_BOXES[stem]) + len(EXTRA_CALLOUTS.get(stem, [])),
                "PlacementReason": f"{layout['reason']} 标注回填到底图预留框，未叠加额外网格。",
                "Status": "PASS" if ok else "RECHECK",
            }
        )
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
