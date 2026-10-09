# AI-þátturinn (vinnuheiti)

Vikulegur þáttur á íslensku um það nýjasta í gervigreind, fyrir YouTube og sem lóðréttar klippur á TikTok, YouTube Shorts og Instagram Reels.

## Hvar er hvað

| Mappa / skjal | Innihald |
|---|---|
| [`snid/thattarsnid.md`](snid/thattarsnid.md) | Snið þáttarins: liðir, rödd, stílbrögð úr MORFÍS-ræðunum, heimildareglur, reglur YouTube og TikTok, vikulegt vinnuferli |
| [`snidmat/`](snidmat/) | Sniðmát fyrir hverja viku: rannsókn, storyboard og handrit |
| [`thaettir/`](thaettir/) | Ein mappa fyrir hvern þátt |
| [`thaettir/001-2026-10-09/`](thaettir/001-2026-10-09/) | Fyrsti þátturinn: [rannsókn](thaettir/001-2026-10-09/rannsokn.md), [storyboard](thaettir/001-2026-10-09/storyboard.md) ([myndræn útgáfa](thaettir/001-2026-10-09/storyboard.html)) og [handrit](thaettir/001-2026-10-09/handrit.md) |
| [`tol/malfar.py`](tol/malfar.py) | Málfarsrýni fyrir handrit (GreynirCorrect frá Miðeind) |

## Málfarsrýni

```bash
pip install reynir-correct
python -m icegrams.download   # einu sinni, sækir mállíkanið
python tol/malfar.py thaettir/001-2026-10-09/handrit.md
```

Tólið bendir á villur en breytir engu sjálft. Það skilur ekki slangur, enskuslettur eða viljandi teygð orð („Neeeiii“), svo þær athugasemdir má hunsa.
