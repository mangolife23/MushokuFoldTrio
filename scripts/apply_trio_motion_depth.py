#!/usr/bin/env python3
"""Make the native character spring visible without moving launcher controls."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_motion_depth.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    '                val amplitude = if (widthDp < 650f) 5f else 9f\n',
    '''                // Different silhouettes need different travel. This is in physical
                // pixels and stays below the scene's computed overscan on both panes.
                val amplitude = (if (widthDp < 650f) 0f else 6f) +
                    when (trioSceneIndex) { 1 -> 12f; 2 -> 9f; else -> 11f }
''', "scene travel")
replace_once(
    '                val idleX = kotlin.math.sin(t * .34f + phase) * amplitude + trioTouchX\n'
    '                val idleY = kotlin.math.sin(t * .47f + 1.1f + phase) * (amplitude * .55f) + trioTouchY\n',
    '                val idleX = kotlin.math.sin(t * .52f + phase) * amplitude + trioTouchX\n'
    '                val idleY = kotlin.math.sin(t * .67f + 1.1f + phase) * (amplitude * .62f) + trioTouchY\n',
    "idle cadence")
replace_once(
    '                val rotation = kotlin.math.sin(t * .22f + phase) * when (trioSceneIndex) { 1 -> .16f; 2 -> .10f; else -> .13f }\n',
    '                val rotation = kotlin.math.sin(t * .30f + phase) * when (trioSceneIndex) { 1 -> .32f; 2 -> .24f; else -> .28f }\n',
    "scene rotation")
replace_once(
    '                val breathe = 1f + overscan + kotlin.math.sin(t * .72f + phase) * .0045f\n',
    '                val breathe = 1f + overscan + kotlin.math.sin(t * .82f + phase) * .008f\n',
    "scene breathing")
replace_once(
    '        trioTouchTargetX = ((x / root.width) - .5f) * -10f\n'
    '        trioTouchTargetY = ((y / root.height) - .5f) * -6f\n',
    '        trioTouchTargetX = ((x / root.width) - .5f) * -20f\n'
    '        trioTouchTargetY = ((y / root.height) - .5f) * -12f\n',
    "touch parallax")

main.write_text(s)
print("Strengthened bounded character spring, breathing, and touch parallax")
