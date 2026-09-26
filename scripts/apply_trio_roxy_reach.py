#!/usr/bin/env python3
"""Alternate Roxy's blink with a short reach toward the launcher app grid."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_roxy_reach.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    "    private var trioRoxyExpression: ImageView? = null\n",
    "    private var trioRoxyExpression: ImageView? = null\n"
    "    private var trioRoxyReach: ImageView? = null\n"
    "    private var trioExpressionBeat = 0\n",
    "Roxy state")
replace_once(
    "        trioRoxyExpression?.let { it.pivotX = it.width * .5f; it.pivotY = it.height * (if (cover) .30f else .40f) }\n",
    "        trioRoxyExpression?.let { it.pivotX = it.width * .5f; it.pivotY = it.height * (if (cover) .30f else .40f) }\n"
    "        trioRoxyReach?.let { it.pivotX = it.width * .5f; it.pivotY = it.height * (if (cover) .30f else .40f) }\n",
    "Roxy pose framing")
replace_once(
    '''                trioRoxyExpression?.let { expression ->
                    expression.translationX = trioMotionX
                    expression.translationY = trioMotionY
                    expression.rotation = rotation
                    expression.scaleX = breathe
                    expression.scaleY = breathe
                }
''',
    '''                for (pose in arrayOf(trioRoxyExpression, trioRoxyReach)) {
                    pose ?: continue
                    pose.translationX = trioMotionX
                    pose.translationY = trioMotionY
                    pose.rotation = rotation
                    pose.scaleX = breathe
                    pose.scaleY = breathe
                }
''', "pose spring transform")
replace_once(
    "        trioRoxyExpression = expression\n        updateTrioSceneFraming()\n",
    '''        trioRoxyExpression = expression
        val reach = ImageView(this).apply {
            setImageResource(R.drawable.trio_roxy_reach)
            setBackgroundColor(Color.BLACK)
            scaleType = ImageView.ScaleType.FIT_CENTER
            alpha = 0f
            isClickable = false
            isFocusable = false
        }
        // The black backing hides the old hat hand during the reaching pose.
        // Both poses remain below the mana, scrim, and real Compose app controls.
        host.addView(reach, 3, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioRoxyReach = reach
        updateTrioSceneFraming()
''', "reach view setup")
replace_once(
    '''        val expression = trioRoxyExpression ?: return
        expression.animate().cancel()
        expression.alpha = 0f
        if (!trioActive || trioSceneIndex != 0) return
''',
    '''        val expression = trioRoxyExpression ?: return
        val reach = trioRoxyReach ?: return
        expression.animate().cancel()
        reach.animate().cancel()
        expression.alpha = 0f
        reach.alpha = 0f
        trioExpressionBeat = 0
        if (!trioActive || trioSceneIndex != 0) return
''', "pose schedule setup")
replace_once(
    '''                expression.animate().alpha(1f).setDuration(130L).withEndAction {
                    expression.postDelayed({
                        if (trioActive && trioSceneIndex == 0)
                            expression.animate().alpha(0f).setDuration(240L).start()
                        else expression.alpha = 0f
                    }, 230L)
                }.start()
''',
    '''                if (trioExpressionBeat++ % 2 == 0) {
                    expression.animate().alpha(1f).setDuration(130L).withEndAction {
                        expression.postDelayed({
                            if (trioActive && trioSceneIndex == 0)
                                expression.animate().alpha(0f).setDuration(240L).start()
                            else expression.alpha = 0f
                        }, 230L)
                    }.start()
                } else {
                    reach.animate().alpha(1f).setDuration(190L).withEndAction {
                        reach.postDelayed({
                            if (trioActive && trioSceneIndex == 0)
                                reach.animate().alpha(0f).setDuration(290L).start()
                            else reach.alpha = 0f
                        }, 690L)
                    }.start()
                }
''', "expression and reach timeline")
replace_once(
    "        trioRoxyExpression?.alpha = 0f\n",
    "        trioRoxyExpression?.alpha = 0f\n"
    "        trioRoxyReach?.animate()?.cancel()\n"
    "        trioRoxyReach?.alpha = 0f\n",
    "stop lifecycle")
replace_once(
    "        trioExpressionRunnable = null; trioRoxyExpression = null\n",
    "        trioRoxyReach?.animate()?.cancel()\n"
    "        trioExpressionRunnable = null; trioRoxyExpression = null; trioRoxyReach = null\n",
    "destroy lifecycle")

main.write_text(s)
print("Added noninteractive Roxy reaching pose alternated with blink")
