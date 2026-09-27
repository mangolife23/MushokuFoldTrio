#!/usr/bin/env python3
"""Add short, framed expression poses for Sylphie and Eris."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_sylphie_eris_expressions.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    "        installTrioRoxyExpressionLayer()\n        installTrioArtworkFxLayer()\n",
    "        installTrioRoxyExpressionLayer()\n"
    "        installTrioAlternateExpressionLayer()\n"
    "        installTrioArtworkFxLayer()\n",
    "alternate pose setup")
replace_once(
    "    private var trioRoxyReach: ImageView? = null\n",
    "    private var trioRoxyReach: ImageView? = null\n"
    "    private var trioSylphieBlink: ImageView? = null\n"
    "    private var trioErisBlink: ImageView? = null\n",
    "alternate pose fields")
replace_once(
    "        apply(trioSceneBack)\n",
    "        apply(trioSceneBack)\n"
    "        apply(trioSylphieBlink)\n"
    "        apply(trioErisBlink)\n",
    "Fold7 pose framing")
replace_once(
    "                for (pose in arrayOf(trioRoxyExpression, trioRoxyReach)) {\n",
    "                for (pose in arrayOf(trioRoxyExpression, trioRoxyReach,\n"
    "                    trioSylphieBlink, trioErisBlink)) {\n",
    "pose spring transform")
replace_once(
    "    private fun scheduleTrioCharacterBeat() {\n",
    '''    private fun installTrioAlternateExpressionLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioSylphieBlink != null) return
        fun pose(resource: Int, character: Int) = ImageView(this).apply {
            setImageResource(resource)
            tag = character
            scaleType = ImageView.ScaleType.CENTER_CROP
            alpha = 0f
            isClickable = false
            isFocusable = false
        }
        val sylphie = pose(R.drawable.trio_sylphie_blink, 1)
        val eris = pose(R.drawable.trio_eris_blink, 2)
        // Alternate full-scene frames sit above portraits but below art FX,
        // mana, the contrast scrim, and real Compose launcher controls.
        host.addView(sylphie, 4, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(eris, 5, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSylphieBlink = sylphie
        trioErisBlink = eris
        updateTrioSceneFraming()
    }

    private fun scheduleTrioCharacterBeat() {
''',
    "alternate pose views")
replace_once(
    "        trioCharacterBeatRunnable?.let(host::removeCallbacks)\n"
    "        trioCharacterBeatRunnable = null\n",
    "        trioCharacterBeatRunnable?.let(host::removeCallbacks)\n"
    "        trioCharacterBeatRunnable = null\n"
    "        for (pose in arrayOf(trioSylphieBlink, trioErisBlink)) {\n"
    "            pose?.animate()?.cancel(); pose?.alpha = 0f\n"
    "        }\n",
    "pose beat reset")
replace_once(
    "                // The artwork effect and the real home icon react together.\n"
    "                trioArtworkFx?.pulse()\n",
    """                // Eyes briefly close before the icon and artwork light respond.
                val expression = if (character == 1) trioSylphieBlink else trioErisBlink
                expression?.let { pose ->
                    pose.animate().cancel()
                    pose.animate().alpha(1f).setDuration(110L).withEndAction {
                        pose.postDelayed({
                            if (trioActive && trioSceneIndex == character)
                                pose.animate().alpha(0f).setDuration(180L).start()
                            else pose.alpha = 0f
                        }, 120L)
                    }.start()
                }
                // The artwork effect and the real home icon react together.
                trioArtworkFx?.pulse()
""",
    "Sylphie and Eris blink beat")
replace_once(
    "        host.addView(fx, 4, ViewGroup.LayoutParams(\n",
    "        host.addView(fx, 6, ViewGroup.LayoutParams(\n",
    "artwork FX layer order")
replace_once(
    "        trioRoxyReach?.alpha = 0f\n",
    "        trioRoxyReach?.alpha = 0f\n"
    "        trioSylphieBlink?.animate()?.cancel(); trioSylphieBlink?.alpha = 0f\n"
    "        trioErisBlink?.animate()?.cancel(); trioErisBlink?.alpha = 0f\n",
    "stop alternate poses")
replace_once(
    "        trioRoxyReach?.animate()?.cancel()\n"
    "        trioExpressionRunnable = null; trioRoxyExpression = null; trioRoxyReach = null\n",
    "        trioRoxyReach?.animate()?.cancel()\n"
    "        trioSylphieBlink?.animate()?.cancel(); trioErisBlink?.animate()?.cancel()\n"
    "        trioExpressionRunnable = null; trioRoxyExpression = null; trioRoxyReach = null\n"
    "        trioSylphieBlink = null; trioErisBlink = null\n",
    "destroy alternate poses")

main.write_text(s)
print("Added brief Sylphie and Eris blink poses over their original scenes")
