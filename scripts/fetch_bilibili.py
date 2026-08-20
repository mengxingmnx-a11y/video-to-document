# -*- coding: utf-8 -*-
"""Fetch Bilibili video metadata + audio. Usage:
    python fetch_bilibili.py BVxxxxx [--out DIR]
"""
import argparse, json, os, sys, urllib.request

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
     "Referer": "https://www.bilibili.com"}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60).read()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bvid")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    view = json.loads(get(f"https://api.bilibili.com/x/web-interface/view?bvid={a.bvid}"))["data"]
    cid = view["cid"]
    print("TITLE:", view["title"])
    print("OWNER:", view["owner"]["name"])
    print("DURATION(s):", view["duration"])
    print("CID:", cid)
    p2 = json.loads(get(f"https://api.bilibili.com/x/player/v2?bvid={a.bvid}&cid={cid}"))
    subs = p2.get("data", {}).get("subtitle", {}).get("subtitles", [])
    print("SUBTITLES:", len(subs))
    for s in subs:
        print("  ", s.get("lan"), s.get("subtitle_url"))
    if subs:
        print("USE SUBTITLES; no audio download needed.")
        return
    pu = json.loads(get(f"https://api.bilibili.com/x/player/playurl?bvid={a.bvid}&cid={cid}&qn=0&fnval=16&fnver=0&fourk=1"))
    audio = max(pu["data"]["dash"]["audio"], key=lambda x: x.get("bandwidth", 0))
    url = audio["baseUrl"]
    out = os.path.join(a.out, "audio.m4s")
    with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=300) as r, open(out, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    print("AUDIO SAVED:", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()
