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
RENDER_TIER = "T4"                                        # tier used for art
RENDER_SIZE = 180                                         # px image size
SPIN_DELAY = 2.4                                          # suspense seconds

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


def item_image_url(item_id: str) -> str:
    """Build the Albion Render API URL for a given internal item id."""
    return (
        f"https://render.albiononline.com/v1/item/{item_id}.png"
        f"?size={RENDER_SIZE}&quality=1"
    )


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
    Weapon("Broadsword", f"{RENDER_TIER}_MAIN_SWORD", 12, "Sword"),
    Weapon("Dagger", f"{RENDER_TIER}_MAIN_DAGGER", 9, "Dagger"),
    Weapon("Bloodletter", f"{RENDER_TIER}_MAIN_RAPIER_MORGANA", 10, "Dagger"),
    Weapon("Spear", f"{RENDER_TIER}_MAIN_SPEAR", 8, "Spear"),
    Weapon("Nature Staff", f"{RENDER_TIER}_MAIN_NATURESTAFF", 8, "Nature Staff"),
    Weapon("Druidic Staff", f"{RENDER_TIER}_MAIN_NATURESTAFF_KEEPER", 7, "Nature Staff"),
    Weapon("Holy Staff", f"{RENDER_TIER}_MAIN_HOLYSTAFF", 8, "Holy Staff"),
    Weapon("Fire Staff", f"{RENDER_TIER}_MAIN_FIRESTAFF", 9, "Fire Staff"),
    Weapon("Frost Staff", f"{RENDER_TIER}_MAIN_FROSTSTAFF", 8, "Frost Staff"),
    Weapon("Cursed Staff", f"{RENDER_TIER}_MAIN_CURSEDSTAFF", 9, "Cursed Staff"),
    Weapon("Arcane Staff", f"{RENDER_TIER}_MAIN_ARCANESTAFF", 7, "Arcane Staff"),
    Weapon("Mace", f"{RENDER_TIER}_MAIN_MACE", 8, "Mace"),
    Weapon("Hammer", f"{RENDER_TIER}_MAIN_HAMMER", 6, "Hammer"),
    Weapon("Battleaxe", f"{RENDER_TIER}_MAIN_AXE", 10, "Axe"),
    # Two-handed (off-hand removed)
    Weapon("Longbow", f"{RENDER_TIER}_2H_LONGBOW", 11, "Bow", two_handed=True),
    Weapon("Bow", f"{RENDER_TIER}_2H_BOW", 9, "Bow", two_handed=True),
    Weapon("Bow of Badon", f"{RENDER_TIER}_2H_BOW_KEEPER", 7, "Bow", two_handed=True),
    Weapon("Greataxe", f"{RENDER_TIER}_2H_AXE", 9, "Axe", two_handed=True),
    Weapon("Realmbreaker", f"{RENDER_TIER}_2H_AXE_AVALON", 6, "Axe", two_handed=True),
    Weapon("Halberd", f"{RENDER_TIER}_2H_HALBERD", 7, "Spear", two_handed=True),
    Weapon("Pike", f"{RENDER_TIER}_2H_SPEAR", 6, "Spear", two_handed=True),
    Weapon("Claws", f"{RENDER_TIER}_2H_CLAWPAIR", 6, "Dagger", two_handed=True),
    Weapon("Claymore", f"{RENDER_TIER}_2H_CLAYMORE", 9, "Sword", two_handed=True),
    Weapon("Dual Swords", f"{RENDER_TIER}_2H_DUALSWORD", 8, "Sword", two_handed=True),
    Weapon("Great Fire Staff", f"{RENDER_TIER}_2H_FIRESTAFF", 8, "Fire Staff", two_handed=True),
    Weapon("Infernal Staff", f"{RENDER_TIER}_2H_INFERNOSTAFF", 6, "Fire Staff", two_handed=True),
    Weapon("Great Frost Staff", f"{RENDER_TIER}_2H_FROSTSTAFF", 7, "Frost Staff", two_handed=True),
    Weapon("Great Cursed Staff", f"{RENDER_TIER}_2H_CURSEDSTAFF", 7, "Cursed Staff", two_handed=True),
    Weapon("Great Nature Staff", f"{RENDER_TIER}_2H_NATURESTAFF", 7, "Nature Staff", two_handed=True),
    Weapon("Great Arcane Staff", f"{RENDER_TIER}_2H_ARCANESTAFF", 6, "Arcane Staff", two_handed=True),
    Weapon("Crossbow", f"{RENDER_TIER}_2H_CROSSBOW", 8, "Crossbow", two_handed=True),
]

# --- Off-hands -------------------------------------------------------------
OFF_HANDS: list[Item] = [
    Item("Shield", f"{RENDER_TIER}_OFF_SHIELD", 13),
    Item("Tome of Spells", f"{RENDER_TIER}_OFF_BOOK", 10),
    Item("Torch", f"{RENDER_TIER}_OFF_TORCH", 10),
    Item("Eye of Secrets", f"{RENDER_TIER}_OFF_ORB_MORGANA", 8),
    Item("Muisak", f"{RENDER_TIER}_OFF_DEMONSKULL_HELL", 7),
    Item("Taproot", f"{RENDER_TIER}_OFF_TOTEM_KEEPER", 6),
    Item("Mistcaller", f"{RENDER_TIER}_OFF_HORN_KEEPER", 5),
]

# --- Armor (Cloth / Leather / Plate -> SET1/SET2/SET3) ---------------------
ARMOR_HEAD: list[Item] = [
    Item("Scholar Cowl (Cloth)", f"{RENDER_TIER}_HEAD_CLOTH_SET1", 12),
    Item("Cleric Cowl (Cloth)", f"{RENDER_TIER}_HEAD_CLOTH_SET2", 8),
    Item("Mage Cowl (Cloth)", f"{RENDER_TIER}_HEAD_CLOTH_SET3", 7),
    Item("Mercenary Hood (Leather)", f"{RENDER_TIER}_HEAD_LEATHER_SET1", 12),
    Item("Hunter Hood (Leather)", f"{RENDER_TIER}_HEAD_LEATHER_SET2", 10),
    Item("Assassin Hood (Leather)", f"{RENDER_TIER}_HEAD_LEATHER_SET3", 8),
    Item("Soldier Helmet (Plate)", f"{RENDER_TIER}_HEAD_PLATE_SET1", 12),
    Item("Knight Helmet (Plate)", f"{RENDER_TIER}_HEAD_PLATE_SET2", 10),
    Item("Guardian Helmet (Plate)", f"{RENDER_TIER}_HEAD_PLATE_SET3", 8),
]

ARMOR_CHEST: list[Item] = [
    Item("Scholar Robe (Cloth)", f"{RENDER_TIER}_ARMOR_CLOTH_SET1", 12),
    Item("Cleric Robe (Cloth)", f"{RENDER_TIER}_ARMOR_CLOTH_SET2", 8),
    Item("Mage Robe (Cloth)", f"{RENDER_TIER}_ARMOR_CLOTH_SET3", 7),
    Item("Mercenary Jacket (Leather)", f"{RENDER_TIER}_ARMOR_LEATHER_SET1", 12),
    Item("Hunter Jacket (Leather)", f"{RENDER_TIER}_ARMOR_LEATHER_SET2", 10),
    Item("Assassin Jacket (Leather)", f"{RENDER_TIER}_ARMOR_LEATHER_SET3", 8),
    Item("Soldier Armor (Plate)", f"{RENDER_TIER}_ARMOR_PLATE_SET1", 12),
    Item("Knight Armor (Plate)", f"{RENDER_TIER}_ARMOR_PLATE_SET2", 10),
    Item("Guardian Armor (Plate)", f"{RENDER_TIER}_ARMOR_PLATE_SET3", 8),
]

ARMOR_SHOES: list[Item] = [
    Item("Scholar Sandals (Cloth)", f"{RENDER_TIER}_SHOES_CLOTH_SET1", 12),
    Item("Cleric Sandals (Cloth)", f"{RENDER_TIER}_SHOES_CLOTH_SET2", 8),
    Item("Mage Sandals (Cloth)", f"{RENDER_TIER}_SHOES_CLOTH_SET3", 7),
    Item("Mercenary Shoes (Leather)", f"{RENDER_TIER}_SHOES_LEATHER_SET1", 12),
    Item("Hunter Shoes (Leather)", f"{RENDER_TIER}_SHOES_LEATHER_SET2", 10),
    Item("Assassin Shoes (Leather)", f"{RENDER_TIER}_SHOES_LEATHER_SET3", 8),
    Item("Soldier Boots (Plate)", f"{RENDER_TIER}_SHOES_PLATE_SET1", 12),
    Item("Knight Boots (Plate)", f"{RENDER_TIER}_SHOES_PLATE_SET2", 10),
    Item("Guardian Boots (Plate)", f"{RENDER_TIER}_SHOES_PLATE_SET3", 8),
]

# --- Capes -----------------------------------------------------------------
CAPES: list[Item] = [
    Item("No Cape", "", 6),
    Item("Thetford Cape", f"{RENDER_TIER}_CAPEITEM_FW_THETFORD", 10),
    Item("Fort Sterling Cape", f"{RENDER_TIER}_CAPEITEM_FW_FORTSTERLING", 10),
    Item("Lymhurst Cape", f"{RENDER_TIER}_CAPEITEM_FW_LYMHURST", 10),
    Item("Bridgewatch Cape", f"{RENDER_TIER}_CAPEITEM_FW_BRIDGEWATCH", 10),
    Item("Martlock Cape", f"{RENDER_TIER}_CAPEITEM_FW_MARTLOCK", 10),
    Item("Caerleon Cape", f"{RENDER_TIER}_CAPEITEM_FW_CAERLEON", 8),
    Item("Heretic Cape", f"{RENDER_TIER}_CAPEITEM_HERETIC", 7),
    Item("Undead Cape", f"{RENDER_TIER}_CAPEITEM_UNDEAD", 7),
    Item("Keeper Cape", f"{RENDER_TIER}_CAPEITEM_KEEPER", 7),
    Item("Morgana Cape", f"{RENDER_TIER}_CAPEITEM_MORGANA", 7),
    Item("Demon Cape", f"{RENDER_TIER}_CAPEITEM_DEMON", 6),
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
    is_two_handed: bool = field(init=False)

    def __post_init__(self) -> None:
        self.is_two_handed = self.main_hand.two_handed


def spin() -> Loadout:
    """Roll a complete loadout. Enforces 2H weapon -> no off-hand."""
    main = _roll(MAIN_HANDS)
    off_hand = None if main.two_handed else _roll(OFF_HANDS)
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
    )


def _clean_challenge(challenge: str) -> str:
    if " " in challenge and not challenge[0].isalnum():
        return challenge.split(" ", 1)[1]
    return challenge


def loadout_to_text(lo: Loadout) -> str:
    """Plain-text summary — paste into Gemini / ChatGPT for reliable reading."""
    hand_type = "Two-Handed" if lo.is_two_handed else "One-Handed"
    off = lo.off_hand.name if lo.off_hand else "None (Two-Handed)"
    return (
        "ALBION ONLINE - RANDOM BUILD\n"
        "============================\n"
        f"Main Hand : {lo.main_hand.name} ({lo.main_hand.archetype}, {hand_type})\n"
        f"Off-Hand  : {off}\n"
        f"Head      : {lo.head.name}\n"
        f"Chest     : {lo.chest.name}\n"
        f"Shoes     : {lo.shoes.name}\n"
        f"Cape      : {lo.cape.name}\n"
        f"Challenge : {_clean_challenge(lo.challenge)}\n"
        "============================\n"
        "Question for AI: Is this build viable? Suggest spec, food, and playstyle."
    )


def loadout_to_share(lo: Loadout) -> str:
    """Viral share text — pretty, with challenge + Ko-fi promo footer."""
    off = lo.off_hand.name if lo.off_hand else "None (2H weapon)"
    return (
        "⚔️ ALBION ROULETTE — Can you beat this build? ⚔️\n\n"
        f"🗡️ Main Hand : {lo.main_hand.name}\n"
        f"🛡️ Off-Hand  : {off}\n"
        f"🪖 Head      : {lo.head.name}\n"
        f"🥋 Chest     : {lo.chest.name}\n"
        f"👢 Shoes     : {lo.shoes.name}\n"
        f"🧣 Cape      : {lo.cape.name}\n\n"
        f"🔥 CHALLENGE : {_clean_challenge(lo.challenge)}\n\n"
        f"🎲 Generated by Albion Master — Support the Dev: {KOFI_URL}"
    )


# ---------------------------------------------------------------------------
# REROLL — single-slot re-randomization (keeps the rest of the build)
# ---------------------------------------------------------------------------
def reroll_slot(slot: str) -> None:
    """Re-roll one slot only. Main-hand reroll re-evaluates 2H/off-hand rule."""
    lo: Loadout | None = st.session_state.get("loadout")
    if lo is None:
        return
    if slot == "main":
        lo.main_hand = _roll(MAIN_HANDS)
        lo.is_two_handed = lo.main_hand.two_handed
        if lo.is_two_handed:
            lo.off_hand = None
        elif lo.off_hand is None:
            lo.off_hand = _roll(OFF_HANDS)
    elif slot == "off":
        if not lo.is_two_handed:
            lo.off_hand = _roll(OFF_HANDS)
    elif slot == "head":
        lo.head = _roll(ARMOR_HEAD)
    elif slot == "chest":
        lo.chest = _roll(ARMOR_CHEST)
    elif slot == "shoes":
        lo.shoes = _roll(ARMOR_SHOES)
    elif slot == "cape":
        lo.cape = _roll(CAPES)
    elif slot == "challenge":
        lo.challenge = _weighted_choice(
            [c[0] for c in CHALLENGES], [c[1] for c in CHALLENGES]
        )
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

    /* ---- Challenge box ---- */
    .am-challenge {
        background: linear-gradient(160deg, #2a1414 0%, #170b0b 100%);
        border: 2px solid #c0392b;
        border-radius: 16px;
        padding: 22px;
        text-align: center;
        box-shadow: 0 0 26px rgba(192,57,43,0.35);
        margin-top: 6px;
    }
    .am-challenge-label {
        color: #ff7b72;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.95rem;
        margin-bottom: 8px;
    }
    .am-challenge-text {
        color: #ffffff;
        font-size: 1.9rem;
        font-weight: 800;
        line-height: 1.25;
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

    /* ---- Ko-fi ---- */
    .am-kofi {
        display: block;
        text-align: center;
        margin: 6px auto 0 auto;
        max-width: 440px;
        white-space: nowrap;
        background: linear-gradient(90deg, #ff5e5b, #d63d3a);
        color: #ffffff !important;
        font-size: 1.2rem;
        font-weight: 800;
        text-decoration: none;
        padding: 14px 18px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(214,61,58,0.4);
    }
    .am-kofi:hover {filter: brightness(1.08);}
</style>
"""


def item_card(label: str, item: Item | None, meta: str = "", placeholder: str = "🚫") -> str:
    """HTML card: image on top, name below. Broken images are hidden gracefully."""
    if item is None or not item.item_id:
        visual = f'<div class="am-img-empty">{placeholder}</div>'
        name = item.name if item else "None"
    else:
        visual = (
            f'<img class="am-img" src="{item_image_url(item.item_id)}" '
            f'alt="{item.name}" loading="lazy" '
            f"onerror=\"this.onerror=null;this.outerHTML='"
            f'<div class=&quot;am-img-empty&quot;>{placeholder}</div>'
            "';\">"
        )
        name = item.name
    meta_html = f'<div class="am-item-meta">{meta}</div>' if meta else ""
    return (
        '<div class="am-card">'
        f'<div class="am-slot-label">{label}</div>'
        f"{visual}"
        f'<div class="am-item-name">{name}</div>'
        f"{meta_html}"
        "</div>"
    )


def render_slot(col, label: str, item: Item | None, slot_key: str,
                meta: str = "", placeholder: str = "🚫",
                can_reroll: bool = True) -> None:
    """Render one inventory slot (image card + a small Reroll button)."""
    with col:
        st.markdown(item_card(label, item, meta, placeholder), unsafe_allow_html=True)
        st.button(
            "🔄 Reroll",
            key=f"rr_{slot_key}",
            type="secondary",
            use_container_width=True,
            disabled=not can_reroll,
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

    # ---- SPIN (Suspense Animation) ----
    if st.button("🎰  SPIN THE BUILD", key="spin_btn", type="primary",
                 use_container_width=True):
        with st.spinner(random.choice(RNG_LINES)):
            time.sleep(SPIN_DELAY)
        st.session_state.loadout = spin()
        st.session_state.spins += 1

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

        # ---- Inventory-style cross layout (mimics the in-game paper-doll) ----
        # Top row: Head (centered)
        _, top_mid, _ = st.columns([1, 1, 1])
        render_slot(top_mid, "Head", loadout.head, "head")

        # Middle row: Main Hand | Chest | Off-Hand | Cape
        m1, m2, m3, m4 = st.columns(4)
        render_slot(m1, "Main Hand", loadout.main_hand, "main", meta=hand_meta)
        render_slot(m2, "Chest", loadout.chest, "chest")
        render_slot(
            m3, "Off-Hand", loadout.off_hand, "off",
            meta=off_meta, placeholder="✋",
            can_reroll=not loadout.is_two_handed,
        )
        render_slot(m4, "Cape", loadout.cape, "cape", placeholder="🧣")

        # Bottom row: Shoes (centered)
        _, bot_mid, _ = st.columns([1, 1, 1])
        render_slot(bot_mid, "Shoes", loadout.shoes, "shoes")

        # Challenge hook (with its own reroll)
        st.markdown(
            '<div class="am-challenge">'
            '<div class="am-challenge-label">🔥 The Content Hook</div>'
            f'<div class="am-challenge-text">{loadout.challenge}</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        cc1, cc2, cc3 = st.columns([1, 1, 1])
        with cc2:
            st.button(
                "🔄 Reroll Challenge",
                key="rr_challenge",
                type="secondary",
                use_container_width=True,
                on_click=reroll_slot,
                args=("challenge",),
            )

        st.markdown(
            '<div class="am-sub" style="margin-top:12px;">'
            f"Spins: <b>{st.session_state.spins}</b> &nbsp;|&nbsp; "
            f"Rerolls: <b>{st.session_state.get('rerolls', 0)}</b></div>",
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
        "☕ Support the Dev: Buy me a coffee (Ko-fi)</a>",
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
