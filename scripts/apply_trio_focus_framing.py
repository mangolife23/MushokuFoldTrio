#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_focus_framing.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

old = '''    private fun updateTrioSceneFraming() {
        val density = resources.displayMetrics.density.coerceAtLeast(1f)
        val widthDp = window.decorView.width / density
        // Cover screen: show the whole illustration instead of CENTER_CROP cutting off faces.
        // Unfolded screen: use a gentle fit while retaining the full character composition.
        val type = if (widthDp in 1f..649.99f) ImageView.ScaleType.CENTER_INSIDE else ImageView.ScaleType.FIT_CENTER
        trioSceneFront?.scaleType = type
        trioSceneBack?.scaleType = type
    }
'''

new = '''    private fun updateTrioSceneFraming() {
        val density = resources.displayMetrics.density.coerceAtLeast(1f)
        val widthDp = window.decorView.width / density
        val cover = widthDp in 1f..649.99f
        // Fill the viewport again, but bias each character vertically so CENTER_CROP
        // keeps the face/upper body instead of blindly centering the source image.
        val focusY = if (cover) {
            when (trioSceneIndex) {
                0 -> 0.30f // Roxy
                1 -> 0.32f // Sylphie
                else -> 0.28f // Eris
            }
        } else {
            when (trioSceneIndex) {
                0 -> 0.40f
                1 -> 0.42f
                else -> 0.38f
            }
        }
        fun apply(view: ImageView?) {
            view ?: return
            view.scaleType = ImageView.ScaleType.CENTER_CROP
            view.pivotX = view.width * 0.5f
            view.pivotY = view.height * focusY
            view.translationY = if (cover) view.height * (0.50f - focusY) * 0.34f else 0f
        }
        apply(trioSceneFront)
        apply(trioSceneBack)
    }
'''

if s.count(old) != 1:
    raise SystemExit("Expected Build #21 framing block not found; refusing unsafe patch")
main.write_text(s.replace(old, new, 1))
print("Applied character-aware full-screen Trio focus framing")
