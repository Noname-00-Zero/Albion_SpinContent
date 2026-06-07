"""Accuracy check: verify every item name matches its Albion item_id.

Pulls the official EN-US name from the Albion gameinfo API and compares it
against the name we display in the app. Run:  python verify_items.py
"""

from __future__ import annotations

import json
import re
import time
import urllib.request

import app_roulette as a

API = "https://gameinfo.albiononline.com/api/gameinfo/items/{}/data"
HEADERS = {"User-Agent": "Mozilla/5.0 (AlbionMaster verify)"}


def official_name(item_id: str) -> str | None:
    req = urllib.request.Request(API.format(item_id), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.load(r)
    return data.get("localizedNames", {}).get("EN-US")


def base(name: str) -> str:
    """Strip our '(Cloth)/(Leather)/(Plate)' suffix + lowercase for matching."""
    return re.sub(r"\s*\(.*?\)", "", name).strip().lower()


def collect() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for w in a.MAIN_HANDS:
        pairs.append((w.name, w.item_id))
    for grp in (a.OFF_HANDS, a.ARMOR_HEAD, a.ARMOR_CHEST, a.ARMOR_SHOES, a.CAPES):
        for it in grp:
            if it.item_id:  # skip "No Cape" (empty id)
                pairs.append((it.name, it.item_id))
    return pairs


def main() -> None:
    pairs = collect()
    print(f"Checking {len(pairs)} items against Albion gameinfo API...\n")
    mismatches, errors = [], []
    for name, item_id in pairs:
        try:
            official = official_name(item_id)
        except Exception as e:  # noqa: BLE001
            errors.append((name, item_id, str(e)))
            print(f"[ERR ] {name:<28} {item_id:<34} {e}")
            continue
        if official is None:
            errors.append((name, item_id, "no EN-US name"))
            print(f"[ERR ] {name:<28} {item_id:<34} no name")
            continue
        ok = base(name) in official.lower()
        tag = "[ OK ]" if ok else "[FAIL]"
        if not ok:
            mismatches.append((name, item_id, official))
        print(f"{tag} {name:<28} {item_id:<34} -> {official}")
        time.sleep(0.05)

    print("\n" + "=" * 60)
    print(f"Total      : {len(pairs)}")
    print(f"Mismatches : {len(mismatches)}")
    print(f"Errors     : {len(errors)}")
    if mismatches:
        print("\n--- NAME/IMAGE MISMATCHES (must fix) ---")
        for name, item_id, official in mismatches:
            print(f"  {name}  ({item_id})  is actually: {official}")
    if not mismatches and not errors:
        print("\nALL ITEMS MATCH. Image == Name, every slot. [PASS]")


if __name__ == "__main__":
    main()
