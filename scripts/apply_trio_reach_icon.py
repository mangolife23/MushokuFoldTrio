#!/usr/bin/env python3
"""Synchronize one real home icon with Roxy's reaching animation."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_reach_icon.py <duo-source-root>")

root = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher"

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text()
    if source.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    path.write_text(source.replace(old, new, 1))

main = root / "MainActivity.kt"
replace_once(main,
    "                } else {\n                    reach.animate().alpha(1f).setDuration(190L).withEndAction {\n",
    "                } else {\n                    TrioReachMotion.beat.intValue++\n                    reach.animate().alpha(1f).setDuration(190L).withEndAction {\n",
    "reach beat")

screen = root / "LauncherScreen.kt"
replace_once(screen,
    "import androidx.compose.animation.core.animateFloatAsState\n",
    "import androidx.compose.animation.core.Animatable\n"
    "import androidx.compose.animation.core.FastOutSlowInEasing\n"
    "import androidx.compose.animation.core.tween\n"
    "import androidx.compose.animation.core.animateFloatAsState\n",
    "animation imports")
replace_once(screen,
    "internal val Ink: Color\n",
    "// MainActivity advances this on the reach beat; visible home icons observe it.\n"
    "internal object TrioReachMotion { val beat = mutableIntStateOf(0) }\n\n"
    "internal val Ink: Color\n",
    "shared reach beat")
replace_once(screen,
    "                    if (visible) AppTile(app, iconSize, labels,\n                        onClick = { onLaunch(app, it) }, onLongClick = { onActions(app) })\n",
    "                    if (visible) AppTile(app, iconSize, labels,\n"
    "                        reachBeat = if (id == ids.firstOrNull() && !drag.active) TrioReachMotion.beat.intValue else 0,\n"
    "                        onClick = { onLaunch(app, it) }, onLongClick = { onActions(app) })\n",
    "home app beat")
replace_once(screen,
    "private fun AppTile(app: AppEntry, size: Float, labels: Boolean, modifier: Modifier = Modifier, onClick: (android.graphics.Rect) -> Unit, onLongClick: () -> Unit) {\n",
    "private fun AppTile(app: AppEntry, size: Float, labels: Boolean, modifier: Modifier = Modifier, reachBeat: Int = 0, onClick: (android.graphics.Rect) -> Unit, onLongClick: () -> Unit) {\n"
    "    val lift = remember { Animatable(0f) }\n"
    "    var lastBeat by remember { mutableIntStateOf(reachBeat) }\n"
    "    val density = LocalDensity.current\n"
    "    LaunchedEffect(reachBeat) {\n"
    "        if (reachBeat > lastBeat) {\n"
    "            lastBeat = reachBeat\n"
    "            lift.snapTo(0f)\n"
    "            lift.animateTo(with(density) { (-18).dp.toPx() }, tween(210, easing = FastOutSlowInEasing))\n"
    "            lift.animateTo(with(density) { 4.dp.toPx() }, tween(300, easing = FastOutSlowInEasing))\n"
    "            lift.animateTo(0f, tween(220, easing = FastOutSlowInEasing))\n"
    "        } else lastBeat = reachBeat\n"
    "    }\n",
    "icon lift")
replace_once(screen,
    "            .graphicsLayer { scaleX = scale; scaleY = scale }.clip(RoundedCornerShape((size * .24f).dp)))\n",
    "            .graphicsLayer { scaleX = scale; scaleY = scale; translationY = lift.value }.clip(RoundedCornerShape((size * .24f).dp)))\n",
    "icon drawing transform")

print("Added reach-synchronized lift to the first real home app icon")
