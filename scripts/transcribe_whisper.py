# -*- coding: utf-8 -*-
"""Wrap whisper-cli transcription. Usage:
    python transcribe_whisper.py --cli <whisper-cli.exe dir> --model <ggml-small.bin> --audio <audio.wav> --out <prefix>
Requires whisper.cpp Release dir (whisper-cli.exe + DLLs) and a ggml model.
"""
import argparse, os, subprocess, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True, help="whisper.cpp Release dir containing whisper-cli.exe")
    ap.add_argument("--model", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default="zh")
    ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args()
    exe = os.path.join(a.cli, "whisper-cli.exe")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    cmd = [exe, "-m", a.model, "-f", a.audio, "-l", a.lang, "-t", str(a.threads),
           "-bs", "3", "-otxt", "-oj", "-of", a.out]
    env = dict(os.environ)
    proc = subprocess.run(cmd, cwd=a.cli, env=env, capture_output=True, text=True)
    print(proc.stdout[-2000:])
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-2000:], file=sys.stderr)
        sys.exit(proc.returncode)
    for suffix in (".txt", ".json"):
        p = a.out + suffix
        if os.path.exists(p):
            print("saved:", p, os.path.getsize(p), "bytes")

if __name__ == "__main__":
    main()
