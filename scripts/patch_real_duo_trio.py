#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch_real_duo_trio.py <duo-source-root>")

root = Path(sys.argv[1])
main = root / "app/src/main/java/com/jake/duolauncher/MainActivity.kt"
m = main.read_text()

old_import = "import android.widget.Toast\n"
new_import = """import android.widget.Toast
import android.widget.ImageView
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.ViewTreeObserver
import android.view.animation.DecelerateInterpolator
"""

old_attach = """        FoldRenderExperiment.attach(this)
        // Reassert the token after recreation"""
new_attach = """        installTrioViewportTransitionProbe()
        installTrioSceneLayer()
        installTrioManaLayer()
        // Reassert the token after recreation"""

old_marker = """    override fun onStart() {
"""
new_marker = """    private var trioLastViewportWidth = 0
    private var trioRevealRunning = false
    private var trioLayoutListener: ViewTreeObserver.OnGlobalLayoutListener? = null
    private var trioManaView: TrioManaView? = null
    private var trioSceneFront: ImageView? = null
    private var trioSceneBack: ImageView? = null
    private var trioSceneIndex = 0
    private var trioSceneRunnable: Runnable? = null
    private data class TrioBurst(val x: Float, val y: Float, val born: Long, val seed: Int)

    private fun installTrioViewportTransitionProbe() {
        val root = window.decorView
        val listener = ViewTreeObserver.OnGlobalLayoutListener {
            val width = root.width
            if (width <= 0) return@OnGlobalLayoutListener
            val previous = trioLastViewportWidth
            trioLastViewportWidth = width
            if (previous <= 0 || trioRevealRunning) return@OnGlobalLayoutListener
            val density = resources.displayMetrics.density.coerceAtLeast(1f)
            val previousDp = previous / density
            val currentDp = width / density
            // Hardware-validated Fold7 detector from the preserved Build #15 baseline.
            if (previousDp < 650f && currentDp >= 650f && width >= previous * 1.35f) {
                root.post {
                    root.postDelayed({
                        playTrioLiveLauncherReveal()
                        trioManaView?.unfoldBurst()
                    }, 180L)
                }
            }
        }
        trioLayoutListener = listener
        root.viewTreeObserver.addOnGlobalLayoutListener(listener)
    }

    private fun installTrioSceneLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioSceneFront != null) return
        fun sceneView() = ImageView(this).apply {
            scaleType = ImageView.ScaleType.CENTER_CROP
            isClickable = false
            isFocusable = false
            alpha = 0f
            scaleX = 1.035f
            scaleY = 1.035f
        }
        val back = sceneView()
        val front = sceneView()
        host.addView(back, 0, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(front, 1, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSceneBack = back
        trioSceneFront = front
        showTrioScene(0, false)
        scheduleTrioScene()
    }

    private fun trioSceneResource(index: Int): Int {
        val names = arrayOf("trio_roxy", "trio_sylphie", "trio_eris")
        return resources.getIdentifier(names[index % names.size], "drawable", packageName)
    }

    private fun showTrioScene(index: Int, animate: Boolean) {
        val front = trioSceneFront ?: return
        val back = trioSceneBack ?: return
        val res = trioSceneResource(index)
        if (res == 0) return
        val oldFront = front
        val newFront = back
        newFront.setImageResource(res)
        newFront.alpha = if (animate) 0f else 0.50f
        newFront.scaleX = 1.045f
        newFront.scaleY = 1.045f
        newFront.animate().cancel()
        oldFront.animate().cancel()
        if (animate) {
            newFront.animate().alpha(0.50f).scaleX(1.015f).scaleY(1.015f).setDuration(1800L).start()
            oldFront.animate().alpha(0f).setDuration(1800L).start()
        } else {
            newFront.scaleX = 1.015f
            newFront.scaleY = 1.015f
            oldFront.alpha = 0f
        }
        trioSceneFront = newFront
        trioSceneBack = oldFront
        trioSceneIndex = index % 3
        trioManaView?.setCharacter(trioSceneIndex)
    }

    private fun scheduleTrioScene() {
        val host = findViewById<View>(android.R.id.content) ?: return
        trioSceneRunnable?.let(host::removeCallbacks)
        val task = object : Runnable {
            override fun run() {
                showTrioScene((trioSceneIndex + 1) % 3, true)
                host.postDelayed(this, 30000L)
            }
        }
        trioSceneRunnable = task
        host.postDelayed(task, 30000L)
    }

    private fun installTrioManaLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioManaView != null) return
        val mana = TrioManaView()
        mana.isClickable = false
        mana.isFocusable = false
        host.addView(mana, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        ))
        trioManaView = mana
    }

    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {
        if (ev.actionMasked == MotionEvent.ACTION_DOWN || ev.actionMasked == MotionEvent.ACTION_MOVE)
            trioManaView?.manaTouch(ev.x, ev.y, ev.eventTime)
        return super.dispatchTouchEvent(ev)
    }

    private inner class TrioManaView : View(this) {
        private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
        private val bursts = ArrayDeque<TrioBurst>()
        private var lastTouchBurst = 0L
        private var unfoldBorn = 0L
        private var character = 0

        fun setCharacter(value: Int) { character = value % 3; invalidate() }

        fun manaTouch(x: Float, y: Float, now: Long) {
            if (now - lastTouchBurst < 42L) return
            lastTouchBurst = now
            bursts.addLast(TrioBurst(x, y, now, (x.toInt() * 31 + y.toInt()) and 0x7fffffff))
            while (bursts.size > 12) bursts.removeFirst()
            postInvalidateOnAnimation()
        }

        fun unfoldBurst() {
            unfoldBorn = android.os.SystemClock.uptimeMillis()
            postInvalidateOnAnimation()
        }

        override fun onDraw(canvas: Canvas) {
            super.onDraw(canvas)
            val now = android.os.SystemClock.uptimeMillis()
            val w = width.toFloat().coerceAtLeast(1f)
            val h = height.toFloat().coerceAtLeast(1f)

            // Slow neutral mana field. Character-specific palettes will be selected by
            // the scene controller once curated adult artwork is added.
            repeat(16) { i ->
                val phase = ((now * (3L + i % 2) + i * 7919L) % 32000L) / 32000f
                val drift = kotlin.math.sin(phase * 6.283f + i * 0.7f) * 18f
                val x = ((i * 0.6180339f + 0.13f) % 1f) * w + drift
                val y = h - phase * (h + 120f)
                val r = 2.2f + (i % 4) * 1.2f
                paint.style = Paint.Style.FILL
                val rgb = when (character) { 1 -> intArrayOf(214, 255, 226); 2 -> intArrayOf(255, 126, 72); else -> intArrayOf(164, 226, 255) }
                paint.color = Color.argb(82, rgb[0], rgb[1], rgb[2])
                canvas.drawCircle(x, y, r, paint)
                paint.style = Paint.Style.STROKE
                paint.strokeWidth = 1.2f
                paint.color = Color.argb(46, rgb[0], rgb[1], rgb[2])
                canvas.drawCircle(x, y, r + 3.2f, paint)
            }

            val expired = ArrayList<TrioBurst>()
            for (b in bursts) {
                val age = (now - b.born).coerceAtLeast(0L)
                if (age > 900L) { expired.add(b); continue }
                val t = age / 900f
                val alpha = ((1f - t) * 205).toInt()
                paint.style = Paint.Style.STROKE
                paint.strokeWidth = 2.4f + (1f - t) * 3f
                val burstRgb = when (character) { 1 -> intArrayOf(196, 255, 214); 2 -> intArrayOf(255, 102, 48); else -> intArrayOf(142, 226, 255) }
                paint.color = Color.argb(alpha, burstRgb[0], burstRgb[1], burstRgb[2])
                canvas.drawCircle(b.x, b.y, 12f + t * 98f, paint)
                repeat(8) { j ->
                    val angle = j * 0.785398f + t * 2.4f + (b.seed % 17) * 0.05f
                    val radius = 10f + t * (44f + (j % 3) * 11f)
                    val px = b.x + kotlin.math.cos(angle) * radius
                    val py = b.y + kotlin.math.sin(angle) * radius - t * 24f
                    paint.style = Paint.Style.FILL
                    paint.color = Color.argb((alpha * 0.86f).toInt(), burstRgb[0], burstRgb[1], burstRgb[2])
                    canvas.drawCircle(px, py, 2.3f + (j % 3), paint)
                }
            }
            expired.forEach { bursts.remove(it) }

            if (unfoldBorn > 0L) {
                val age = now - unfoldBorn
                if (age < 950L) {
                    val t = age / 950f
                    repeat(2) { ring ->
                        paint.style = Paint.Style.STROKE
                        paint.strokeWidth = (6f - ring * 2f) * (1f - t) + 1f
                        paint.color = Color.argb(((1f - t) * (145 - ring * 35)).toInt(), 160, 230, 255)
                        canvas.drawCircle(w / 2f, h / 2f, 36f + ring * 28f + t * kotlin.math.max(w, h) * (0.56f + ring * 0.06f), paint)
                    }
                } else unfoldBorn = 0L
            }
            if (bursts.isNotEmpty() || unfoldBorn > 0L || isShown) postInvalidateOnAnimation()
        }
    }

    private fun playTrioLiveLauncherReveal() {
        if (trioRevealRunning || isFinishing || isDestroyed) return
        val content = findViewById<View>(android.R.id.content) ?: return
        if (content.width <= 0 || content.height <= 0) return
        trioRevealRunning = true
        content.animate().cancel()
        // Never scale the live root during Fold7 resize. Build #15 hardware feedback
        // established that waiting for layout settlement avoids the half-screen phase.
        content.scaleX = 1f
        content.scaleY = 1f
        content.alpha = 0.90f
        content.animate().alpha(1f)
            .setDuration(650L)
            .setInterpolator(DecelerateInterpolator(1.7f))
            .withEndAction {
                content.scaleX = 1f
                content.scaleY = 1f
                content.alpha = 1f
                trioRevealRunning = false
            }.start()
    }

    override fun onStart() {
"""

old_destroy = """    override fun onDestroy() {
        recreatingShadeSetup = isChangingConfigurations
"""
new_destroy = """    override fun onDestroy() {
        trioLayoutListener?.let { listener ->
            window.decorView.viewTreeObserver.takeIf { it.isAlive }?.removeOnGlobalLayoutListener(listener)
        }
        trioLayoutListener = null
        trioSceneRunnable?.let { findViewById<View>(android.R.id.content)?.removeCallbacks(it) }
        trioSceneRunnable = null
        trioSceneFront = null
        trioSceneBack = null
        trioManaView = null
        recreatingShadeSetup = isChangingConfigurations
"""

for old, new, label in (
    (old_import, new_import, "imports"),
    (old_attach, new_attach, "attachment"),
    (old_marker, new_marker, "Fold7/mana methods"),
    (old_destroy, new_destroy, "cleanup"),
):
    if m.count(old) != 1:
        raise SystemExit(f"Pinned upstream {label} block changed; refusing unsafe patch")
    m = m.replace(old, new, 1)

main.write_text(m)
print("Applied MushokuFoldTrio Fold7 detector and neutral interactive mana foundation")
