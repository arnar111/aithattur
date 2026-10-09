"""Skjátextar úr upptöku og uppskrift (t.d. frá Wispr Flow).

Wispr Flow skilar nákvæmum íslenskum texta en ekki tímasetningum. Þetta tól
stillir textann af við hljóðið (forced alignment með stable-ts/Whisper) og
býr til skjátexta:

    <ut>.srt           YouTube (2 línur, mest 42 stafir í línu)
    <ut>_lodrett.srt   TikTok, Shorts og Reels (1 stutt lína í einu)
    <ut>_ord.json      tími hvers orðs, fyrir grafík í After Effects eða Remotion

Uppsetning (einu sinni):
    pip install torch --index-url https://download.pytorch.org/whl/cpu
    pip install stable-ts

Notkun:
    python tol/skjatextar.py upptaka.m4a --texti wispr.txt --ut thaettir/<þáttur>/skjatextar
    python tol/skjatextar.py upptaka.m4a --ut ...   (án uppskriftar: Whisper giskar á textann, verri gæði)
"""

import argparse
import json
import re
import sys
from pathlib import Path

ENDIR = (".", "?", "!", "…")


def hreinsa_texta(texti: str) -> str:
    """Fjarlægir tímastimpla og nöfn þeirra sem tala, ef uppskriftin er með slíkt."""
    linur = []
    for lina in texti.splitlines():
        lina = re.sub(r"^\s*\[?\d{1,2}:\d{2}(:\d{2})?(\.\d+)?\]?\s*", "", lina)
        lina = re.sub(r"^\s*[A-ZÁÐÉÍÓÚÝÞÆÖa-záðéíóúýþæö .]{1,30}:\s+", "", lina)
        if lina.strip():
            linur.append(lina.strip())
    return " ".join(linur)


def ord_ur_nidurstodu(nidurstada) -> list[dict]:
    ord_ = []
    for seg in nidurstada.segments:
        for w in seg.words:
            texti = w.word.strip()
            if texti:
                ord_.append({"ord": texti, "byrjun": round(w.start, 3), "endir": round(w.end, 3)})
    return ord_


def passar(texti: str, max_lina: int, max_linur: int) -> bool:
    """Kemst textinn fyrir í max_linur línum sem eru mest max_lina stafir?"""
    linur, nuna = 1, ""
    for o in texti.split():
        if len(o) > max_lina:
            return False
        if nuna and len(nuna) + 1 + len(o) > max_lina:
            linur, nuna = linur + 1, o
        else:
            nuna = f"{nuna} {o}".strip()
    return linur <= max_linur


def bua_til_spjold(ord_: list[dict], max_lina: int, max_linur: int, max_lengd: float, max_hle: float) -> list[dict]:
    """Raðar orðum í spjöld: brýtur við setningaskil, kommur, löng hlé, lengd og plássleysi."""
    spjold, nuna = [], []
    rymd = max_lina * max_linur

    def texti(ord_lista):
        return " ".join(x["ord"] for x in ord_lista)

    def loka():
        if nuna:
            spjold.append({"byrjun": nuna[0]["byrjun"], "endir": nuna[-1]["endir"], "texti": texti(nuna)})
            nuna.clear()

    for o in ord_:
        if nuna:
            hle = o["byrjun"] - nuna[-1]["endir"]
            if (not passar(texti(nuna + [o]), max_lina, max_linur) or hle > max_hle
                    or o["endir"] - nuna[0]["byrjun"] > max_lengd):
                loka()
        nuna.append(o)
        lengd = len(texti(nuna))
        if o["ord"].endswith(ENDIR) and lengd > rymd * 0.3:
            loka()
        elif o["ord"].endswith((",", ":", ";")) and lengd > rymd * 0.6:
            loka()
    loka()
    return spjold


def skipta_i_linur(texti: str, max_lina: int) -> str:
    """Skiptir í mest tvær línur, sem jafnlangar og hægt er."""
    if len(texti) <= max_lina:
        return texti
    ord_ = texti.split()
    best, best_munur = texti, 10**9
    for i in range(1, len(ord_)):
        a, b = " ".join(ord_[:i]), " ".join(ord_[i:])
        if len(a) <= max_lina and len(b) <= max_lina and abs(len(a) - len(b)) < best_munur:
            best, best_munur = f"{a}\n{b}", abs(len(a) - len(b))
    return best


def timi(sek: float) -> str:
    ms = int(round(sek * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def skrifa_srt(spjold: list[dict], slod: Path, max_lina: int, min_lengd: float = 1.0) -> None:
    hlutar = []
    for i, sp in enumerate(spjold):
        endir = max(sp["endir"], sp["byrjun"] + min_lengd)
        if i + 1 < len(spjold):
            endir = min(endir, spjold[i + 1]["byrjun"] - 0.04)
        hlutar.append(f"{i + 1}\n{timi(sp['byrjun'])} --> {timi(endir)}\n{skipta_i_linur(sp['texti'], max_lina)}\n")
    slod.write_text("\n".join(hlutar), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("hljod", help="hljóð- eða myndskrá (wav, m4a, mp3, mp4, mov ...)")
    p.add_argument("--texti", help="uppskrift, t.d. frá Wispr Flow (txt)")
    p.add_argument("--ut", default="skjatextar", help="forskeyti úttaksskráa")
    p.add_argument("--likan", default="small", help="Whisper-líkan: base, small, medium (stærra = nákvæmara, hægara)")
    a = p.parse_args()

    import stable_whisper

    likan = stable_whisper.load_model(a.likan)
    if a.texti:
        texti = hreinsa_texta(Path(a.texti).read_text(encoding="utf-8"))
        nidurstada = likan.align(a.hljod, texti, language="is")
    else:
        print("Engin uppskrift: Whisper giskar á textann. Farðu vel yfir hann.", file=sys.stderr)
        nidurstada = likan.transcribe(a.hljod, language="is", word_timestamps=True)

    ord_ = ord_ur_nidurstodu(nidurstada)
    ut = Path(a.ut)
    ut.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{ut}_ord.json").write_text(json.dumps(ord_, ensure_ascii=False, indent=1), encoding="utf-8")
    skrifa_srt(bua_til_spjold(ord_, 42, 2, 7.0, 0.7), Path(f"{ut}.srt"), 42)
    skrifa_srt(bua_til_spjold(ord_, 22, 1, 2.5, 0.4), Path(f"{ut}_lodrett.srt"), 22)
    print(f"{len(ord_)} orð. Skrifaði {ut}.srt, {ut}_lodrett.srt og {ut}_ord.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
