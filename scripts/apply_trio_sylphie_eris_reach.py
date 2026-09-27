#!/usr/bin/env python3
"""Stage Sylphie's reach and Eris's sword motion with launcher icons."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_sylphie_eris_reach.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    "        installTrioAlternateExpressionLayer()\n        installTrioArtworkFxLayer()\n",
    "        installTrioAlternateExpressionLayer()\n"
    "        installTrioAlternateReachLayer()\n"
    "        installTrioArtworkFxLayer()\n",
    "alternate reach setup")
replace_once(
    "    private var trioErisBlink: ImageView? = null\n",
    "    private var trioErisBlink: ImageView? = null\n"
    "    private var trioSylphieReach: ImageView? = null\n"
    "    private var trioErisReach: ImageView? = null\n",
    "reach pose state")
replace_once(
    "        apply(trioErisBlink)\n",
    "        apply(trioErisBlink)\n"
    "        apply(trioSylphieReach)\n"
    "        apply(trioErisReach)\n",
    "reach pose Fold7 framing")
replace_once(
    "                    trioSylphieBlink, trioErisBlink)) {\n",
    "                    trioSylphieBlink, trioErisBlink, trioSylphieReach, trioErisReach)) {\n",
    "reach pose spring transform")
replace_once(
    "    private fun scheduleTrioCharacterBeat() {\n",
    '''    private fun installTrioAlternateReachLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioSylphieReach != null) return
        fun pose(resource: Int, character: Int) = ImageView(this).apply {
            setImageResource(resource)
            tag = character
            scaleType = ImageView.ScaleType.CENTER_CROP
            alpha = 0f
            isClickable = false
            isFocusable = false
        }
        val sylphie = pose(R.drawable.trio_sylphie_reach, 1)
        val eris = pose(R.drawable.trio_eris_reach, 2)
        host.addView(sylphie, 6, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(eris, 7, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSylphieReach = sylphie
        trioErisReach = eris
        updateTrioSceneFraming()
    }

    private fun scheduleTrioCharacterBeat() {
''',
    "alternate reach views")
replace_once(
    "        for (pose in arrayOf(trioSylphieBlink, trioErisBlink)) {\n",
    "        for (pose in arrayOf(trioSylphieBlink, trioErisBlink,\n"
    "            trioSylphieReach, trioErisReach)) {\n",
    "scene beat pose cleanup")
replace_once(
    '''                // Eyes briefly close before the icon and artwork light respond.
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
                TrioReachMotion.beat.intValue++
''',
    '''                // Blink, move the arm or sword, then lift the real app icon
                // as the character reaches it. Each pose releases as it lands.
                val expression = if (character == 1) trioSylphieBlink else trioErisBlink
                expression?.let { pose ->
                    pose.animate().cancel()
                    pose.animate().alpha(1f).setDuration(90L).withEndAction {
                        pose.postDelayed({
                            if (trioActive && trioSceneIndex == character)
                                pose.animate().alpha(0f).setDuration(120L).start()
                            else pose.alpha = 0f
                        }, 80L)
                    }.start()
                }
                val reaching = if (character == 1) trioSylphieReach else trioErisReach
                reaching?.let { pose ->
                    pose.postDelayed({
                        if (trioActive && trioSceneIndex == character) {
                            pose.animate().cancel()
                            pose.animate().alpha(1f).setDuration(if (character == 1) 220L else 170L)
                                .setInterpolator(DecelerateInterpolator(1.5f)).withEndAction {
                                    pose.postDelayed({
                                        if (trioActive && trioSceneIndex == character)
                                            pose.animate().alpha(0f)
                                                .setDuration(if (character == 1) 260L else 210L)
                                                .start()
                                        else pose.alpha = 0f
                                    }, if (character == 1) 720L else 300L)
                                }.start()
                        }
                    }, if (character == 1) 280L else 260L)
                }
                host.postDelayed({
                    if (trioActive && trioSceneIndex == character) {
                        trioArtworkFx?.pulse()
                        TrioReachMotion.beat.intValue++
                    }
                }, if (character == 1) 430L else 340L)
''',
    "Sylphie and Eris pose choreography")
replace_once(
    "        host.addView(fx, 6, ViewGroup.LayoutParams(\n",
    "        host.addView(fx, 8, ViewGroup.LayoutParams(\n",
    "artwork FX above reach poses")
replace_once(
    "        trioErisBlink?.animate()?.cancel(); trioErisBlink?.alpha = 0f\n",
    "        trioErisBlink?.animate()?.cancel(); trioErisBlink?.alpha = 0f\n"
    "        trioSylphieReach?.animate()?.cancel(); trioSylphieReach?.alpha = 0f\n"
    "        trioErisReach?.animate()?.cancel(); trioErisReach?.alpha = 0f\n",
    "stop reach poses")
replace_once(
    "        trioSylphieBlink?.animate()?.cancel(); trioErisBlink?.animate()?.cancel()\n",
    "        trioSylphieBlink?.animate()?.cancel(); trioErisBlink?.animate()?.cancel()\n"
    "        trioSylphieReach?.animate()?.cancel(); trioErisReach?.animate()?.cancel()\n",
    "destroy reach pose animations")
replace_once(
    "        trioSylphieBlink = null; trioErisBlink = null\n",
    "        trioSylphieBlink = null; trioErisBlink = null\n"
    "        trioSylphieReach = null; trioErisReach = null\n",
    "destroy reach pose state")

main.write_text(s)
print("Added Sylphie and Eris motion poses staged with live app icons")
