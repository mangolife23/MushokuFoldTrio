# MushokuFoldTrio

Samsung Galaxy Z Fold7 launcher integration based on genuine DuoLauncher, expanding the validated MushokuFoldRoxy experience into an adult-character scene system for Roxy, Sylphie, and Eris.

## Engineering invariants

- Genuine DuoLauncher upstream is pinned and verified in CI.
- Hardware-validated Fold7 detector is preserved: narrow `<650dp` to expanded `>=650dp`, with at least `1.35x` width growth.
- The live Activity root is never scaled during unfold; effects wait for expanded layout to settle.
- Visual overlays never consume launcher touch events.
- Character artwork remains separate from launcher logic.

## Character direction

- **Roxy** — water-blue mana and droplets.
- **Sylphie** — pale green/white wind mana.
- **Eris** — warm red/orange sword-energy accents.

Only adult-era artwork will be used for the three character scene collections.
