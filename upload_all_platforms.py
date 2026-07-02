"""
Lingexa Across - British vs American English Upload Script
"""

import os, sys, json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
upload_dir = Path(__file__).parent / "upload"
if upload_dir.exists() and str(upload_dir) not in sys.path:
    sys.path.insert(0, str(upload_dir))

upload_to_facebook = None
upload_to_instagram = None
upload_to_youtube = None
try:
    from upload_facebook import upload_to_facebook as fb_upload; upload_to_facebook = fb_upload
except ImportError: pass
try:
    from upload_instagram import upload_to_instagram as ig_upload; upload_to_instagram = ig_upload
except ImportError: pass
try:
    from upload_to_youtube import upload_to_youtube as yt_upload; upload_to_youtube = yt_upload
except ImportError: pass

CHANNEL_NAME = "Lingexa Across"

def get_latest_reel():
    video_dir = Path("output/video")
    if not video_dir.exists():
        return None
    reels = list(video_dir.glob("*/final_reel.mp4"))
    if not reels:
        return None
    latest = max(reels, key=lambda p: p.stat().st_mtime)
    metadata_file = latest.parent / "metadata.json"
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    pairs_data = metadata.get("pairs", [])
    return {"video_path": str(latest), "metadata": metadata, "pairs": pairs_data, "word": pairs_data[0].get("british", "UK") if pairs_data else "UK"}

def generate_caption(reel_data, platform="facebook"):
    pairs = reel_data.get("pairs", [])
    if not pairs:
        return f"British vs American English with {CHANNEL_NAME}! #LingexaAcross #BritishVsAmerican"
    if platform == "facebook":
        lines = [f"🇬🇧 British vs 🇺🇸 American: 3 Word Differences!", f""]
        for i, p in enumerate(pairs, 1):
            brit = p.get("british", "")
            us = p.get("american", "")
            definition = p.get("definition", "")
            brit_ex = p.get("british_example", "")
            us_ex = p.get("american_example", "")
            lines.append(f"{i}. {brit.upper()} vs {us.upper()}")
            lines.append(f"   → {definition}")
            lines.append(f"   🇬🇧 {brit_ex}")
            lines.append(f"   🇺🇸 {us_ex}")
            lines.append(f"")
        lines.extend([f"💡 Save this to remember the difference!", f"🔔 Follow {CHANNEL_NAME} for daily UK vs US words!", f"", f"#LingexaAcross #BritishVsAmerican #UKvsUS #English #LearnEnglish #BritishEnglish #AmericanEnglish #LanguageLearning #ESL"])
    else:
        lines = [f"🇬🇧 vs 🇺🇸 British vs American words today!", f""]
        for i, p in enumerate(pairs[:3], 1):
            lines.append(f"{i}. {p['british']} / {p['american']}")
        lines.extend([f"", f"#LingexaAcross #BritishVsAmerican #English"])
    return "\n".join(lines)

def main():
    reel = get_latest_reel()
    if not reel:
        print("No reel found!")
        sys.exit(1)
    caption = generate_caption(reel, platform="facebook")
    print(f"Caption ({len(caption)} chars):\n{caption[:300]}...")

if __name__ == "__main__":
    main()
