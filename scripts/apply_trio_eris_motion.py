#!/usr/bin/env python3
"""Add subtle, artwork-tracked native sword glints to Eris's scene."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_eris_motion.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()
old = '''        private fun drawRoxyHairMana(canvas: Canvas, scene: ImageView, now: Long) {
'''
new = '''        private fun drawErisSwordMana(canvas: Canvas, scene: ImageView, now: Long) {
            if (scene.tag != 2 || scene.alpha <= .01f) return
            val art = scene.drawable ?: return
            if (scene.width <= 0 || scene.height <= 0 || art.intrinsicWidth <= 0 || art.intrinsicHeight <= 0) return
            // ImageView's crop matrix and the View's spring transform both affect
            // the sword. Map the glints through those same matrices on every frame.
            fun artPoint(px: Float, py: Float): FloatArray {
                val point = floatArrayOf(px, py)
                scene.imageMatrix.mapPoints(point)
                scene.matrix.mapPoints(point)
                point[0] += scene.left; point[1] += scene.top
                return point
            }
            repeat(3) { i ->
                val phase = ((now * .00055f + i * .31f) % 1f)
                val x = 820f + phase * 680f
                val y = 1240f + phase * 640f
                val center = artPoint(x, y)
                val tip = artPoint(x + 16f, y - 16f)
                val strength = kotlin.math.sin(phase * kotlin.math.PI.toFloat()).coerceAtLeast(0f)
                paint.style = Paint.Style.STROKE
                paint.strokeWidth = 2f
                paint.color = Color.argb((scene.alpha * strength * 95f).toInt().coerceIn(0, 255), 255, 213, 184)
                canvas.drawLine(center[0] * 2f - tip[0], center[1] * 2f - tip[1], tip[0], tip[1], paint)
                paint.style = Paint.Style.FILL
                paint.color = Color.argb((scene.alpha * strength * 110f).toInt().coerceIn(0, 255), 255, 238, 216)
                canvas.drawCircle(center[0], center[1], 2.6f, paint)
            }
        }
        private fun drawRoxyHairMana(canvas: Canvas, scene: ImageView, now: Long) {
'''
if s.count(old) != 1:
    raise SystemExit("Expected Trio hair effect insertion point changed; refusing unsafe patch")
s = s.replace(old, new, 1)
old = '''            trioSceneFront?.let { drawRoxyHairMana(canvas, it, now) }
            trioSceneBack?.let { drawRoxyHairMana(canvas, it, now) }
'''
new = '''            trioSceneFront?.let { drawRoxyHairMana(canvas, it, now); drawErisSwordMana(canvas, it, now) }
            trioSceneBack?.let { drawRoxyHairMana(canvas, it, now); drawErisSwordMana(canvas, it, now) }
'''
if s.count(old) != 1:
    raise SystemExit("Expected Trio mana draw call changed; refusing unsafe patch")
main.write_text(s.replace(old, new, 1))
print("Added native Eris sword glints aligned to artwork crop and spring")
