#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_background_layer.py <duo-source-root>")

root = Path(sys.argv[1])
main = root / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
launcher = root / "app/src/main/java/com/jake/duolauncher/LauncherScreen.kt"

s = main.read_text()
old = '''        val back = sceneView(); val front = sceneView()
        host.addView(back, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(front, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSceneBack = back; trioSceneFront = front
'''
new = '''        val back = sceneView(); val front = sceneView()
        // Artwork is a real launcher background. Duo's Compose content stays above it.
        host.addView(back, 0, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(front, 1, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSceneBack = back; trioSceneFront = front
'''
if s.count(old) != 1:
    raise SystemExit("Expected Trio scene insertion block not found; refusing unsafe patch")
main.write_text(s.replace(old, new, 1))

# DuoLauncher paints its own full-screen DuneWallpaper inside LauncherScreen.
# Build #23 proved that this Compose layer hides our correctly-positioned background.
# Remove only that one home-screen wallpaper call; keep every launcher control intact.
l = launcher.read_text()
needle = '''        DuneWallpaper()
        BoxWithConstraints(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing)) {'''
replacement = '''        // Trio supplies the opaque animated character background below Compose.
        BoxWithConstraints(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing)) {'''
if l.count(needle) != 1:
    raise SystemExit("Expected LauncherScreen DuneWallpaper block not found; refusing unsafe patch")
launcher.write_text(l.replace(needle, replacement, 1))

print("Moved Trio artwork behind Duo UI and removed only Duo's opaque home wallpaper layer")
