#!/usr/bin/env python3
"""Add a short Roxy expression beat over the existing native character spring."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_roxy_expression.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    "        installTrioContrastScrim()\n",
    "        installTrioContrastScrim()\n        installTrioRoxyExpressionLayer()\n",
    "Trio layer setup")
replace_once(
    "    private var trioSceneIndex = 0\n",
    "    private var trioSceneIndex = 0\n"
    "    private var trioRoxyExpression: ImageView? = null\n"
    "    private var trioExpressionRunnable: Runnable? = null\n",
    "scene state")
replace_once(
    "        trioManaView?.setCharacter(trioSceneIndex)\n",
    "        trioManaView?.setCharacter(trioSceneIndex)\n"
    "        scheduleTrioExpression()\n",
    "scene switch")
replace_once(
    "        apply(trioSceneBack)\n    }\n",
    "        apply(trioSceneBack)\n"
    "        trioRoxyExpression?.let { it.pivotX = it.width * .5f; it.pivotY = it.height * (if (cover) .30f else .40f) }\n"
    "    }\n",
    "Roxy framing")
replace_once(
    "                host.postDelayed(this, 32L)\n",
    '''                // The expression pose follows exactly the same view transform;
                // it does not shift app icons or form a separate touch surface.
                trioRoxyExpression?.let { expression ->
                    expression.translationX = trioMotionX
                    expression.translationY = trioMotionY
                    expression.rotation = rotation
                    expression.scaleX = breathe
                    expression.scaleY = breathe
                }
                host.postDelayed(this, 32L)
''', "idle scene transform")
replace_once(
    "    private fun installTrioManaLayer() {\n",
    '''    private fun installTrioRoxyExpressionLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioRoxyExpression != null) return
        val expression = ImageView(this).apply {
            setImageResource(R.drawable.trio_roxy_sneeze)
            scaleType = ImageView.ScaleType.FIT_CENTER
            alpha = 0f
            isClickable = false
            isFocusable = false
        }
        // Art 0–1, expression 2, mana 3, top scrim 4, Compose above all.
        host.addView(expression, 2, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioRoxyExpression = expression
        updateTrioSceneFraming()
        scheduleTrioExpression()
    }

    private fun scheduleTrioExpression() {
        val host = findViewById<View>(android.R.id.content) ?: return
        trioExpressionRunnable?.let(host::removeCallbacks)
        val expression = trioRoxyExpression ?: return
        expression.animate().cancel()
        expression.alpha = 0f
        if (!trioActive || trioSceneIndex != 0) return
        val task = object : Runnable {
            override fun run() {
                if (!trioActive || trioSceneIndex != 0) return
                expression.animate().alpha(1f).setDuration(130L).withEndAction {
                    expression.postDelayed({
                        if (trioActive && trioSceneIndex == 0)
                            expression.animate().alpha(0f).setDuration(240L).start()
                        else expression.alpha = 0f
                    }, 230L)
                }.start()
                host.postDelayed(this, 7400L)
            }
        }
        trioExpressionRunnable = task
        host.postDelayed(task, 3500L)
    }

    private fun installTrioManaLayer() {
''', "expression methods")
replace_once(
    "        scheduleTrioIdleMotion()\n",
    "        scheduleTrioIdleMotion()\n        scheduleTrioExpression()\n",
    "start lifecycle")
replace_once(
    "        trioIdleRunnable?.let { host?.removeCallbacks(it) }\n",
    "        trioIdleRunnable?.let { host?.removeCallbacks(it) }\n"
    "        trioExpressionRunnable?.let { host?.removeCallbacks(it) }\n"
    "        trioRoxyExpression?.animate()?.cancel()\n"
    "        trioRoxyExpression?.alpha = 0f\n",
    "stop lifecycle")
replace_once(
    "        trioIdleRunnable = null; trioSceneFront = null; trioSceneBack = null; trioManaView = null\n",
    "        trioExpressionRunnable?.let { findViewById<View>(android.R.id.content)?.removeCallbacks(it) }\n"
    "        trioRoxyExpression?.animate()?.cancel()\n"
    "        trioExpressionRunnable = null; trioRoxyExpression = null\n"
    "        trioIdleRunnable = null; trioSceneFront = null; trioSceneBack = null; trioManaView = null\n",
    "destroy lifecycle")

main.write_text(s)
print("Added native Roxy expression beat with matched scene transform and lifecycle")
