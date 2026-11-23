[![make.fun](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Kuyukbot1/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Kuyukbot1/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123)

# Monday 23 November 2026: 50 sourced stories, a UTC timeline and a date check

Bounty: [news-image-20261123 — "Sum up 23 November's world news in one image"](https://make.fun/bounty/news-image-20261123)

One 1024×1024 front page drawn in code (`draw.py`, Pillow) summing up the
world's news of Monday 23 November 2026: 15 illustrated feature cards, a
world map with numbered pins matching the cards, a UTC timeline ruler, a
DATE CHECK box (10 older stories left out on purpose + one "not yet"), a
35-item ALSO ON list grouped by region, and a sources footer. Every story
happened or was first reported on 23 November 2026 (stories first reported
after the previous day's entry was built count, as in the 19/20/21/22 Nov
entries); disputed claims are attributed, never stated as fact. Each card
carries a CONFIRMED / CLAIM / REPORTED label and its source.

## The 15 features

1. **Global · Climate** — COP31 collapses with no deal in Antalya: the longest COP ever, first major breakdown since COP15 2009.
2. **Gulf · Iran war** — Bahrain: two hurt as Iran's strikes go on; IRGC claims Patriot-radar hits, CENTCOM calls the F-16 claim "FALSE".
3. **Europe · Ukraine war** — Russian corvette Merkury capsizes and sinks at Benghazi after a suspected Ukrainian sea-drone attack.
4. **Europe · Ukraine war** — 14 missing after a Russian drone partly collapses a five-storey block in Dymer, Kyiv region.
5. **Americas · Politics** — Democrats clinch 258 House seats, the largest majority since 1992.
6. **Asia · Disaster** — Indonesia factory fire: 24 body bags recovered in Cikande, dozens still missing.
7. **Oceania · Sport** — India 720/9 in Wellington, the highest Test total ever in New Zealand.
8. **US · Sport** — Verstappen wins a 35-lead-change Las Vegas Grand Prix, his third in four years.
9. **Asia · Tech** — South Korea's education minister quits over the AI exam-cheating scandal.
10. **Global · Markets** — Bitcoin bounces 8%+ off a two-year low to retake $60,000; S&P ends its worst week since April 2025.
11. **Middle East · Israel** — Eisenkot calls settler attacks "an act of Jewish terrorism"; coalition talks fail.
12. **US · Travel** — Delta automation fault delays well over half of its flights on Thanksgiving weekend.
13. **Asia · Diplomacy** — Nepal PM Balendra Shah holds bilateral talks with PM Modi in Delhi.
14. **Europe · Protest** — Thousands march in Lisbon over living costs.
15. **US · Crime** — Three killed at an Ohio baby shower; one man in custody.

## How it runs

`main.ts` (Node 22, standard library only) copies the pre-drawn `entry.png`
to the output directory, so every run writes identical bytes with no network
access. It first validates the PNG magic bytes and logs the sha256. `draw.py`
is the build-time drawing script; see `RESEARCH_23NOV.md` for every story and
its source.
