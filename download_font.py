"""
download_font.py — Auto-download NotoSansDevanagari font
=========================================================
Run once: python download_font.py
"""
import os
import urllib.request
from pathlib import Path

FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
FONT_PATH = Path("fonts") / "NotoSansDevanagari-Regular.ttf"

def download():
    FONT_PATH.parent.mkdir(exist_ok=True)
    if FONT_PATH.exists():
        print(f"✅ Font already exists: {FONT_PATH}")
        return
    print(f"Downloading Noto Sans Devanagari font...")
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    print(f"Font downloaded: {FONT_PATH} ({FONT_PATH.stat().st_size:,} bytes)")

if __name__ == "__main__":
    download()
