#!/usr/bin/env python3
"""Keep white status and widget text legible across bright Trio scenes."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_readability.py <duo-source-root>")

root = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher"

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text()
    if source.count(old) != 1:
        raise SystemExit(f"Expected {label} changed; refusing unsafe patch")
    path.write_text(source.replace(old, new, 1))

main = root / "MainActivity.kt"
replace_once(main,
    "        installTrioManaLayer()\n",
    "        installTrioManaLayer()\n        installTrioContrastScrim()\n",
    "Trio layer startup")
replace_once(main,
    "    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {\n",
    '''    private fun installTrioContrastScrim() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        // Behind Compose and above the illustration. This View consumes no touch
        // events and gives Android's white system status icons a stable backing.
        val scrim = View(this).apply {
            background = android.graphics.drawable.GradientDrawable(
                android.graphics.drawable.GradientDrawable.Orientation.TOP_BOTTOM,
                intArrayOf(Color.argb(190, 8, 12, 20), Color.TRANSPARENT))
            isClickable = false
            isFocusable = false
        }
        val height = (90f * resources.displayMetrics.density).toInt()
        host.addView(scrim, 3, android.widget.FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, height, android.view.Gravity.TOP))
    }

    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {
''', "Trio touch dispatch")

launcher = root / "LauncherScreen.kt"
replace_once(launcher,
    "        color = Glass.copy(alpha = .24f), shape = RoundedCornerShape(24.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(alpha = .18f))) {",
    "        color = Color(0xFF101821).copy(alpha = .68f), shape = RoundedCornerShape(24.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(alpha = .18f))) {",
    "widget glass backing")

rail = root / "StatusRail.kt"
replace_once(rail, "import androidx.compose.foundation.Canvas\n",
    "import androidx.compose.foundation.Canvas\nimport androidx.compose.foundation.background\nimport androidx.compose.foundation.shape.RoundedCornerShape\nimport androidx.compose.ui.draw.clip\n",
    "status rail imports")
replace_once(rail,
    '    BoxWithConstraints(modifier.testTag("status-rail").semantics(mergeDescendants = true) { contentDescription = description }) {',
    '    BoxWithConstraints(modifier.clip(RoundedCornerShape(18.dp))\n'
    '        .background(Color(0xFF101821).copy(alpha = .76f))\n'
    '        .padding(horizontal = 4.dp, vertical = 4.dp)\n'
    '        .testTag("status-rail").semantics(mergeDescendants = true) { contentDescription = description }) {',
    "status rail contrast backing")

print("Added dark backing for Trio clock, status rail, and system status bar")
