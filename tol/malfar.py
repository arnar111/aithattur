"""Málfarsrýni fyrir handrit þáttarins.

Keyrir GreynirCorrect (Miðeind) á Markdown-skjal og prentar þær setningar
sem fá athugasemd. Tólið breytir engu sjálft, það bendir bara á.

Uppsetning (einu sinni):
    pip install reynir-correct
    python -m icegrams.download

Notkun:
    python tol/malfar.py thaettir/001-2026-10-09/handrit.md
"""

import re
import sys

from reynir_correct import check_with_stats

# Línur sem eru ekki talað mál: fyrirsagnir, töflur, tenglar, leiðbeiningar
# í hornklofum og kóðablokkir.
SLEPPA = re.compile(r"^\s*(#|\||>|```|-{3,}|\[|https?://)")


def talmal(texti: str) -> str:
    """Skilar aðeins þeim línum sem verða lesnar upp."""
    linur = []
    i_kodablokk = False
    for lina in texti.splitlines():
        if lina.strip().startswith("```"):
            i_kodablokk = not i_kodablokk
            continue
        if i_kodablokk or SLEPPA.match(lina):
            continue
        # Fjarlægja sviðsleiðbeiningar [svona] og (svona), Markdown-áherslur
        # og nafn þess sem talar, t.d. "**ADDI:**".
        lina = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", lina)
        lina = re.sub(r"\*\*[A-ZÁÐÉÍÓÚÝÞÆÖ0-9 ]+:\*\*", "", lina)
        lina = lina.replace("**", "").replace("*", "").replace("_", "")
        lina = lina.strip(" -")
        if lina:
            linur.append(lina)
    return "\n\n".join(linur)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        texti = talmal(f.read())

    nidurstada = check_with_stats(texti, split_paragraphs=True)
    fjoldi = 0
    for setning in nidurstada["sentences"]:
        if not setning.annotations:
            continue
        fjoldi += 1
        print(f"\n> {setning.text}")
        for athugasemd in setning.annotations:
            print(f"  {athugasemd}")
    print(f"\n{fjoldi} setningar með athugasemd af {nidurstada['num_sentences']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
