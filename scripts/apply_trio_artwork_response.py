#!/usr/bin/env python3
"""Let each artwork light respond briefly to touch and Roxy's reach beat."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_artwork_response.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    "                    TrioReachMotion.beat.intValue++\n",
    "                    TrioReachMotion.beat.intValue++\n"
    "                    trioArtworkFx?.pulse()\n",
    "Roxy reach response")
replace_once(
    "    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {\n"
    "        if (ev.actionMasked == MotionEvent.ACTION_DOWN || ev.actionMasked == MotionEvent.ACTION_MOVE) {\n",
    "    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {\n"
    "        if (trioActive && ev.actionMasked == MotionEvent.ACTION_DOWN) trioArtworkFx?.pulse()\n"
    "        if (ev.actionMasked == MotionEvent.ACTION_DOWN || ev.actionMasked == MotionEvent.ACTION_MOVE) {\n",
    "touch response")
replace_once(
    "        private val glint = Paint(Paint.ANTI_ALIAS_FLAG)\n\n"
    "        override fun onDraw(canvas: Canvas) {\n",
    """        private val glint = Paint(Paint.ANTI_ALIAS_FLAG)
        private var pulseBorn = 0L

        fun pulse() {
            pulseBorn = android.os.SystemClock.uptimeMillis()
            invalidate()
        }

        override fun onDraw(canvas: Canvas) {
""",
    "artwork pulse state")
replace_once(
    "            val seconds = android.os.SystemClock.uptimeMillis() / 1000f\n",
    """            val now = android.os.SystemClock.uptimeMillis()
            val seconds = now / 1000f
            val pulseAge = if (pulseBorn > 0L) ((now - pulseBorn).coerceAtLeast(0L) / 800f)
                .coerceIn(0f, 1f) else 1f
            val surge = (1f - pulseAge) * (1f - pulseAge)
""",
    "artwork pulse envelope")
replace_once(
    "                val radius = density * (if (kind == 1) 43f else 27f) * (1f + beat * .18f)\n",
    "                val radius = density * (if (kind == 1) 43f else 27f) *\n"
    "                    (1f + beat * .18f + surge * .22f)\n",
    "artwork light pulse")
replace_once(
    "                    intArrayOf(Color.argb((opacity * (36 + beat * 42)).toInt(),\n",
    "                    intArrayOf(Color.argb((opacity * (36 + beat * 42 + surge * 66)).toInt(),\n",
    "pulse brightness")
replace_once(
    "                canvas.drawArc(x - radius * .52f, y - radius * .52f,\n"
    "                    x + radius * .52f, y + radius * .52f,\n"
    "                    seconds * (if (kind == 2) 32f else 18f), sweep, false, glint)\n"
    "                canvas.restore()\n",
    """                canvas.drawArc(x - radius * .52f, y - radius * .52f,
                    x + radius * .52f, y + radius * .52f,
                    seconds * (if (kind == 2) 32f else 18f), sweep, false, glint)
                if (surge > .001f) {
                    glint.color = Color.argb((opacity * surge * 135).toInt(),
                        Color.red(color), Color.green(color), Color.blue(color))
                    glint.strokeWidth = density * (1f + surge * 2f)
                    when (kind) {
                        1 -> { // Sylphie's orb sends a soft ring outward.
                            val r = radius * (.35f + pulseAge * 1.25f)
                            canvas.drawCircle(x, y, r, glint)
                        }
                        2 -> { // A short blade glint follows Eris's sword.
                            canvas.drawLine(x - radius * .5f, y - radius * .45f,
                                x + radius * (1.0f + pulseAge),
                                y + radius * (.65f + pulseAge * .45f), glint)
                        }
                        else -> { // Roxy's crystal releases two small arcs.
                            val r = radius * (.42f + pulseAge * .8f)
                            canvas.drawArc(x - r, y - r, x + r, y + r,
                                seconds * 70f, 95f, false, glint)
                            canvas.drawArc(x - r, y - r, x + r, y + r,
                                seconds * 70f + 180f, 95f, false, glint)
                        }
                    }
                }
                canvas.restore()
""",
    "per-character pulse drawing")

main.write_text(s)
print("Added touch and reach responses to all three anchored artwork lights")
