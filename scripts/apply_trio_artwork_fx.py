#!/usr/bin/env python3
"""Add small artwork-anchored light beats without covering launcher controls."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_artwork_fx.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    "        installTrioRoxyExpressionLayer()\n",
    "        installTrioRoxyExpressionLayer()\n"
    "        installTrioArtworkFxLayer()\n",
    "artwork overlay setup")
replace_once(
    "    private var trioManaView: TrioManaView? = null\n",
    "    private var trioManaView: TrioManaView? = null\n"
    "    private var trioArtworkFx: TrioArtworkFxView? = null\n",
    "artwork overlay state")
replace_once(
    "                host.postDelayed(this, 32L)\n",
    "                trioArtworkFx?.invalidate()\n"
    "                host.postDelayed(this, 32L)\n",
    "overlay frame redraw")
replace_once(
    "    private fun installTrioContrastScrim() {\n",
    '''    private fun installTrioArtworkFxLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioArtworkFx != null) return
        val fx = TrioArtworkFxView()
        fx.isClickable = false
        fx.isFocusable = false
        // Above the portraits and poses, below mana, status scrim, and Compose.
        host.addView(fx, 4, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioArtworkFx = fx
    }

    private inner class TrioArtworkFxView : View(this) {
        private val glow = Paint(Paint.ANTI_ALIAS_FLAG)
        private val glint = Paint(Paint.ANTI_ALIAS_FLAG)

        override fun onDraw(canvas: Canvas) {
            super.onDraw(canvas)
            val seconds = android.os.SystemClock.uptimeMillis() / 1000f
            // Both sides draw during the 1.8 second scene crossfade.
            for (scene in arrayOf(trioSceneBack, trioSceneFront)) {
                scene ?: continue
                val opacity = scene.alpha.coerceIn(0f, 1f)
                if (opacity < .01f) continue
                val kind = scene.tag as? Int ?: continue
                val art = scene.drawable ?: continue
                val dw = art.intrinsicWidth.toFloat()
                val dh = art.intrinsicHeight.toFloat()
                if (dw <= 0f || dh <= 0f || scene.width <= 0 || scene.height <= 0) continue
                // Coordinates are in the original art, then mapped through the
                // exact image transform used for the cover or unfolded display.
                val anchor = when (kind) {
                    1 -> floatArrayOf(dw * .232f, dh * .750f) // Sylphie's orb
                    2 -> floatArrayOf(dw * .355f, dh * .705f) // Eris's blade
                    else -> floatArrayOf(dw * .895f, dh * .176f) // Roxy's staff
                }
                if (scene.scaleType == ImageView.ScaleType.MATRIX) {
                    scene.imageMatrix.mapPoints(anchor)
                } else {
                    val scale = if (scene.scaleType == ImageView.ScaleType.FIT_CENTER)
                        kotlin.math.min(scene.width / dw, scene.height / dh)
                    else kotlin.math.max(scene.width / dw, scene.height / dh)
                    anchor[0] = (scene.width - dw * scale) * .5f + anchor[0] * scale
                    anchor[1] = (scene.height - dh * scale) * .5f + anchor[1] * scale
                }
                val x = anchor[0]; val y = anchor[1]
                if (x < -80f || x > width + 80f || y < -80f || y > height + 80f) continue
                val density = resources.displayMetrics.density.coerceAtLeast(1f)
                val beat = (kotlin.math.sin(seconds * when (kind) {
                    1 -> 1.24f; 2 -> 2.06f; else -> 1.51f
                }) + 1f) * .5f
                val color = when (kind) {
                    1 -> Color.rgb(255, 90, 45)
                    2 -> Color.rgb(210, 235, 255)
                    else -> Color.rgb(81, 165, 255)
                }
                val radius = density * (if (kind == 1) 43f else 27f) * (1f + beat * .18f)
                canvas.save()
                canvas.concat(scene.matrix)
                glow.shader = android.graphics.RadialGradient(x, y, radius,
                    intArrayOf(Color.argb((opacity * (36 + beat * 42)).toInt(),
                        Color.red(color), Color.green(color), Color.blue(color)),
                        Color.argb((opacity * 12).toInt(), Color.red(color), Color.green(color), Color.blue(color)),
                        Color.TRANSPARENT), floatArrayOf(0f, .46f, 1f),
                    android.graphics.Shader.TileMode.CLAMP)
                canvas.drawCircle(x, y, radius, glow)
                glow.shader = null
                glint.color = Color.argb((opacity * (24 + beat * 44)).toInt(),
                    Color.red(color), Color.green(color), Color.blue(color))
                glint.style = Paint.Style.STROKE
                glint.strokeWidth = density * 1.2f
                val sweep = if (kind == 2) 42f else 75f
                canvas.drawArc(x - radius * .52f, y - radius * .52f,
                    x + radius * .52f, y + radius * .52f,
                    seconds * (if (kind == 2) 32f else 18f), sweep, false, glint)
                canvas.restore()
            }
        }
    }

    private fun installTrioContrastScrim() {
''',
    "artwork overlay drawing")

main.write_text(s)
print("Added subtle staff, orb, and sword light beats anchored to artwork")
