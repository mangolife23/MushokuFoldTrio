#!/usr/bin/env python3
"""Show which Fold7 feed window precondition prevents connection."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_feed_bounds_diagnostics.py <duo-source-root>")

root = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher"

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text()
    if source.count(old) != 1:
        raise SystemExit(f"Pinned upstream {label} changed; refusing unsafe patch")
    path.write_text(source.replace(old, new, 1))

replace_once(root / "DiscoverBounds.kt",
    "    fun resetViewport() { measuredViewport = null }\n",
    "    fun resetViewport() { measuredViewport = null }\n"
    '    fun viewportSize(): String = measuredViewport?.let { "${it.width()}x${it.height()}" } ?: "unset"\n',
    "feed viewport state")

replace_once(root / "DiscoverActivity.kt",
    '            else message.value = "Discover couldn\'t fit beside the dock. Return home and try again."\n',
    '''            else {
                val embedded = ActivityEmbeddingController.getInstance(this).isActivityEmbedded(this)
                message.value = "Discover window unavailable (embedded=$embedded, actual=${decor.width}x${decor.height}, expected=${DiscoverBounds.viewportSize()}). Return home and retry."
            }
''', "feed activity recovery")

replace_once(root / "LiveDiscoverActivity.kt",
    '            else LiveDiscover.message.value = "Discover couldn\'t fit beside the dock."\n',
    '''            else {
                val embedded = ActivityEmbeddingController.getInstance(this).isActivityEmbedded(this)
                LiveDiscover.message.value = "Discover window unavailable (embedded=$embedded, actual=${decor.width}x${decor.height}, expected=${DiscoverBounds.viewportSize()})."
            }
''', "live feed recovery")

print("Added Fold7 feed embedding and viewport diagnostics")
