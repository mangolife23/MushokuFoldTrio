#!/usr/bin/env python3
"""Give the portrait and icon response a less metronomic, softer cadence."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_natural_motion.py <duo-source-root>")

root = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher"

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text()
    if source.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    path.write_text(source.replace(old, new, 1))

main = root / "MainActivity.kt"
replace_once(main,
    "                val idleX = kotlin.math.sin(t * .52f + phase) * amplitude + trioTouchX\n"
    "                val idleY = kotlin.math.sin(t * .67f + 1.1f + phase) * (amplitude * .62f) + trioTouchY\n",
    "                // Two slow rhythms prevent a perfectly repeating pendulum path.\n"
    "                val idleX = (kotlin.math.sin(t * .52f + phase) +\n"
    "                    .31f * kotlin.math.sin(t * .19f + phase * .63f)) * amplitude + trioTouchX\n"
    "                val idleY = (kotlin.math.sin(t * .67f + 1.1f + phase) * .62f +\n"
    "                    .18f * kotlin.math.sin(t * .27f + phase * 1.4f)) * amplitude + trioTouchY\n",
    "portrait idle rhythm")
replace_once(main,
    "                val breathe = 1f + overscan + kotlin.math.sin(t * .82f + phase) * .008f\n",
    "                val breathe = 1f + overscan + kotlin.math.sin(t * .82f + phase) * .007f +\n"
    "                    kotlin.math.sin(t * 1.64f + phase + .6f) * .002f\n",
    "breathing rhythm")
replace_once(main,
    "                for (pose in arrayOf(trioRoxyExpression, trioRoxyReach)) {\n"
    "                    pose ?: continue\n"
    "                    pose.translationX = trioMotionX\n"
    "                    pose.translationY = trioMotionY\n",
    "                for (pose in arrayOf(trioRoxyExpression, trioRoxyReach)) {\n"
    "                    pose ?: continue\n"
    "                    // The reach glides into the held silhouette as its alpha rises.\n"
    "                    val entering = if (pose === trioRoxyReach) (1f - pose.alpha) else 0f\n"
    "                    pose.translationX = trioMotionX + entering * 9f\n"
    "                    pose.translationY = trioMotionY + entering * 4f\n",
    "reach anticipation")
replace_once(main,
    "                host.postDelayed(this, 7400L)\n",
    "                // Two quick reactions and two quieter pauses within Roxy's scene.\n"
    "                val gaps = longArrayOf(5700L, 7900L, 6400L, 9000L)\n"
    "                host.postDelayed(this, gaps[(trioExpressionBeat - 1) % gaps.size])\n",
    "variable reaction timing")
replace_once(main,
    "        host.postDelayed(task, 3500L)\n",
    "        host.postDelayed(task, 3100L)\n",
    "first reaction timing")

screen = root / "LauncherScreen.kt"
replace_once(screen,
    "    val density = LocalDensity.current\n"
    "    LaunchedEffect(reachBeat) {\n",
    "    val density = LocalDensity.current\n"
    "    val liftDistance = with(density) { 18.dp.toPx() }\n"
    "    LaunchedEffect(reachBeat) {\n",
    "icon animation distance")
replace_once(screen,
    "            lift.animateTo(with(density) { (-18).dp.toPx() }, tween(210, easing = FastOutSlowInEasing))\n"
    "            lift.animateTo(with(density) { 4.dp.toPx() }, tween(300, easing = FastOutSlowInEasing))\n"
    "            lift.animateTo(0f, tween(220, easing = FastOutSlowInEasing))\n",
    "            lift.animateTo(-liftDistance, tween(250, easing = FastOutSlowInEasing))\n"
    "            lift.animateTo(with(density) { 3.dp.toPx() }, tween(340, easing = FastOutSlowInEasing))\n"
    "            lift.animateTo(0f, tween(260, easing = FastOutSlowInEasing))\n",
    "icon lift and settle")
replace_once(screen,
    "            .graphicsLayer { scaleX = scale; scaleY = scale; translationY = lift.value }.clip(RoundedCornerShape((size * .24f).dp)))\n",
    "            .graphicsLayer {\n"
    "                val rise = (-lift.value / liftDistance).coerceIn(0f, 1f)\n"
    "                scaleX = scale * (1f + rise * .055f)\n"
    "                scaleY = scale * (1f + rise * .055f)\n"
    "                translationY = lift.value\n"
    "                translationX = lift.value * .32f\n"
    "                rotationZ = rise * -5f\n"
    "            }.clip(RoundedCornerShape((size * .24f).dp)))\n",
    "icon arc and tilt")

print("Added compound breathing, varied pose timing, and an icon arc")
