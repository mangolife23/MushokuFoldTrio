#!/usr/bin/env python3
"""Synchronize Sylphie and Eris artwork beats with real home app icons."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_sylphie_eris_beats.py <duo-source-root>")

root = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher"

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text()
    if source.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    path.write_text(source.replace(old, new, 1))

main = root / "MainActivity.kt"
replace_once(main,
    "    private var trioExpressionRunnable: Runnable? = null\n",
    "    private var trioExpressionRunnable: Runnable? = null\n"
    "    private var trioCharacterBeatRunnable: Runnable? = null\n",
    "character beat state")
replace_once(main,
    "        trioSceneFront = newFront; trioSceneBack = oldFront; trioSceneIndex = index % 3\n",
    "        trioSceneFront = newFront; trioSceneBack = oldFront; trioSceneIndex = index % 3\n"
    "        TrioReachMotion.scene.intValue = trioSceneIndex\n",
    "current icon motion scene")
replace_once(main,
    "        scheduleTrioExpression()\n    }\n\n    private fun scheduleTrioScene() {\n",
    "        scheduleTrioExpression()\n"
    "        scheduleTrioCharacterBeat()\n"
    "    }\n\n    private fun scheduleTrioScene() {\n",
    "scene switch beat scheduling")
replace_once(main,
    "    private fun installTrioManaLayer() {\n",
    '''    private fun scheduleTrioCharacterBeat() {
        val host = findViewById<View>(android.R.id.content) ?: return
        trioCharacterBeatRunnable?.let(host::removeCallbacks)
        trioCharacterBeatRunnable = null
        val character = trioSceneIndex
        if (!trioActive || character == 0) return
        var count = 0
        val intervals = if (character == 1) longArrayOf(7700L, 8400L, 9000L)
            else longArrayOf(8100L, 7500L, 8600L)
        val task = object : Runnable {
            override fun run() {
                if (!trioActive || trioSceneIndex != character) return
                // The artwork effect and the real home icon react together.
                trioArtworkFx?.pulse()
                TrioReachMotion.beat.intValue++
                host.postDelayed(this, intervals[count++ % intervals.size])
            }
        }
        trioCharacterBeatRunnable = task
        host.postDelayed(task, if (character == 1) 4400L else 5100L)
    }

    private fun installTrioManaLayer() {
''',
    "Sylphie and Eris scene beats")
replace_once(main,
    "        scheduleTrioExpression()\n        if (!timeReceiverRegistered) {\n",
    "        scheduleTrioExpression()\n"
    "        scheduleTrioCharacterBeat()\n"
    "        if (!timeReceiverRegistered) {\n",
    "start beat scheduling")
replace_once(main,
    "        trioExpressionRunnable?.let { host?.removeCallbacks(it) }\n",
    "        trioExpressionRunnable?.let { host?.removeCallbacks(it) }\n"
    "        trioCharacterBeatRunnable?.let { host?.removeCallbacks(it) }\n",
    "stop beat scheduling")
replace_once(main,
    "        trioExpressionRunnable?.let { findViewById<View>(android.R.id.content)?.removeCallbacks(it) }\n",
    "        trioExpressionRunnable?.let { findViewById<View>(android.R.id.content)?.removeCallbacks(it) }\n"
    "        trioCharacterBeatRunnable?.let { findViewById<View>(android.R.id.content)?.removeCallbacks(it) }\n"
    "        trioCharacterBeatRunnable = null\n",
    "destroy beat scheduling")

screen = root / "LauncherScreen.kt"
replace_once(screen,
    "internal object TrioReachMotion { val beat = mutableIntStateOf(0) }\n",
    "internal object TrioReachMotion {\n"
    "    val beat = mutableIntStateOf(0)\n"
    "    val scene = mutableIntStateOf(0)\n"
    "}\n",
    "icon motion scene state")
replace_once(screen,
    "                        reachBeat = if (id == ids.firstOrNull() && !drag.active) TrioReachMotion.beat.intValue else 0,\n",
    "                        reachBeat = if (id == ids.firstOrNull()) TrioReachMotion.beat.intValue else 0,\n"
    "                        motionKind = TrioReachMotion.scene.intValue, motionEnabled = !drag.active,\n",
    "home app motion style")
replace_once(screen,
    "private fun AppTile(app: AppEntry, size: Float, labels: Boolean, modifier: Modifier = Modifier, reachBeat: Int = 0, onClick: (android.graphics.Rect) -> Unit, onLongClick: () -> Unit) {\n",
    "private fun AppTile(app: AppEntry, size: Float, labels: Boolean, modifier: Modifier = Modifier, reachBeat: Int = 0, motionKind: Int = 0, motionEnabled: Boolean = true, onClick: (android.graphics.Rect) -> Unit, onLongClick: () -> Unit) {\n",
    "AppTile character parameter")
replace_once(screen,
    '''    val liftDistance = with(density) { 18.dp.toPx() }
    LaunchedEffect(reachBeat) {
        if (reachBeat > lastBeat) {
            lastBeat = reachBeat
            lift.snapTo(0f)
            lift.animateTo(-liftDistance, tween(250, easing = FastOutSlowInEasing))
            lift.animateTo(with(density) { 3.dp.toPx() }, tween(340, easing = FastOutSlowInEasing))
            lift.animateTo(0f, tween(260, easing = FastOutSlowInEasing))
        } else lastBeat = reachBeat
    }
''',
    '''    val liftDistance = with(density) { (when (motionKind) { 1 -> 14; 2 -> 10; else -> 18 }).dp.toPx() }
    LaunchedEffect(reachBeat, motionKind, motionEnabled) {
        if (!motionEnabled) { lift.snapTo(0f); lastBeat = reachBeat }
        else if (reachBeat > lastBeat) {
            lastBeat = reachBeat
            lift.snapTo(0f)
            when (motionKind) {
                1 -> { // Sylphie's orb draws the icon gently upward.
                    lift.animateTo(-liftDistance, tween(340, easing = FastOutSlowInEasing))
                    lift.animateTo(with(density) { 2.dp.toPx() }, tween(410, easing = FastOutSlowInEasing))
                    lift.animateTo(0f, tween(300, easing = FastOutSlowInEasing))
                }
                2 -> { // Eris's sword gives it a quick nudge and rebound.
                    lift.animateTo(-liftDistance, tween(150, easing = FastOutSlowInEasing))
                    lift.animateTo(with(density) { 5.dp.toPx() }, tween(240, easing = FastOutSlowInEasing))
                    lift.animateTo(0f, tween(210, easing = FastOutSlowInEasing))
                }
                else -> {
                    lift.animateTo(-liftDistance, tween(250, easing = FastOutSlowInEasing))
                    lift.animateTo(with(density) { 3.dp.toPx() }, tween(340, easing = FastOutSlowInEasing))
                    lift.animateTo(0f, tween(260, easing = FastOutSlowInEasing))
                }
            }
        } else lastBeat = reachBeat
    }
''',
    "distinct icon trajectories")
replace_once(screen,
    '''                scaleX = scale * (1f + rise * .055f)
                scaleY = scale * (1f + rise * .055f)
                translationY = lift.value
                translationX = lift.value * .32f
                rotationZ = rise * -5f
''',
    '''                val sizeGain = when (motionKind) { 1 -> .035f; 2 -> .045f; else -> .055f }
                scaleX = scale * (1f + rise * sizeGain)
                scaleY = scale * (1f + rise * sizeGain)
                translationY = lift.value
                translationX = lift.value * when (motionKind) { 1 -> .58f; 2 -> -.68f; else -> .32f }
                rotationZ = rise * when (motionKind) { 1 -> -2f; 2 -> 7f; else -> -5f }
''',
    "distinct icon arcs")

print("Added separate Sylphie and Eris icon and artwork motion beats")
