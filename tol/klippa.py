"""Lóðrétt klippa (9:16) með innbrenndum skjátextum fyrir TikTok, Shorts og Reels.

Sker bút úr upptökunni, klippir miðjuna út í 9:16 (Addi er í miðjum ramma),
og brennir inn skjátexta úr <ut>_lodrett.srt frá skjatextar.py.

Notkun:
    python tol/klippa.py upptaka.mp4 01:35 02:20 thaettir/<þáttur>/skjatextar_lodrett.srt klippa1.mp4

Þarf ffmpeg.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

STILL = ("FontName=Arial,FontSize=13,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
         "BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=80")


def sek(t: str) -> float:
    hlutar = [float(x) for x in t.replace(",", ".").split(":")]
    while len(hlutar) < 3:
        hlutar.insert(0, 0.0)
    return hlutar[0] * 3600 + hlutar[1] * 60 + hlutar[2]


def srt_timi(s: float) -> str:
    ms = max(0, int(round(s * 1000)))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s_, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"


def hlidra_srt(srt: str, byrjun: float, endir: float) -> str:
    """Heldur spjöldum innan bútsins og færir tímana svo bútinn byrji á 0."""
    ut, nr = [], 0
    for blokk in re.split(r"\n\s*\n", srt.strip()):
        linur = blokk.splitlines()
        if len(linur) < 3 or "-->" not in linur[1]:
            continue
        a, b = (sek(x.strip()) for x in linur[1].split("-->"))
        if b <= byrjun or a >= endir:
            continue
        nr += 1
        ut.append(f"{nr}\n{srt_timi(max(a, byrjun) - byrjun)} --> {srt_timi(min(b, endir) - byrjun)}\n" + "\n".join(linur[2:]))
    return "\n\n".join(ut) + "\n"


def main() -> int:
    if len(sys.argv) != 6:
        print(__doc__)
        return 2
    upptaka, byrjun, endir, srt, ut = sys.argv[1:]
    b, e = sek(byrjun), sek(endir)
    with tempfile.TemporaryDirectory() as d:
        bút_srt = Path(d) / "bútur.srt"
        bút_srt.write_text(hlidra_srt(Path(srt).read_text(encoding="utf-8"), b, e), encoding="utf-8")
        sia = (f"crop=ih*9/16:ih,scale=1080:1920,"
               f"subtitles={bút_srt.as_posix()}:force_style='{STILL}'")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(b), "-to", str(e), "-i", upptaka,
                        "-vf", sia, "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-c:a", "aac", "-b:a", "160k", ut], check=True)
    print(f"Skrifaði {ut}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
