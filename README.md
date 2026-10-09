# AI-þátturinn (vinnuheiti)

Vikulegur þáttur á íslensku um gervigreind: Addi í vefmyndavél, um 10 mínútur, með grafík úr After Effects og Blender. Klippur fyrir TikTok, YouTube Shorts og Instagram Reels.

## Hvar er hvað

| Mappa / skjal | Innihald |
|---|---|
| [`snid/thattarsnid.md`](snid/thattarsnid.md) | Snið þáttarins: uppbygging, rödd (Gagnaverið og MORFÍS-ræðurnar), óháðar mælingar á módelum, heimildareglur, reglur YouTube og TikTok, vinnuferli |
| [`snidmat/`](snidmat/) | Sniðmát fyrir hverja viku: rannsókn, storyboard og handrit |
| [`thaettir/`](thaettir/) | Ein mappa fyrir hvern þátt |
| [`thaettir/001-2026-10-09/`](thaettir/001-2026-10-09/) | Fyrsti þátturinn: [rannsókn](thaettir/001-2026-10-09/rannsokn.md), [storyboard](thaettir/001-2026-10-09/storyboard.md) ([myndræn útgáfa](thaettir/001-2026-10-09/storyboard.html)) og [handrit](thaettir/001-2026-10-09/handrit.md); gögn fyrir grafík í [`grafik/`](thaettir/001-2026-10-09/grafik/) |
| [`tol/malfar.py`](tol/malfar.py) | Málfarsrýni fyrir handrit (GreynirCorrect frá Miðeind) |
| [`tol/skjatextar.py`](tol/skjatextar.py) | Skjátextar (SRT) úr upptöku og Wispr Flow uppskrift |
| [`tol/klippa.py`](tol/klippa.py) | Lóðrétt klippa (9:16) með innbrenndum skjátextum |

## Málfarsrýni

```bash
pip install reynir-correct
python -m icegrams.download   # einu sinni, sækir mállíkanið
python tol/malfar.py thaettir/001-2026-10-09/handrit.md
```

Tólið bendir á villur en breytir engu sjálft. Það skilur ekki slangur, enskuslettur eða viljandi teygð orð („Neeeiii“), svo þær athugasemdir má hunsa.
