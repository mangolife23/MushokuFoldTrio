#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_background_layer.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

old = '''        val back = sceneView(); val front = sceneView()
        host.addView(back, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(front, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSceneBack = back; trioSceneFront = front
'''
new = '''        val back = sceneView(); val front = sceneView()
        // Artwork is a true launcher background. Keep DuoLauncher's existing UI
        // (icons, search, folders, gestures) above both crossfade image layers.
        host.addView(back, 0, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(front, 1, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSceneBack = back; trioSceneFront = front
'''

if s.count(old) != 1:
    raise SystemExit("Expected Trio scene insertion block not found; refusing unsafe patch")
s = s.replace(old, new, 1)
main.write_text(s)
print("Moved opaque Trio artwork behind DuoLauncher UI while preserving mana overlay")
