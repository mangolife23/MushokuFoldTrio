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

        // Fill the launcher viewport without interrupting ongoing artwork motion.
        // CENTER_CROP preserves aspect ratio and crops overflow rather than fitting
        // the entire bitmap inside the view.
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
            // Roxy's transparent portrait shows the whole figure. Sylphie
            // remains centered; Eris's face is left of center in her wide art.
            if (view.tag == 0) view.scaleType = ImageView.ScaleType.FIT_CENTER
            else if (view.tag == 2) {
                val art = view.drawable
                if (art != null && art.intrinsicWidth > 0 && art.intrinsicHeight > 0 && view.width > 0 && view.height > 0) {
                    val scale = kotlin.math.max(view.width.toFloat() / art.intrinsicWidth,
                        view.height.toFloat() / art.intrinsicHeight)
                    val scaledWidth = art.intrinsicWidth * scale
                    val scaledHeight = art.intrinsicHeight * scale
                    val faceX = if (cover) .30f else .36f
                    val dx = (view.width * .45f - scaledWidth * faceX)
                        .coerceIn(view.width - scaledWidth, 0f)
                    val dy = (view.height - scaledHeight) * .5f
                    view.scaleType = ImageView.ScaleType.MATRIX
                    view.imageMatrix = android.graphics.Matrix().apply {
                        setScale(scale, scale)
                        postTranslate(dx, dy)
                    }
                }
            } else view.scaleType = ImageView.ScaleType.CENTER_CROP
            // The animation owns translation and scale. Resetting them here snaps
            // the artwork on a scene switch or a Fold7 layout pass.
            view.pivotX = view.width * 0.5f
            view.pivotY = view.height * focusY
        }
        apply(trioSceneFront)
        apply(trioSceneBack)
    }
'''

if s.count(old) != 1:
    raise SystemExit("Expected Build #21 framing block not found; refusing unsafe patch")
main.write_text(s.replace(old, new, 1))
print("Applied edge-to-edge Trio artwork framing with launcher UI unchanged")
