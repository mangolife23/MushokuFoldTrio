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
import android.graphics.Path
import android.graphics.RectF
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.ViewTreeObserver
import android.view.animation.DecelerateInterpolator
import kotlin.math.pow
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
    private var trioIdleRunnable: Runnable? = null
    private var trioTouchX = 0f
    private var trioTouchY = 0f
    private var trioTouchTargetX = 0f
    private var trioTouchTargetY = 0f
    private var trioMotionX = 0f
    private var trioMotionY = 0f
    private var trioVelocityX = 0f
    private var trioVelocityY = 0f
    private var trioActive = false
    private data class TrioBurst(val x: Float, val y: Float, val born: Long, val seed: Int)

    private fun installTrioViewportTransitionProbe() {
        val root = window.decorView
        val listener = ViewTreeObserver.OnGlobalLayoutListener {
            val width = root.width
            if (width <= 0) return@OnGlobalLayoutListener
            val previous = trioLastViewportWidth
            trioLastViewportWidth = width
            updateTrioSceneFraming()
            if (previous <= 0 || trioRevealRunning || !trioActive) return@OnGlobalLayoutListener
            val density = resources.displayMetrics.density.coerceAtLeast(1f)
            val previousDp = previous / density
            val currentDp = width / density
            if (previousDp < 650f && currentDp >= 650f && width >= previous * 1.35f) {
                root.post { root.postDelayed({ playTrioLiveLauncherReveal(); trioManaView?.unfoldBurst() }, 180L) }
            }
        }
        trioLayoutListener = listener
        root.viewTreeObserver.addOnGlobalLayoutListener(listener)
    }

    private fun installTrioSceneLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioSceneFront != null) return
        fun sceneView() = ImageView(this).apply {
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            adjustViewBounds = false
            setBackgroundColor(Color.BLACK)
            isClickable = false
            isFocusable = false
            alpha = 0f
            scaleX = 1f
            scaleY = 1f
        }
        val back = sceneView(); val front = sceneView()
        host.addView(back, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        host.addView(front, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        trioSceneBack = back; trioSceneFront = front
        showTrioScene(0, false); updateTrioSceneFraming()
    }

    private fun updateTrioSceneFraming() {
        val density = resources.displayMetrics.density.coerceAtLeast(1f)
        val widthDp = window.decorView.width / density
        // Cover screen: show the whole illustration instead of CENTER_CROP cutting off faces.
        // Unfolded screen: use a gentle fit while retaining the full character composition.
        val type = if (widthDp in 1f..649.99f) ImageView.ScaleType.CENTER_INSIDE else ImageView.ScaleType.FIT_CENTER
        trioSceneFront?.scaleType = type
        trioSceneBack?.scaleType = type
    }

    private fun trioSceneResource(index: Int): Int {
        val names = arrayOf("trio_roxy_cutout", "trio_sylphie", "trio_eris")
        return resources.getIdentifier(names[index % names.size], "drawable", packageName)
    }

    private fun showTrioScene(index: Int, animate: Boolean) {
        val front = trioSceneFront ?: return; val back = trioSceneBack ?: return
        val res = trioSceneResource(index); if (res == 0) return
        val oldFront = front; val newFront = back
        newFront.setImageResource(res)
        newFront.tag = index % 3
        newFront.alpha = if (animate) 0f else 1.0f
        // Keep the incoming art covered until the next idle frame takes over.
        newFront.scaleX = oldFront.scaleX; newFront.scaleY = oldFront.scaleY
        newFront.translationX = oldFront.translationX
        newFront.translationY = oldFront.translationY
        newFront.rotation = oldFront.rotation
        newFront.animate().cancel(); oldFront.animate().cancel()
        if (animate) {
            newFront.animate().alpha(1.0f).setDuration(1800L).start()
            oldFront.animate().alpha(0f).setDuration(1800L).start()
        } else { oldFront.alpha = 0f }
        trioSceneFront = newFront; trioSceneBack = oldFront; trioSceneIndex = index % 3
        updateTrioSceneFraming()
        trioManaView?.setCharacter(trioSceneIndex)
    }

    private fun scheduleTrioScene() {
        val host = findViewById<View>(android.R.id.content) ?: return
        trioSceneRunnable?.let(host::removeCallbacks)
        val task = object : Runnable { override fun run() { showTrioScene((trioSceneIndex + 1) % 3, true); host.postDelayed(this, 30000L) } }
        trioSceneRunnable = task; host.postDelayed(task, 30000L)
    }

    private fun scheduleTrioIdleMotion() {
        val host = findViewById<View>(android.R.id.content) ?: return
        trioIdleRunnable?.let(host::removeCallbacks)
        val started = android.os.SystemClock.uptimeMillis()
        var lastFrame = started
        val task = object : Runnable {
            override fun run() {
                val front = trioSceneFront ?: return
                val now = android.os.SystemClock.uptimeMillis()
                val t = (now - started) / 1000f
                // Bound a resumed frame so a pause cannot launch the artwork across the screen.
                val frame = ((now - lastFrame).coerceIn(1L, 64L) / 32f)
                lastFrame = now
                val density = resources.displayMetrics.density.coerceAtLeast(1f)
                val widthDp = window.decorView.width / density
                val amplitude = if (widthDp < 650f) 5f else 9f
                // Ease touch motion back to rest; an immediate reset looked like a snap.
                val touchEase = 1f - .88f.pow(frame)
                trioTouchX += (trioTouchTargetX - trioTouchX) * touchEase
                trioTouchY += (trioTouchTargetY - trioTouchY) * touchEase
                val phase = when (trioSceneIndex) { 1 -> 1.8f; 2 -> 3.5f; else -> 0f }
                // Give each character a slightly different physical cadence. Roxy glides,
                // Sylphie feels lighter, and Eris settles with a firmer spring.
                val spring = when (trioSceneIndex) { 1 -> .050f; 2 -> .075f; else -> .060f }
                val damping = when (trioSceneIndex) { 1 -> .86f; 2 -> .79f; else -> .83f }
                val idleX = kotlin.math.sin(t * .34f + phase) * amplitude + trioTouchX
                val idleY = kotlin.math.sin(t * .47f + 1.1f + phase) * (amplitude * .55f) + trioTouchY
                trioVelocityX = (trioVelocityX + (idleX - trioMotionX) * spring * frame) * damping.pow(frame)
                trioVelocityY = (trioVelocityY + (idleY - trioMotionY) * spring * frame) * damping.pow(frame)
                trioMotionX += trioVelocityX * frame
                trioMotionY += trioVelocityY * frame
                val rotation = kotlin.math.sin(t * .22f + phase) * when (trioSceneIndex) { 1 -> .16f; 2 -> .10f; else -> .13f }
                // Overscan is computed from the smaller viewport dimension, so
                // translation and breathing cannot reveal a black edge on either screen.
                val shortSide = kotlin.math.min(front.width, front.height).coerceAtLeast(1)
                val overscan = (2f * (amplitude + 6f) + 16f) / shortSide
                val breathe = 1f + overscan + kotlin.math.sin(t * .72f + phase) * .0045f
                // Both artwork views move together while their alpha crossfades.
                // Otherwise the departing character appears to freeze mid-motion.
                for (scene in arrayOf(front, trioSceneBack)) {
                    scene ?: continue
                    scene.translationX = trioMotionX
                    scene.translationY = trioMotionY
                    scene.rotation = rotation
                    scene.scaleX = breathe
                    scene.scaleY = breathe
                }
                host.postDelayed(this, 32L)
            }
        }
        trioIdleRunnable = task
        host.post(task)
    }

    private fun nudgeTrioScene(x: Float, y: Float) {
        val root = window.decorView
        if (root.width <= 0 || root.height <= 0) return
        trioTouchTargetX = ((x / root.width) - .5f) * -10f
        trioTouchTargetY = ((y / root.height) - .5f) * -6f
        root.removeCallbacks(trioTouchReset)
        root.postDelayed(trioTouchReset, 260L)
    }

    private val trioTouchReset = Runnable {
        trioTouchTargetX = 0f
        trioTouchTargetY = 0f
    }

    private fun installTrioManaLayer() {
        val host = findViewById<ViewGroup>(android.R.id.content) ?: return
        if (trioManaView != null) return
        val mana = TrioManaView(); mana.isClickable = false; mana.isFocusable = false
        host.addView(mana, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)); trioManaView = mana
    }

    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {
        if (ev.actionMasked == MotionEvent.ACTION_DOWN || ev.actionMasked == MotionEvent.ACTION_MOVE) {
            trioManaView?.manaTouch(ev.x, ev.y, ev.eventTime)
            nudgeTrioScene(ev.x, ev.y)
        }
        return super.dispatchTouchEvent(ev)
    }

    private inner class TrioManaView : View(this) {
        private val paint = Paint(Paint.ANTI_ALIAS_FLAG); private val bursts = ArrayDeque<TrioBurst>()
        private val droplet = Path()
        private val windArc = RectF()
        private var active = false
        private var fieldX = 0f; private var fieldY = 0f
        private var fieldTargetX = 0f; private var fieldTargetY = 0f
        private var lastTouchBurst = 0L; private var unfoldBorn = 0L; private var character = 0
        fun setActive(value: Boolean) { active = value; if (value) postInvalidateOnAnimation() }
        fun setCharacter(value: Int) { character = value % 3; invalidate() }
        fun manaTouch(x: Float, y: Float, now: Long) {
            if (!active) return
            // The mana has its own shallow parallax, separate from the artwork spring.
            fieldTargetX = ((x / width.coerceAtLeast(1)) - .5f) * 36f
            fieldTargetY = ((y / height.coerceAtLeast(1)) - .5f) * 24f
            if (now - lastTouchBurst < 42L) return; lastTouchBurst = now
            bursts.addLast(TrioBurst(x, y, now, (x.toInt() * 31 + y.toInt()) and 0x7fffffff))
            while (bursts.size > 12) bursts.removeFirst(); postInvalidateOnAnimation()
        }
        fun unfoldBurst() { unfoldBorn = android.os.SystemClock.uptimeMillis(); postInvalidateOnAnimation() }
        override fun onDraw(canvas: Canvas) {
            super.onDraw(canvas); val now = android.os.SystemClock.uptimeMillis(); val w = width.toFloat().coerceAtLeast(1f); val h = height.toFloat().coerceAtLeast(1f)
            if (now - lastTouchBurst > 300L) { fieldTargetX *= .92f; fieldTargetY *= .92f }
            fieldX += (fieldTargetX - fieldX) * .08f
            fieldY += (fieldTargetY - fieldY) * .08f
            val rgb = when (character) { 1 -> intArrayOf(214,255,226); 2 -> intArrayOf(255,126,72); else -> intArrayOf(164,226,255) }
            repeat(16) { i ->
                val phase = ((now * (3L + i % 2) + i * 7919L) % 32000L) / 32000f
                val depth = 0.65f + (i % 3) * .25f
                val x = ((i * 0.6180339f + 0.13f) % 1f) * w + kotlin.math.sin(phase * 6.283f + i * 0.7f) * 18f + fieldX * depth
                val y = h - phase * (h + 120f) + fieldY * depth; val r = 2.2f + (i % 4) * 1.2f
                when (character) {
                    1 -> { // Sylphie: short, drifting wind curves.
                        paint.style = Paint.Style.STROKE; paint.strokeWidth = 1.4f
                        paint.color = Color.argb(86,rgb[0],rgb[1],rgb[2])
                        windArc.set(x-r*3f,y-r*1.7f,x+r*3f,y+r*1.7f)
                        canvas.drawArc(windArc, 205f, 140f, false, paint)
                    }
                    2 -> { // Eris: warm rising embers with a fading tail.
                        paint.style = Paint.Style.STROKE; paint.strokeWidth = r*.8f
                        paint.color = Color.argb(78,rgb[0],rgb[1],rgb[2])
                        canvas.drawLine(x+r*.7f,y+r*2.5f,x,y,paint)
                        paint.style = Paint.Style.FILL; paint.color = Color.argb(120,rgb[0],rgb[1],rgb[2])
                        canvas.drawCircle(x,y,r*.65f,paint)
                    }
                    else -> { // Roxy: pointed water droplets.
                        paint.style = Paint.Style.FILL; paint.color = Color.argb(90,rgb[0],rgb[1],rgb[2])
                        droplet.reset(); droplet.moveTo(x,y-r*2.2f)
                        droplet.cubicTo(x-r*1.8f,y+r*.5f,x-r,y+r*1.5f,x,y+r*1.5f)
                        droplet.cubicTo(x+r,y+r*1.5f,x+r*1.8f,y+r*.5f,x,y-r*2.2f)
                        droplet.close(); canvas.drawPath(droplet,paint)
                    }
                }
            }
            val expired = ArrayList<TrioBurst>()
            for (b in bursts) {
                val age=(now-b.born).coerceAtLeast(0L); if(age>900L){expired.add(b);continue}; val t=age/900f; val alpha=((1f-t)*205).toInt(); val rgb=when(character){1->intArrayOf(196,255,214);2->intArrayOf(255,102,48);else->intArrayOf(142,226,255)}
                paint.style=Paint.Style.STROKE;paint.strokeWidth=2.4f+(1f-t)*3f;paint.color=Color.argb(alpha,rgb[0],rgb[1],rgb[2]);canvas.drawCircle(b.x,b.y,12f+t*98f,paint)
                repeat(8){j->val angle=j*.785398f+t*2.4f+(b.seed%17)*.05f;val radius=10f+t*(44f+(j%3)*11f);paint.style=Paint.Style.FILL;paint.color=Color.argb((alpha*.86f).toInt(),rgb[0],rgb[1],rgb[2]);canvas.drawCircle(b.x+kotlin.math.cos(angle)*radius,b.y+kotlin.math.sin(angle)*radius-t*24f,2.3f+(j%3),paint)}
            }
            expired.forEach { bursts.remove(it) }
            if(unfoldBorn>0L){val age=now-unfoldBorn;if(age<950L){val t=age/950f;repeat(2){ring->paint.style=Paint.Style.STROKE;paint.strokeWidth=(6f-ring*2f)*(1f-t)+1f;paint.color=Color.argb(((1f-t)*(145-ring*35)).toInt(),160,230,255);canvas.drawCircle(w/2f,h/2f,36f+ring*28f+t*kotlin.math.max(w,h)*(.56f+ring*.06f),paint)}}else unfoldBorn=0L}
            if(active)postInvalidateOnAnimation()
        }
    }

    private fun playTrioLiveLauncherReveal() {
        if(trioRevealRunning||isFinishing||isDestroyed)return
        val content=findViewById<View>(android.R.id.content)?:return;if(content.width<=0||content.height<=0)return
        trioRevealRunning=true;content.animate().cancel();content.scaleX=1f;content.scaleY=1f;content.alpha=.90f
        content.animate().alpha(1f).setDuration(650L).setInterpolator(DecelerateInterpolator(1.7f)).withEndAction{content.scaleX=1f;content.scaleY=1f;content.alpha=1f;trioRevealRunning=false}.start()
    }

    override fun onStart() {
"""

old_lifecycle_start = """    override fun onStart() {
        super.onStart(); widgets.host.startListening()
"""
new_lifecycle_start = """    override fun onStart() {
        super.onStart(); widgets.host.startListening()
        trioActive = true
        trioManaView?.setActive(true)
        scheduleTrioScene()
        scheduleTrioIdleMotion()
"""

old_lifecycle_stop = """    override fun onStop() {
        if (timeReceiverRegistered) { unregisterReceiver(timeReceiver); timeReceiverRegistered = false }
"""
new_lifecycle_stop = """    override fun onStop() {
        trioActive = false
        trioManaView?.setActive(false)
        val host = findViewById<View>(android.R.id.content)
        trioSceneRunnable?.let { host?.removeCallbacks(it) }
        trioIdleRunnable?.let { host?.removeCallbacks(it) }
        window.decorView.removeCallbacks(trioTouchReset)
        trioTouchTargetX = 0f; trioTouchTargetY = 0f
        if (timeReceiverRegistered) { unregisterReceiver(timeReceiver); timeReceiverRegistered = false }
"""

old_destroy = """    override fun onDestroy() {
        recreatingShadeSetup = isChangingConfigurations
"""
new_destroy = """    override fun onDestroy() {
        trioLayoutListener?.let { listener -> window.decorView.viewTreeObserver.takeIf { it.isAlive }?.removeOnGlobalLayoutListener(listener) }
        trioLayoutListener = null
        trioSceneRunnable?.let { findViewById<View>(android.R.id.content)?.removeCallbacks(it) }
        trioSceneRunnable = null
        trioIdleRunnable?.let { findViewById<View>(android.R.id.content)?.removeCallbacks(it) }
        window.decorView.removeCallbacks(trioTouchReset)
        trioIdleRunnable = null; trioSceneFront = null; trioSceneBack = null; trioManaView = null
        recreatingShadeSetup = isChangingConfigurations
"""

for old,new,label in ((old_import,new_import,"imports"),(old_attach,new_attach,"attachment"),(old_marker,new_marker,"Fold7/mana methods"),(old_lifecycle_start,new_lifecycle_start,"start lifecycle"),(old_lifecycle_stop,new_lifecycle_stop,"stop lifecycle"),(old_destroy,new_destroy,"cleanup")):
    if m.count(old) != 1: raise SystemExit(f"Pinned upstream {label} block changed; refusing unsafe patch")
    m=m.replace(old,new,1)
main.write_text(m)
print("Applied Build #20 foundation with Fold7-safe full-artwork framing")
