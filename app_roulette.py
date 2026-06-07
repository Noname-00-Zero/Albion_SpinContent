"""
Albion Master — Streamer Build Roulette & Challenge Generator
=============================================================
Single-page Streamlit app (V1.1 — Visual Edition) for the global Albion
Online community.

Self-contained Level-1 app. Zero external DB. Hardcoded datasets only.
Does NOT import or touch any trading / Riko_Genesis modules.

Item art is pulled live from the official Albion Render API:
    https://render.albiononline.com/v1/item/{ITEM_ID}.png

Run:
    streamlit run app_roulette.py
"""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
KOFI_URL = "https://ko-fi.com/albioncode"                # <- your Ko-fi page
ADSENSE_CLIENT = "ca-pub-0000000000000000"               # <- your AdSense id
RENDER_SIZE = 180                                         # px image size
SPIN_DELAY = 2.4                                          # suspense seconds

# Tier system — each item rolls a random tier (T4-T8) for extra chaos.
TIERS = ["T4", "T5", "T6", "T7", "T8"]
TIER_WEIGHTS = [32, 28, 22, 12, 6]                       # lower tiers more common
TIER_NAMES = {
    "T4": "Adept's",
    "T5": "Expert's",
    "T6": "Master's",
    "T7": "Grandmaster's",
    "T8": "Elder's",
}
TIER_COLORS = {
    "T4": "#9aa0b0",   # grey-blue
    "T5": "#4caf6d",   # green
    "T6": "#3d8bff",   # blue
    "T7": "#b56bff",   # purple
    "T8": "#f5a623",   # orange/gold
}

# Funny loading lines shown during the suspense spin (great for live streams).
RNG_LINES = [
    "Praying to the RNG Gods...",
    "Bribing the loot goblin...",
    "Consulting the Caerleon black market...",
    "Rolling the dice of destiny...",
    "Summoning a cursed build...",
    "Asking Morgana for a favor...",
    "Shuffling the destiny board...",
]

st.set_page_config(
    page_title="Albion Master — Build Roulette",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def item_image_url(base_id: str, tier: str = "T4") -> str:
    """Build the Albion Render API URL for a tier-prefixed item id."""
    return (
        f"https://render.albiononline.com/v1/item/{tier}_{base_id}.png"
        f"?size={RENDER_SIZE}&quality=1"
    )


def roll_tier() -> str:
    """Pick a random item tier (T4-T8), weighted toward lower tiers."""
    return random.choices(TIERS, weights=TIER_WEIGHTS, k=1)[0]


def tiered_name(item: Item, tier: str) -> str:
    """Full in-game style name, e.g. 'Master's Greataxe'."""
    return f"{TIER_NAMES.get(tier, '')} {item.name}".strip()


# ---------------------------------------------------------------------------
# DATASET (Task 1)  — name -> internal item id, with roll weights
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Item:
    name: str
    item_id: str
    weight: int = 10


@dataclass(frozen=True)
class Weapon(Item):
    archetype: str = ""
    two_handed: bool = False


# --- Main hands ------------------------------------------------------------
MAIN_HANDS: list[Weapon] = [
    # One-handed (off-hand allowed)
    Weapon("Broadsword", "MAIN_SWORD", 12, "Sword"),
    Weapon("Dagger", "MAIN_DAGGER", 9, "Dagger"),
    Weapon("Bloodletter", "MAIN_RAPIER_MORGANA", 10, "Dagger"),
    Weapon("Spear", "MAIN_SPEAR", 8, "Spear"),
    Weapon("Nature Staff", "MAIN_NATURESTAFF", 8, "Nature Staff"),
    Weapon("Druidic Staff", "MAIN_NATURESTAFF_KEEPER", 7, "Nature Staff"),
    Weapon("Holy Staff", "MAIN_HOLYSTAFF", 8, "Holy Staff"),
    Weapon("Fire Staff", "MAIN_FIRESTAFF", 9, "Fire Staff"),
    Weapon("Frost Staff", "MAIN_FROSTSTAFF", 8, "Frost Staff"),
    Weapon("Cursed Staff", "MAIN_CURSEDSTAFF", 9, "Cursed Staff"),
    Weapon("Arcane Staff", "MAIN_ARCANESTAFF", 7, "Arcane Staff"),
    Weapon("Mace", "MAIN_MACE", 8, "Mace"),
    Weapon("Hammer", "MAIN_HAMMER", 6, "Hammer"),
    Weapon("Battleaxe", "MAIN_AXE", 10, "Axe"),
    # Two-handed (off-hand removed)
    Weapon("Longbow", "2H_LONGBOW", 11, "Bow", two_handed=True),
    Weapon("Bow", "2H_BOW", 9, "Bow", two_handed=True),
    Weapon("Bow of Badon", "2H_BOW_KEEPER", 7, "Bow", two_handed=True),
    Weapon("Greataxe", "2H_AXE", 9, "Axe", two_handed=True),
    Weapon("Realmbreaker", "2H_AXE_AVALON", 6, "Axe", two_handed=True),
    Weapon("Halberd", "2H_HALBERD", 7, "Spear", two_handed=True),
    Weapon("Pike", "2H_SPEAR", 6, "Spear", two_handed=True),
    Weapon("Claws", "2H_CLAWPAIR", 6, "Dagger", two_handed=True),
    Weapon("Claymore", "2H_CLAYMORE", 9, "Sword", two_handed=True),
    Weapon("Dual Swords", "2H_DUALSWORD", 8, "Sword", two_handed=True),
    Weapon("Great Fire Staff", "2H_FIRESTAFF", 8, "Fire Staff", two_handed=True),
    Weapon("Infernal Staff", "2H_INFERNOSTAFF", 6, "Fire Staff", two_handed=True),
    Weapon("Great Frost Staff", "2H_FROSTSTAFF", 7, "Frost Staff", two_handed=True),
    Weapon("Great Cursed Staff", "2H_CURSEDSTAFF", 7, "Cursed Staff", two_handed=True),
    Weapon("Great Nature Staff", "2H_NATURESTAFF", 7, "Nature Staff", two_handed=True),
    Weapon("Great Arcane Staff", "2H_ARCANESTAFF", 6, "Arcane Staff", two_handed=True),
    Weapon("Crossbow", "2H_CROSSBOW", 8, "Crossbow", two_handed=True),
]

# --- Off-hands -------------------------------------------------------------
OFF_HANDS: list[Item] = [
    Item("Shield", "OFF_SHIELD", 13),
    Item("Tome of Spells", "OFF_BOOK", 10),
    Item("Torch", "OFF_TORCH", 10),
    Item("Eye of Secrets", "OFF_ORB_MORGANA", 8),
    Item("Muisak", "OFF_DEMONSKULL_HELL", 7),
    Item("Taproot", "OFF_TOTEM_KEEPER", 6),
    Item("Mistcaller", "OFF_HORN_KEEPER", 5),
]

# --- Armor (Cloth / Leather / Plate -> SET1/SET2/SET3) ---------------------
ARMOR_HEAD: list[Item] = [
    Item("Scholar Cowl (Cloth)", "HEAD_CLOTH_SET1", 12),
    Item("Cleric Cowl (Cloth)", "HEAD_CLOTH_SET2", 8),
    Item("Mage Cowl (Cloth)", "HEAD_CLOTH_SET3", 7),
    Item("Mercenary Hood (Leather)", "HEAD_LEATHER_SET1", 12),
    Item("Hunter Hood (Leather)", "HEAD_LEATHER_SET2", 10),
    Item("Assassin Hood (Leather)", "HEAD_LEATHER_SET3", 8),
    Item("Soldier Helmet (Plate)", "HEAD_PLATE_SET1", 12),
    Item("Knight Helmet (Plate)", "HEAD_PLATE_SET2", 10),
    Item("Guardian Helmet (Plate)", "HEAD_PLATE_SET3", 8),
]

ARMOR_CHEST: list[Item] = [
    Item("Scholar Robe (Cloth)", "ARMOR_CLOTH_SET1", 12),
    Item("Cleric Robe (Cloth)", "ARMOR_CLOTH_SET2", 8),
    Item("Mage Robe (Cloth)", "ARMOR_CLOTH_SET3", 7),
    Item("Mercenary Jacket (Leather)", "ARMOR_LEATHER_SET1", 12),
    Item("Hunter Jacket (Leather)", "ARMOR_LEATHER_SET2", 10),
    Item("Assassin Jacket (Leather)", "ARMOR_LEATHER_SET3", 8),
    Item("Soldier Armor (Plate)", "ARMOR_PLATE_SET1", 12),
    Item("Knight Armor (Plate)", "ARMOR_PLATE_SET2", 10),
    Item("Guardian Armor (Plate)", "ARMOR_PLATE_SET3", 8),
]

ARMOR_SHOES: list[Item] = [
    Item("Scholar Sandals (Cloth)", "SHOES_CLOTH_SET1", 12),
    Item("Cleric Sandals (Cloth)", "SHOES_CLOTH_SET2", 8),
    Item("Mage Sandals (Cloth)", "SHOES_CLOTH_SET3", 7),
    Item("Mercenary Shoes (Leather)", "SHOES_LEATHER_SET1", 12),
    Item("Hunter Shoes (Leather)", "SHOES_LEATHER_SET2", 10),
    Item("Assassin Shoes (Leather)", "SHOES_LEATHER_SET3", 8),
    Item("Soldier Boots (Plate)", "SHOES_PLATE_SET1", 12),
    Item("Knight Boots (Plate)", "SHOES_PLATE_SET2", 10),
    Item("Guardian Boots (Plate)", "SHOES_PLATE_SET3", 8),
]

# --- Capes -----------------------------------------------------------------
CAPES: list[Item] = [
    Item("No Cape", "", 6),
    Item("Thetford Cape", "CAPEITEM_FW_THETFORD", 10),
    Item("Fort Sterling Cape", "CAPEITEM_FW_FORTSTERLING", 10),
    Item("Lymhurst Cape", "CAPEITEM_FW_LYMHURST", 10),
    Item("Bridgewatch Cape", "CAPEITEM_FW_BRIDGEWATCH", 10),
    Item("Martlock Cape", "CAPEITEM_FW_MARTLOCK", 10),
    Item("Caerleon Cape", "CAPEITEM_FW_CAERLEON", 8),
    Item("Heretic Cape", "CAPEITEM_HERETIC", 7),
    Item("Undead Cape", "CAPEITEM_UNDEAD", 7),
    Item("Keeper Cape", "CAPEITEM_KEEPER", 7),
    Item("Morgana Cape", "CAPEITEM_MORGANA", 7),
    Item("Demon Cape", "CAPEITEM_DEMON", 6),
]

CHALLENGES: list[tuple[str, int]] = [
    ("☠️ Must enter the Black Zone with this build", 10),
    ("🐎 No Mounts allowed during this run", 9),
    ("🧪 Cannot use healing potions", 9),
    ("⚔️ Must secure 1 PvP kill before changing gear", 10),
    ("💰 No banking — keep everything you loot for 30 min", 7),
    ("🏃 Cannot retreat from a fight you started", 8),
    ("👥 Solo only — no grouping for this run", 8),
    ("🍖 No food buffs allowed", 7),
    ("🎯 Must gank at least 1 player in the Red Zone", 8),
    ("🛑 Permadeath: One death = restart the spin", 6),
    ("🗺️ Roam only one cluster — no jumping zones", 6),
    ("💎 Must dive a random dungeon you've never cleared", 7),
    ("🔥 Full-loot duel any player who challenges you", 7),
    ("🤝 First viewer in chat picks your destination", 8),
]


# ---------------------------------------------------------------------------
# SPIN ENGINE (Task 2) — weighted randomizer
# ---------------------------------------------------------------------------
def _weighted_choice(pool: list[str], weights: list[int]) -> str:
    return random.choices(pool, weights=weights, k=1)[0]


def _roll(pool: list[Item]) -> Item:
    return random.choices(pool, weights=[i.weight for i in pool], k=1)[0]


@dataclass
class Loadout:
    main_hand: Weapon
    off_hand: Item | None
    head: Item
    chest: Item
    shoes: Item
    cape: Item
    challenge: str
    tiers: dict = field(default_factory=dict)
    is_two_handed: bool = field(init=False)

    def __post_init__(self) -> None:
        self.is_two_handed = self.main_hand.two_handed


def spin() -> Loadout:
    """Roll a complete loadout. Enforces 2H weapon -> no off-hand."""
    main = _roll(MAIN_HANDS)
    off_hand = None if main.two_handed else _roll(OFF_HANDS)
    tiers = {
        "main": roll_tier(),
        "off": roll_tier() if off_hand else "T4",
        "head": roll_tier(),
        "chest": roll_tier(),
        "shoes": roll_tier(),
        "cape": roll_tier(),
    }
    return Loadout(
        main_hand=main,
        off_hand=off_hand,
        head=_roll(ARMOR_HEAD),
        chest=_roll(ARMOR_CHEST),
        shoes=_roll(ARMOR_SHOES),
        cape=_roll(CAPES),
        challenge=_weighted_choice(
            [c[0] for c in CHALLENGES], [c[1] for c in CHALLENGES]
        ),
        tiers=tiers,
    )


def _clean_challenge(challenge: str) -> str:
    if " " in challenge and not challenge[0].isalnum():
        return challenge.split(" ", 1)[1]
    return challenge


def _named(lo: Loadout, item: Item | None, slot: str, fallback: str) -> str:
    if item is None:
        return fallback
    return f"{tiered_name(item, lo.tiers.get(slot, 'T4'))} ({lo.tiers.get(slot, 'T4')})"


def loadout_to_text(lo: Loadout) -> str:
    """Plain-text summary — paste into Gemini / ChatGPT for reliable reading."""
    hand_type = "Two-Handed" if lo.is_two_handed else "One-Handed"
    main = f"{_named(lo, lo.main_hand, 'main', '')} [{lo.main_hand.archetype}, {hand_type}]"
    off = _named(lo, lo.off_hand, "off", "None (Two-Handed)")
    return (
        "ALBION ONLINE - RANDOM BUILD\n"
        "============================\n"
        f"Main Hand : {main}\n"
        f"Off-Hand  : {off}\n"
        f"Head      : {_named(lo, lo.head, 'head', '')}\n"
        f"Chest     : {_named(lo, lo.chest, 'chest', '')}\n"
        f"Shoes     : {_named(lo, lo.shoes, 'shoes', '')}\n"
        f"Cape      : {_named(lo, lo.cape, 'cape', 'None')}\n"
        f"Challenge : {_clean_challenge(lo.challenge)}\n"
        "============================\n"
        "Question for AI: Is this build viable? Suggest spec, food, and playstyle."
    )


def loadout_to_share(lo: Loadout) -> str:
    """Viral share text — pretty, with challenge + Ko-fi promo footer."""
    off = _named(lo, lo.off_hand, "off", "None (2H weapon)")
    return (
        "⚔️ ALBION ROULETTE — Can you beat this build? ⚔️\n\n"
        f"🗡️ Main Hand : {_named(lo, lo.main_hand, 'main', '')}\n"
        f"🛡️ Off-Hand  : {off}\n"
        f"🪖 Head      : {_named(lo, lo.head, 'head', '')}\n"
        f"🥋 Chest     : {_named(lo, lo.chest, 'chest', '')}\n"
        f"👢 Shoes     : {_named(lo, lo.shoes, 'shoes', '')}\n"
        f"🧣 Cape      : {_named(lo, lo.cape, 'cape', 'None')}\n\n"
        f"🔥 CHALLENGE : {_clean_challenge(lo.challenge)}\n\n"
        f"🎲 Generated by Albion Master — Support the Dev: {KOFI_URL}"
    )


# ---------------------------------------------------------------------------
# REROLL — single-slot re-randomization (keeps the rest of the build)
# ---------------------------------------------------------------------------
def reroll_slot(slot: str) -> None:
    """Re-roll one slot only — costs 1 Donation Credit (locked otherwise).

    Main-hand reroll re-evaluates the 2H/off-hand rule. Each gear reroll also
    re-rolls that slot's tier for maximum chaos.
    """
    lo: Loadout | None = st.session_state.get("loadout")
    if lo is None:
        return
    # Gatekeeper: no credits -> reroll is locked.
    if st.session_state.get("credits", 0) <= 0:
        return

    if slot == "main":
        lo.main_hand = _roll(MAIN_HANDS)
        lo.is_two_handed = lo.main_hand.two_handed
        lo.tiers["main"] = roll_tier()
        if lo.is_two_handed:
            lo.off_hand = None
        elif lo.off_hand is None:
            lo.off_hand = _roll(OFF_HANDS)
            lo.tiers["off"] = roll_tier()
    elif slot == "off":
        if lo.is_two_handed:
            return  # nothing to reroll; don't burn a credit
        lo.off_hand = _roll(OFF_HANDS)
        lo.tiers["off"] = roll_tier()
    elif slot == "head":
        lo.head = _roll(ARMOR_HEAD)
        lo.tiers["head"] = roll_tier()
    elif slot == "chest":
        lo.chest = _roll(ARMOR_CHEST)
        lo.tiers["chest"] = roll_tier()
    elif slot == "shoes":
        lo.shoes = _roll(ARMOR_SHOES)
        lo.tiers["shoes"] = roll_tier()
    elif slot == "cape":
        lo.cape = _roll(CAPES)
        lo.tiers["cape"] = roll_tier()
    elif slot == "challenge":
        lo.challenge = _weighted_choice(
            [c[0] for c in CHALLENGES], [c[1] for c in CHALLENGES]
        )

    st.session_state.credits = st.session_state.get("credits", 0) - 1
    st.session_state.rerolls = st.session_state.get("rerolls", 0) + 1


# ---------------------------------------------------------------------------
# STYLING (Task 3) — Obsidian-Dark, OBS-friendly
# ---------------------------------------------------------------------------
OBSIDIAN_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(900px 500px at 50% -10%, #1d2030 0%, rgba(10,11,14,0) 60%),
            linear-gradient(180deg, #0a0b0e 0%, #050507 100%);
        color: #e8eaf0;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 1.2rem;}

    /* ---- Header banner ---- */
    .am-banner {
        text-align: center;
        margin-bottom: 6px;
        padding: 14px 0 6px 0;
        border-bottom: 1px solid #2a2e3a;
    }
    .am-title {
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #f7e08c, #e8b04b 45%, #b9772a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 32px rgba(232,176,75,0.25);
        margin: 0;
    }
    .am-sub {
        text-align: center;
        color: #8b90a0;
        font-size: 1.0rem;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    /* ---- Item card (image over name) ---- */
    .am-card {
        position: relative;
        background: linear-gradient(160deg, #1a1d26 0%, #11131a 100%);
        border: 1px solid #2a2e3a;
        border-radius: 16px;
        padding: 14px 10px 12px 10px;
        margin-bottom: 12px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.45);
        min-height: 196px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }
    .am-tier-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        color: #0a0b0e;
        font-size: 0.72rem;
        font-weight: 900;
        letter-spacing: 0.5px;
        padding: 2px 8px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }
    .am-slot-label {
        color: #7d8295;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        margin-bottom: 6px;
    }
    .am-img {
        width: 92px;
        height: 92px;
        object-fit: contain;
        filter: drop-shadow(0 6px 10px rgba(0,0,0,0.5));
    }
    .am-img-empty {
        width: 92px; height: 92px;
        display: flex; align-items: center; justify-content: center;
        font-size: 2.4rem; color: #3a3e4a;
    }
    .am-item-name {
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 800;
        line-height: 1.15;
        margin-top: 8px;
    }
    .am-item-meta {
        color: #f5d76e;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 2px;
    }

    /* ---- Challenge box (high-contrast: gold border + red glow) ---- */
    .am-challenge {
        background: linear-gradient(160deg, #2e1710 0%, #170b0b 100%);
        border: 3px solid #e8b04b;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow:
            0 0 0 1px rgba(192,57,43,0.6),
            0 0 34px rgba(232,176,75,0.45),
            inset 0 0 24px rgba(192,57,43,0.25);
        margin-top: 6px;
        animation: am-pulse 2.4s ease-in-out infinite;
    }
    @keyframes am-pulse {
        0%, 100% { box-shadow: 0 0 0 1px rgba(192,57,43,0.6),
                               0 0 22px rgba(232,176,75,0.35),
                               inset 0 0 20px rgba(192,57,43,0.2); }
        50%      { box-shadow: 0 0 0 1px rgba(192,57,43,0.8),
                               0 0 40px rgba(232,176,75,0.6),
                               inset 0 0 26px rgba(192,57,43,0.3); }
    }
    .am-challenge-label {
        color: #f5d76e;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 1.0rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .am-challenge-text {
        color: #ffffff;
        font-size: 2.0rem;
        font-weight: 900;
        line-height: 1.25;
        text-shadow: 0 2px 12px rgba(0,0,0,0.6);
    }

    /* ---- Ad placeholder ---- */
    .am-ad {
        border: 1px dashed #3a3e4a;
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        color: #565b6a;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }

    /* ---- SPIN button (primary) ---- */
    div.stButton > button[kind="primary"] {
        width: 100%;
        background: linear-gradient(90deg, #f0bd57, #c98f2e);
        color: #1a1206;
        font-size: 1.9rem;
        font-weight: 900;
        letter-spacing: 4px;
        border: none;
        border-radius: 16px;
        padding: 20px 0;
        box-shadow: 0 8px 28px rgba(232,176,75,0.45);
        transition: transform 0.05s ease, box-shadow 0.2s ease, filter 0.2s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 12px 38px rgba(232,176,75,0.65);
        transform: translateY(-2px);
        filter: brightness(1.05);
        color: #1a1206;
    }
    div.stButton > button[kind="primary"]:active {transform: translateY(1px);}

    /* ---- Reroll buttons (secondary) ---- */
    div.stButton > button[kind="secondary"] {
        width: 100%;
        background: #20242e;
        color: #c9cee0;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: 1px solid #343a48;
        border-radius: 10px;
        padding: 4px 0;
        margin-top: -6px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: #2c3140;
        border-color: #e8b04b;
        color: #f5d76e;
    }

    /* ---- Ko-fi (high-visibility CTA) ---- */
    .am-kofi {
        display: block;
        text-align: center;
        margin: 6px auto 0 auto;
        max-width: 460px;
        white-space: nowrap;
        background: linear-gradient(90deg, #ff8a3d, #ff5e5b 50%, #d63d3a);
        color: #ffffff !important;
        font-size: 1.35rem;
        font-weight: 900;
        letter-spacing: 1px;
        text-decoration: none;
        padding: 16px 18px;
        border-radius: 14px;
        border: 2px solid rgba(255,255,255,0.18);
        box-shadow: 0 8px 26px rgba(214,61,58,0.5);
        animation: am-kofi-pulse 2s ease-in-out infinite;
        transition: transform 0.1s ease, filter 0.15s ease;
    }
    @keyframes am-kofi-pulse {
        0%, 100% { box-shadow: 0 8px 26px rgba(214,61,58,0.45); }
        50%      { box-shadow: 0 8px 36px rgba(255,138,61,0.7); }
    }
    .am-kofi:hover {filter: brightness(1.1); transform: translateY(-2px);}

    /* ---- Donation credit bar ---- */
    .am-credit-bar {
        text-align: center;
        background: linear-gradient(160deg, #161a22 0%, #10131a 100%);
        border: 1px solid #2a2e3a;
        border-left: 4px solid #6c5ce7;
        border-radius: 12px;
        padding: 10px 14px;
        margin-top: 8px;
        color: #c9cee0;
        font-size: 1.0rem;
    }
</style>
"""


def item_card(label: str, item: Item | None, tier: str = "T4",
              meta: str = "", placeholder: str = "🚫") -> str:
    """HTML card: image on top, name below. Broken images are hidden gracefully."""
    badge_html = ""
    if item is None or not item.item_id:
        visual = f'<div class="am-img-empty">{placeholder}</div>'
        name = item.name if item else "None"
    else:
        visual = (
            f'<img class="am-img" src="{item_image_url(item.item_id, tier)}" '
            f'alt="{item.name}" loading="lazy" '
            f"onerror=\"this.onerror=null;this.outerHTML='"
            f'<div class=&quot;am-img-empty&quot;>{placeholder}</div>'
            "';\">"
        )
        name = item.name
        color = TIER_COLORS.get(tier, "#9aa0b0")
        badge_html = (
            f'<div class="am-tier-badge" style="background:{color};">{tier}</div>'
        )
    meta_html = f'<div class="am-item-meta">{meta}</div>' if meta else ""
    return (
        '<div class="am-card">'
        f"{badge_html}"
        f'<div class="am-slot-label">{label}</div>'
        f"{visual}"
        f'<div class="am-item-name">{name}</div>'
        f"{meta_html}"
        "</div>"
    )


def render_slot(col, label: str, item: Item | None, slot_key: str,
                tier: str = "T4", meta: str = "", placeholder: str = "🚫",
                can_reroll: bool = True) -> None:
    """Render one inventory slot (image card + a credit-gated Reroll button)."""
    credits = st.session_state.get("credits", 0)
    unlocked = can_reroll and credits > 0
    label_txt = "🔄 Reroll (1)" if unlocked else "🔒 Locked"
    with col:
        st.markdown(item_card(label, item, tier, meta, placeholder),
                    unsafe_allow_html=True)
        st.button(
            label_txt,
            key=f"rr_{slot_key}",
            type="secondary",
            use_container_width=True,
            disabled=not unlocked,
            on_click=reroll_slot,
            args=(slot_key,),
        )


def copy_to_clipboard_button(text: str, label: str) -> None:
    """A real one-click copy button (uses the browser clipboard via JS)."""
    payload = json.dumps(text)  # safely escape for embedding in JS
    html = f"""
    <style>
      .am-copy-btn {{
        width: 100%;
        background: linear-gradient(90deg, #6c5ce7, #4834d4);
        color: #fff; border: none; border-radius: 12px;
        font-size: 1.15rem; font-weight: 800; letter-spacing: 0.5px;
        padding: 14px 0; cursor: pointer;
        box-shadow: 0 6px 20px rgba(72,52,212,0.4);
        font-family: "Source Sans Pro", sans-serif;
        transition: filter 0.15s ease;
      }}
      .am-copy-btn:hover {{ filter: brightness(1.1); }}
      .am-copy-btn.copied {{ background: linear-gradient(90deg, #00b894, #019a7c); }}
    </style>
    <button class="am-copy-btn" id="amCopy" onclick="amCopy()">{label}</button>
    <script>
      const amText = {payload};
      function amCopy() {{
        const btn = document.getElementById('amCopy');
        navigator.clipboard.writeText(amText).then(() => {{
          btn.classList.add('copied');
          btn.innerText = '✅ Copied! Paste it in Discord';
          setTimeout(() => {{
            btn.classList.remove('copied');
            btn.innerText = {json.dumps(label)};
          }}, 2200);
        }}).catch(() => {{ btn.innerText = '⚠️ Press Ctrl+C to copy'; }});
      }}
    </script>
    """
    components.html(html, height=64)


def spin_overlay_html(message: str) -> str:
    """A large, centered spinning roulette graphic shown during the SPIN delay.

    Cycles through real Albion weapon icons so the reveal feels like a slot
    machine. CSS keyframes animate client-side while Python sleeps server-side.
    """
    icons = ["2H_LONGBOW", "MAIN_FIRESTAFF", "2H_AXE", "MAIN_SWORD",
             "2H_CURSEDSTAFF", "MAIN_RAPIER_MORGANA", "2H_CROSSBOW", "MAIN_MACE"]
    tier = random.choice(TIERS)
    imgs = "".join(
        f'<img src="{item_image_url(i, tier)}" class="am-spin-icon" '
        f'style="animation-delay:{n * 0.28:.2f}s;">'
        for n, i in enumerate(icons)
    )
    return f"""
    <style>
      .am-spin-wrap {{
        text-align:center; padding: 18px 0 6px 0;
        font-family:"Source Sans Pro",sans-serif;
      }}
      .am-spin-ring {{
        position:relative; width:230px; height:230px; margin:0 auto;
        border-radius:50%;
        border:6px solid rgba(232,176,75,0.18);
        border-top-color:#e8b04b; border-right-color:#c0392b;
        animation: am-rot 0.9s linear infinite;
        box-shadow:0 0 50px rgba(232,176,75,0.45), inset 0 0 40px rgba(0,0,0,0.6);
        display:flex; align-items:center; justify-content:center;
        background: radial-gradient(circle at 50% 50%, #15171f 0%, #0a0b0e 70%);
      }}
      .am-spin-icons {{ position:absolute; width:118px; height:118px; }}
      .am-spin-icon {{
        position:absolute; top:0; left:0; width:118px; height:118px;
        object-fit:contain; opacity:0;
        animation: am-flash 2.24s linear infinite;
        filter: drop-shadow(0 6px 12px rgba(0,0,0,0.6));
      }}
      @keyframes am-rot {{ to {{ transform: rotate(360deg); }} }}
      @keyframes am-flash {{
        0%, 100% {{ opacity:0; transform:scale(0.7); }}
        6%       {{ opacity:1; transform:scale(1.05); }}
        12%      {{ opacity:0; transform:scale(0.7); }}
      }}
      .am-spin-text {{
        margin-top:18px; font-size:1.6rem; font-weight:900;
        letter-spacing:1px;
        background:linear-gradient(90deg,#f7e08c,#e8b04b,#c0392b);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        animation: am-pulse-text 1s ease-in-out infinite;
      }}
      @keyframes am-pulse-text {{ 50% {{ opacity:0.55; }} }}
    </style>
    <div class="am-spin-wrap">
      <div class="am-spin-ring"><div class="am-spin-icons">{imgs}</div></div>
      <div class="am-spin-text">{message}</div>
    </div>
    """


# ---------------------------------------------------------------------------
# DONATION CREDITS — gate the rerolls (Twitch / Ko-fi engagement loop)
# ---------------------------------------------------------------------------
def add_credit() -> None:
    st.session_state.credits = st.session_state.get("credits", 0) + 1


def reset_credits() -> None:
    st.session_state.credits = 0


def render_credit_panel() -> None:
    """Streamer-facing control: 1 viewer donation = +1 reroll credit."""
    credits = st.session_state.get("credits", 0)
    locked_note = (
        "🔒 Rerolls are LOCKED — viewers must donate to unlock them!"
        if credits <= 0
        else f"🔓 {credits} reroll(s) unlocked — spend them wisely!"
    )
    st.markdown(
        f'<div class="am-credit-bar">🎟️ Reroll Credits: '
        f"<b>{credits}</b> &nbsp;·&nbsp; {locked_note}</div>",
        unsafe_allow_html=True,
    )
    with st.expander("🎬 Streamer Control Panel (click each donation)", expanded=False):
        st.caption(
            "Keep rerolls fair on stream: each time a viewer donates (Twitch "
            "bits / Ko-fi / channel points), click **+1 Credit**. Each credit "
            "lets you reroll exactly ONE slot. No credits = play the build as-is!"
        )
        c1, c2 = st.columns(2)
        with c1:
            st.button("➕  +1 Credit (donation received!)",
                      key="add_credit_btn", use_container_width=True,
                      on_click=add_credit)
        with c2:
            st.button("🔁  Reset credits to 0",
                      key="reset_credit_btn", use_container_width=True,
                      on_click=reset_credits)


# ---------------------------------------------------------------------------
# APP BODY
# ---------------------------------------------------------------------------
def main() -> None:
    st.markdown(OBSIDIAN_CSS, unsafe_allow_html=True)

    st.markdown(
        '<div class="am-banner">'
        '<div class="am-title">⚔️ ALBION ROULETTE ⚔️</div>'
        '<div class="am-sub">Streamer Build Roulette &amp; Challenge Generator</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    if "loadout" not in st.session_state:
        st.session_state.loadout = None
    if "spins" not in st.session_state:
        st.session_state.spins = 0
    if "credits" not in st.session_state:
        st.session_state.credits = 0

    # ---- SPIN with big center spinning animation ----
    spin_clicked = st.button("🎰  SPIN THE BUILD", key="spin_btn", type="primary",
                             use_container_width=True)
    if spin_clicked:
        overlay = st.empty()
        overlay.markdown(spin_overlay_html(random.choice(RNG_LINES)),
                         unsafe_allow_html=True)
        time.sleep(SPIN_DELAY)
        overlay.empty()
        st.session_state.loadout = spin()
        st.session_state.spins += 1

    # ---- Streamer Control Panel: Donation Credits gate the rerolls ----
    render_credit_panel()

    st.markdown("<br>", unsafe_allow_html=True)
    loadout: Loadout | None = st.session_state.loadout

    if loadout is None:
        st.markdown(
            '<div class="am-card" style="min-height:160px;justify-content:center;">'
            '<div class="am-item-name" style="font-size:1.4rem;">'
            "Press SPIN to roll your fate 🎲</div>"
            '<div class="am-slot-label" style="margin-top:10px;">'
            "Window-capture this in OBS for your stream</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        off_meta = "Two-Handed" if loadout.is_two_handed else ""
        hand_meta = f"{loadout.main_hand.archetype} · " + (
            "2H" if loadout.is_two_handed else "1H"
        )

        t = loadout.tiers
        # ---- Inventory-style cross layout (mimics the in-game paper-doll) ----
        # Top row: Head (centered)
        _, top_mid, _ = st.columns([1, 1, 1])
        render_slot(top_mid, "Head", loadout.head, "head", tier=t.get("head", "T4"))

        # Middle row: Main Hand | Chest | Off-Hand | Cape
        m1, m2, m3, m4 = st.columns(4)
        render_slot(m1, "Main Hand", loadout.main_hand, "main",
                    tier=t.get("main", "T4"), meta=hand_meta)
        render_slot(m2, "Chest", loadout.chest, "chest", tier=t.get("chest", "T4"))
        render_slot(
            m3, "Off-Hand", loadout.off_hand, "off",
            tier=t.get("off", "T4"), meta=off_meta, placeholder="✋",
            can_reroll=not loadout.is_two_handed,
        )
        render_slot(m4, "Cape", loadout.cape, "cape",
                    tier=t.get("cape", "T4"), placeholder="🧣")

        # Bottom row: Shoes (centered)
        _, bot_mid, _ = st.columns([1, 1, 1])
        render_slot(bot_mid, "Shoes", loadout.shoes, "shoes", tier=t.get("shoes", "T4"))

        # Challenge hook (reroll is also credit-gated)
        st.markdown(
            '<div class="am-challenge">'
            '<div class="am-challenge-label">🔥 The Content Hook</div>'
            f'<div class="am-challenge-text">{loadout.challenge}</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        ch_unlocked = st.session_state.get("credits", 0) > 0
        cc1, cc2, cc3 = st.columns([1, 1, 1])
        with cc2:
            st.button(
                "🔄 Reroll Challenge (1)" if ch_unlocked else "🔒 Locked",
                key="rr_challenge",
                type="secondary",
                use_container_width=True,
                disabled=not ch_unlocked,
                on_click=reroll_slot,
                args=("challenge",),
            )

        st.markdown(
            '<div class="am-sub" style="margin-top:12px;">'
            f"Spins: <b>{st.session_state.spins}</b> &nbsp;|&nbsp; "
            f"Rerolls: <b>{st.session_state.get('rerolls', 0)}</b> &nbsp;|&nbsp; "
            f"Credits: <b>{st.session_state.get('credits', 0)}</b></div>",
            unsafe_allow_html=True,
        )

        # ---- Viral Export: one-click copy with Ko-fi promo ----
        st.markdown("<br>", unsafe_allow_html=True)
        copy_to_clipboard_button(
            loadout_to_share(loadout), "📋 Copy Build to Clipboard (challenge a friend!)"
        )

        # AI-friendly plain-text export (for Gemini / ChatGPT)
        with st.expander("🤖 Export for AI (Gemini / ChatGPT)", expanded=False):
            st.caption("Plain text — AI reads this far better than a screenshot.")
            st.code(loadout_to_text(loadout), language="text")

    # ---- Monetization (Task 4) ----
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<a class="am-kofi" href="{KOFI_URL}" target="_blank" rel="noopener">'
        "☕ Support the Chaos</a>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="am-ad">[ Google AdSense Placeholder ]<br>'
        f"client: {ADSENSE_CLIENT} &nbsp;|&nbsp; slot: responsive banner</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
