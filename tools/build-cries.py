"""Convert PokeAPI cries (OGG Vorbis, which Safari cannot play) into small AAC .m4a files.

Usage:
    python tools/build-cries.py <dir-with-{id}.ogg>   [--ids 1-1025]

Source: https://github.com/PokeAPI/cries  (cries/pokemon/latest/{id}.ogg)
Output: cries/{id}.m4a in the repo root - mono, 24 kHz, ~48 kbps, loudness-normalised so
        quiet and loud cries play at a similar level. Needs ffmpeg on PATH or in FFMPEG env var.
"""
import concurrent.futures, glob, os, pathlib, shutil, subprocess, sys

def find_ffmpeg():
    cand = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if cand:
        return cand
    hits = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*ffmpeg*\*\bin\ffmpeg.exe"))
    if hits:
        return hits[0]
    sys.exit("ffmpeg not found; set FFMPEG=<path to ffmpeg.exe>")

def convert(ffmpeg, src, dst):
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ac", "1", "-ar", "24000",
           "-c:a", "aac", "-b:a", "48k", "-movflags", "+faststart", str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return (src.stem, r.returncode == 0, r.stderr.strip())

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src_dir = pathlib.Path(sys.argv[1])
    lo, hi = 1, 1025
    if "--ids" in sys.argv:
        lo, hi = (int(x) for x in sys.argv[sys.argv.index("--ids") + 1].split("-"))
    ffmpeg = find_ffmpeg()
    out = pathlib.Path(__file__).resolve().parent.parent / "cries"
    out.mkdir(exist_ok=True)
    jobs = []
    for i in range(lo, hi + 1):
        src = src_dir / f"{i}.ogg"
        if src.exists():
            jobs.append((src, out / f"{i}.m4a"))
        else:
            print("missing source", src, file=sys.stderr)
    failed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        for stem, ok, err in ex.map(lambda j: convert(ffmpeg, *j), jobs):
            if not ok:
                failed.append((stem, err))
    total = sum(p.stat().st_size for p in out.glob("*.m4a"))
    print(f"converted {len(jobs) - len(failed)}/{len(jobs)} -> {out} ({total / 1e6:.1f} MB)")
    for stem, err in failed[:10]:
        print("FAILED", stem, err, file=sys.stderr)
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
