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

## Prototype APK signing

Actions currently falls back to a fresh runner debug key. Its APK can build successfully but cannot update an earlier APK signed by another runner. The security report in each artifact records `prototype_signing_mode` and the certificate fingerprint.

For repeatable updates, create a private Android keystore and configure these GitHub Actions repository secrets: `TRIO_KEYSTORE_BASE64` (base64 of the keystore file), `TRIO_STORE_PASSWORD`, `TRIO_KEY_ALIAS`, and `TRIO_KEY_PASSWORD`. Keep the keystore and passwords outside this public repository. The workflow uses the key only for the isolated `com.otakuhoarder.mushokufold.nativeprototype` APK. All four secrets must be set together; otherwise the build fails rather than publishing an unexpectedly signed APK.

The first stable-signed APK cannot update a previously installed runner-signed prototype. After that one-time install migration, keep the same private keystore so subsequent builds can update in place.
