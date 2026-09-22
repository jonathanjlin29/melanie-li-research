#!/usr/bin/env python3
"""Regenerate data.json for the Melanie Li research dashboard.

Pulls fresh follower counts for Melanie and the creator watchlist via
instagram-cli, keeps the curated formats/ideas, and stamps updated_at.
Weekly trend items are appended by the refresh job (see README).
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

ACCOUNT_ID = "17841401529160627"
DIR = "/home/hatch/workspace/melanie-li-research"

WATCHLIST = [
    # (username, display name, niche, relevance note)
    ("thestevenhe", "Steven He", "Asian-dad comedy skits",
     "Master of the two-role parent-comparison skit; the format to study for scripted bits."),
    ("jimmyoyang", "Jimmy O. Yang", "HK-born stand-up",
     "Cantonese-cussing bit is his most clipped segment; proof language humor travels."),
    ("jlouofficial", "J Lou", "Multilingual-mom persona skits",
     "Persona-switching (sweet English mom vs. scary Cantonese mom) — template for grandma/granddaughter two-character energy."),
    ("iammcjin", "MC Jin", "Rapper / Cantonese storytelling",
     "'My first Cantonese verse' storytelling maps directly to dish-origin stories."),
    ("esafung", "Esa Fung", "ABC parent comedy",
     "ABC-coded family humor; closest comedic tone reference."),
    ("andrew.buoy", "Andrew Buoy", "Cantonese learning journey (SF)",
     "Closest overall match: SF-based, learning Cantonese on camera, films with his grandma, serialized journey format."),
    ("cantotomando", "CantotoMando", "Canto household comedy",
     "'Phrases Canto Moms Say' listicle series; 'Things my Toisan grandma says while I cook' is the untapped variant."),
    ("davidbfung", "David Fung", "Fung Bros / ABC in Asia",
     "Long-form ABC identity content; audience overlap."),
    ("matthewpwj_", "Matthew", "'Jayden' mum-mock trend",
     "Mixed English-Cantonese mum talk trend; millions of views, brands trendjacked it."),
]

FORMATS = [
    {"name": "Language-gap quiz",
     "description": "Contestants translate everyday phrases into Cantonese and fail entertainingly. A*Pop's 'Can These Chinese Americans Pass A Basic Cantonese Language Quiz?' runs multi-million views across rounds.",
     "example_label": "A*Pop Cantonese quiz (45K likes)",
     "example_url": "https://www.instagram.com/reel/DTTVmJbEg-u/"},
    {"name": "Parent-comparison two-role skit",
     "description": "One actor plays both the overbearing Asian parent and the American-raised kid. Steven He's 'How your parents COMPARE you to your cousin' hit ~310K likes.",
     "example_label": "Steven He cousin-comparison skit",
     "example_url": "https://www.instagram.com/reel/DYDGyewkna3/"},
    {"name": "Recurring character",
     "description": "A signature persona fans quote back. Jake Sing Chan's 'Ni Howdy' (exaggerated American vs. CNY red-envelope exchange) became a catchphrase engine.",
     "example_label": "'Ni Howdy' CNY skit (76K likes)",
     "example_url": "https://www.instagram.com/reel/DU3kl6tkfwT/"},
    {"name": "'Phrases Canto moms say' series",
     "description": "Serialized listicles of mom-isms. Each entry is a shareable clip and comment bait ('my mom says this too').",
     "example_label": "CantotoMando 'Signs you grew up in a Canto Household'",
     "example_url": "https://www.instagram.com/reel/DbqYs6Iz71-/"},
    {"name": "'Cantonese card revoked'",
     "description": "Attempt the entire video in Cantonese and fail, with mom roasting off-camera. Relatable incompetence + family comedy.",
     "example_label": "Eric Ou 'ABC son gets his Cantonese card revoked'",
     "example_url": "https://www.instagram.com/reel/Db9X_DCJpqc/"},
    {"name": "Day-N learning journey",
     "description": "Serialized progress vlogs ('Day 152 of practicing Cantonese'). Builds returning viewers; stakes rise with the count.",
     "example_label": "Andrew Buoy 'Cantonese & Toisan school for ABCs'",
     "example_url": "https://www.instagram.com/reel/DbG3WZQP8Ko/"},
    {"name": "Mixed English-Cantonese mum mock",
     "description": "Mocking how mums awkwardly force English words into Cantonese sentences ('Jayden, 媽咪 told you 呀, too much 啦'). Went mega-viral in HK; brands trendjacked it.",
     "example_label": "Marketing-Interactive: the 'Jayden' trend",
     "example_url": "https://www.marketing-interactive.com/hk-brands-trendjack-jayden-reels-mocking-mixed-english-cantonese-mum-talk"},
    {"name": "Multilingual persona switch",
     "description": "One creator, multiple parenting personas toggled by language. J Lou's sweet-English-mom to scary-Cantonese-mom switch is the template.",
     "example_label": "J Lou multilingual mom skit",
     "example_url": "https://www.instagram.com/reel/DcN-kQWC5gm/"},
]

IDEAS = [
    {"title": "Can my husband pass a Cantonese food vocab quiz?",
     "hook": "Have him translate zongzi ingredients and dim sum names on camera. The fails are the content.",
     "why": "Lifts the proven A*Pop quiz format into her husband-wife comedy lane."},
    {"title": "Things my Toisan grandma says while I cook",
     "hook": "Serialized listicle; each entry a shareable clip. Comment bait: 'my grandma says this too.'",
     "why": "CantotoMando's 'Phrases Canto Moms Say' format, but the Toisan-grandma variant is untapped."},
    {"title": "Day N of learning grandma's recipes before they're gone",
     "hook": "Serialized journey with emotional stakes; recipe-preservation content gets saved and shared hard.",
     "why": "Andrew Buoy's journey format with higher emotional stakes."},
    {"title": "Your grandma was doing wellness before it was cool",
     "hook": "Cantonese soups reframed as the original gut-health / depuff trend, with a wink at the wellness girlies.",
     "why": "Her winter-melon 'depuffing since age 3' post is already the hook; trend-hijack angle."},
    {"title": "Rating my grandma's reaction to my cooking",
     "hook": "Reaction format: grandma is the star, Melanie is the straight man.",
     "why": "Family-reaction videos travel; grandma content is already her audience's favorite."},
]


def ig_profile(username: str) -> dict | None:
    try:
        out = subprocess.run(
            ["instagram-cli", "profile", "--account-id", ACCOUNT_ID,
             "--username", username],
            capture_output=True, text=True, timeout=60)
        data = json.loads(out.stdout)
        profiles = data.get("profiles") or []
        return profiles[0] if profiles else None
    except Exception:
        return None


def main() -> None:
    try:
        with open(f"{DIR}/data.json", encoding="utf-8") as f:
            prev = json.load(f)
    except Exception:
        prev = {}

    mel = ig_profile("melanie_li") or {}
    melanie = {
        "username": "melanie_li",
        "name": mel.get("name") or "Melanie Li",
        "followers": mel.get("follower_count"),
        "following": mel.get("following_count"),
        "posts": mel.get("post_count"),
        "bio": (mel.get("bio") or "").strip(),
        "profile_url": "https://www.instagram.com/melanie_li",
    }

    creators = []
    for username, name, niche, relevance in WATCHLIST:
        p = ig_profile(username) or {}
        creators.append({
            "username": username,
            "name": p.get("name") or name,
            "followers": p.get("follower_count"),
            "verified": p.get("is_verified"),
            "niche": niche,
            "relevance": relevance,
            "profile_url": f"https://www.instagram.com/{username}",
        })

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "melanie": melanie,
        "creators": creators,
        "formats": FORMATS,
        "ideas": IDEAS,
        # Weekly trend notes, newest first. The refresh job prepends new entries.
        "trends": prev.get("trends", [
            {"date": "2026-09-22",
             "items": [
                 {"label": "'Jayden' mixed English-Cantonese mum trend goes mega-viral in HK; brands trendjack it",
                  "url": "https://www.marketing-interactive.com/hk-brands-trendjack-jayden-reels-mocking-mixed-english-cantonese-mum-talk",
                  "note": "Matthew (@matthewpwj_) + Janice (@janicewanwan) reels mocking mums who force English into Cantonese sentences. Millions of views."},
                 {"label": "Steven He 'parents compare you to your cousin' skit (~310K likes)",
                  "url": "https://www.instagram.com/reel/DYDGyewkna3/",
                  "note": "Two-role parent-comparison format still dominating."},
                 {"label": "Jimmy O. Yang Cantonese-cussing stand-up clip circulating",
                  "url": "https://www.instagram.com/reel/DYnyNWrJ61a/",
                  "note": "Language-humor proof point: 'Cantonese is the most fun language to cuss in.'"},
             ]},
        ]),
    }
    with open(f"{DIR}/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"wrote data.json at {data['updated_at']}")


if __name__ == "__main__":
    main()
