#!/usr/bin/env python3
"""Stage Roxy's hand, icon, and crystal as one reach and release."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_reach_choreography.py <duo-source-root>")

main = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
s = main.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    s = s.replace(old, new, 1)

replace_once(
    "                    pose.translationX = trioMotionX + entering * 9f\n"
    "                    pose.translationY = trioMotionY + entering * 4f\n",
    "                    pose.translationX = trioMotionX + entering * 16f\n"
    "                    pose.translationY = trioMotionY + entering * 7f\n",
    "reach artwork glide")
replace_once(
    '''                    TrioReachMotion.beat.intValue++
                    trioArtworkFx?.pulse()
                    reach.animate().alpha(1f).setDuration(190L).withEndAction {
                        reach.postDelayed({
                            if (trioActive && trioSceneIndex == 0)
                                reach.animate().alpha(0f).setDuration(290L).start()
                            else reach.alpha = 0f
                        }, 690L)
                    }.start()
''',
    '''                    // Hand first, icon and crystal on contact, then the pose
                    // releases as the real icon finishes its 850 ms landing arc.
                    reach.postDelayed({
                        if (trioActive && trioSceneIndex == 0) {
                            TrioReachMotion.beat.intValue++
                            trioArtworkFx?.pulse()
                        }
                    }, 170L)
                    reach.animate().alpha(1f).setDuration(240L)
                        .setInterpolator(DecelerateInterpolator(1.6f)).withEndAction {
                            reach.postDelayed({
                                if (trioActive && trioSceneIndex == 0)
                                    reach.animate().alpha(0f).setDuration(310L)
                                        .setInterpolator(DecelerateInterpolator(1.3f)).start()
                                else reach.alpha = 0f
                            }, 780L)
                        }.start()
''',
    "reach and icon timing")

main.write_text(s)
print("Staged Roxy reach, icon lift, and crystal pulse as one action")
