#!/usr/bin/env python3
"""Give the three launcher portraits distinct, bounded idle choreography."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_character_motion.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
source = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global source
    if source.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    source = source.replace(old, new, 1)

replace_once(
    "    private var trioSceneIndex = 0\n",
    "    private var trioSceneIndex = 0\n"
    "    private var trioSceneStartedAt = android.os.SystemClock.uptimeMillis()\n",
    "scene timing state")
replace_once(
    "        trioSceneFront = newFront; trioSceneBack = oldFront; trioSceneIndex = index % 3\n",
    "        trioSceneFront = newFront; trioSceneBack = oldFront; trioSceneIndex = index % 3\n"
    "        trioSceneStartedAt = android.os.SystemClock.uptimeMillis()\n",
    "scene timing reset")
replace_once(
    "                // Two slow rhythms prevent a perfectly repeating pendulum path.\n"
    "                val idleX = (kotlin.math.sin(t * .52f + phase) +\n"
    "                    .31f * kotlin.math.sin(t * .19f + phase * .63f)) * amplitude + trioTouchX\n"
    "                val idleY = (kotlin.math.sin(t * .67f + 1.1f + phase) * .62f +\n"
    "                    .18f * kotlin.math.sin(t * .27f + phase * 1.4f)) * amplitude + trioTouchY\n",
    """                // Roxy glides, Sylphie floats, and Eris makes a short, confident
                // shift twice per scene. The accent eases to zero at both ends.
                val sceneAge = (now - trioSceneStartedAt).coerceAtLeast(0L) / 1000f
                val accentDistance = (1f - kotlin.math.abs((sceneAge % 13f) - 5f) / 1.8f)
                    .coerceIn(0f, 1f)
                val erisAccent = accentDistance * accentDistance * (3f - 2f * accentDistance)
                val (idleX, idleY) = when (trioSceneIndex) {
                    1 -> Pair(
                        (kotlin.math.sin(t * .37f + phase) * .72f +
                            kotlin.math.sin(t * .16f + .8f) * .24f) * amplitude + trioTouchX,
                        (kotlin.math.sin(t * .48f + 1.1f + phase) * .63f +
                            kotlin.math.sin(t * .21f + .4f) * .22f) * amplitude + trioTouchY)
                    2 -> Pair(
                        (kotlin.math.sin(t * .76f + phase) * .80f +
                            kotlin.math.sin(t * .31f + .3f) * .14f) * amplitude +
                            erisAccent * 7f + trioTouchX,
                        (kotlin.math.sin(t * .88f + phase) * .42f) * amplitude -
                            erisAccent * 4f + trioTouchY)
                    else -> Pair(
                        (kotlin.math.sin(t * .52f + phase) +
                            .31f * kotlin.math.sin(t * .19f + phase * .63f)) * amplitude + trioTouchX,
                        (kotlin.math.sin(t * .67f + 1.1f + phase) * .62f +
                            .18f * kotlin.math.sin(t * .27f + phase * 1.4f)) * amplitude + trioTouchY)
                }
""",
    "character paths")
replace_once(
    "                val rotation = kotlin.math.sin(t * .30f + phase) * when (trioSceneIndex) { 1 -> .32f; 2 -> .24f; else -> .28f }\n",
    """                val rotation = when (trioSceneIndex) {
                    1 -> kotlin.math.sin(t * .23f + phase) * .38f
                    2 -> kotlin.math.sin(t * .39f + phase) * .23f + erisAccent * .13f
                    else -> kotlin.math.sin(t * .30f + phase) * .28f
                }
""",
    "character sway")
replace_once(
    "                val breathe = 1f + overscan + kotlin.math.sin(t * .82f + phase) * .007f +\n"
    "                    kotlin.math.sin(t * 1.64f + phase + .6f) * .002f\n",
    """                val breathe = 1f + overscan + when (trioSceneIndex) {
                    1 -> kotlin.math.sin(t * .71f + phase) * .006f +
                        kotlin.math.sin(t * 1.42f + .6f) * .002f
                    2 -> kotlin.math.sin(t * .94f + phase) * .004f +
                        kotlin.math.sin(t * 1.88f + .6f) * .001f
                    else -> kotlin.math.sin(t * .82f + phase) * .007f +
                        kotlin.math.sin(t * 1.64f + phase + .6f) * .002f
                }
""",
    "character breath")

main.write_text(source)
print("Added distinct Roxy, Sylphie, and Eris portrait motion")
