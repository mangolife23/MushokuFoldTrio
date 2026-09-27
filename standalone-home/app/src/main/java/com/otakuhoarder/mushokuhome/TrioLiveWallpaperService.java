package com.otakuhoarder.mushokuhome;

import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.service.wallpaper.WallpaperService;
import android.view.MotionEvent;
import android.view.SurfaceHolder;

/** Independent live wallpaper: three transparent portraits, timed fades, touch mana. */
public final class TrioLiveWallpaperService extends WallpaperService {
    @Override public Engine onCreateEngine() { return new TrioEngine(); }

    private final class TrioEngine extends Engine {
        private static final long SCENE_MS = 30000L, FADE_MS = 1800L;
        private final Handler handler = new Handler(Looper.getMainLooper());
        private final Paint artPaint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
        private final Paint fxPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final SharedPreferences prefs = getSharedPreferences(TrioScenes.PREFS, MODE_PRIVATE);
        private final Runnable frame = new Runnable() {
            @Override public void run() {
                if (!visible || !surfaceReady) return;
                drawFrame();
                handler.postDelayed(this, 33L);
            }
        };
        private Bitmap portrait, blurredBack, nextPortrait, nextBack;
        private int scene = TrioScenes.bounded(prefs.getInt("active_scene", 0));
        private int nextScene = -1, width, height;
        private boolean visible, surfaceReady;
        private long lastScene = SystemClock.uptimeMillis(), fadeAt, pulseAt = -10000L;
        private float pulseX = .5f, pulseY = .5f;

        @Override public void onSurfaceCreated(SurfaceHolder holder) {
            super.onSurfaceCreated(holder);
            surfaceReady = true;
            start();
        }
        @Override public void onSurfaceChanged(SurfaceHolder holder, int format, int w, int h) {
            super.onSurfaceChanged(holder, format, w, h);
            width = w; height = h; surfaceReady = true;
            if (portrait == null) loadCurrent();
            start();
        }
        @Override public void onVisibilityChanged(boolean shown) {
            visible = shown;
            if (shown) { lastScene = SystemClock.uptimeMillis(); start(); }
            else handler.removeCallbacks(frame);
        }
        @Override public void onSurfaceDestroyed(SurfaceHolder holder) {
            surfaceReady = false; handler.removeCallbacks(frame);
            release();
            super.onSurfaceDestroyed(holder);
        }
        @Override public void onDestroy() {
            handler.removeCallbacks(frame); release(); super.onDestroy();
        }
        @Override public void onTouchEvent(MotionEvent e) {
            if (e.getActionMasked() == MotionEvent.ACTION_DOWN && width > 0 && height > 0)
                pulse(e.getX() / width, e.getY() / height);
            super.onTouchEvent(e);
        }
        private void start() {
            handler.removeCallbacks(frame);
            if (visible && surfaceReady && width > 0 && height > 0) handler.post(frame);
        }
        private void pulse(float x, float y) {
            pulseX = x; pulseY = y; pulseAt = SystemClock.uptimeMillis();
        }
        private Bitmap decode(int id) {
            BitmapFactory.Options bounds = new BitmapFactory.Options();
            bounds.inJustDecodeBounds = true;
            BitmapFactory.decodeResource(getResources(), id, bounds);
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inSampleSize = 1;
            // Keep a screen-sized source; portrait assets remain 4K in the APK.
            int desired = Math.max(width, height);
            while (options.inSampleSize * 2 <= 4 && bounds.outHeight / (options.inSampleSize * 2) >= desired)
                options.inSampleSize *= 2;
            return BitmapFactory.decodeResource(getResources(), id, options);
        }
        private Bitmap back(int id) {
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inSampleSize = 16;
            Bitmap source = BitmapFactory.decodeResource(getResources(), id, options);
            if (source == null) return null;
            Bitmap tiny = Bitmap.createScaledBitmap(source, 72, 128, true);
            if (tiny != source) source.recycle();
            return tiny;
        }
        private void loadCurrent() {
            release();
            portrait = decode(TrioScenes.REST[scene]);
            blurredBack = back(TrioScenes.BACK[scene]);
        }
        private void queueScene(int requested, long now) {
            if (nextScene >= 0 || requested == scene) return;
            try {
                nextPortrait = decode(TrioScenes.REST[requested]);
                nextBack = back(TrioScenes.BACK[requested]);
                if (nextPortrait != null) {
                    nextScene = requested; fadeAt = now; pulse(.5f, .44f);
                } else recycle(nextBack);
            } catch (OutOfMemoryError failure) {
                recycle(nextPortrait); recycle(nextBack);
                nextPortrait = nextBack = null;
            }
        }
        private void finish(long now) {
            recycle(portrait); recycle(blurredBack);
            portrait = nextPortrait; blurredBack = nextBack;
            nextPortrait = nextBack = null;
            scene = nextScene; nextScene = -1; lastScene = now;
            prefs.edit().putInt("active_scene", scene).apply();
        }
        private void drawFrame() {
            if (portrait == null) loadCurrent();
            if (portrait == null) return;
            long now = SystemClock.uptimeMillis();
            int preferred = TrioScenes.bounded(prefs.getInt("active_scene", scene));
            if (preferred != scene) queueScene(preferred, now);
            else if (nextScene < 0 && prefs.getBoolean("rotation_enabled", true) && now - lastScene >= SCENE_MS)
                queueScene((scene + 1) % TrioScenes.NAMES.length, now);
            Canvas c = null;
            try {
                c = getSurfaceHolder().lockCanvas();
                if (c == null) return;
                width = c.getWidth(); height = c.getHeight();
                c.drawColor(0xff0b1422);
                float seconds = now / 1000f;
                drawScene(c, portrait, blurredBack, scene, 255, seconds);
                if (nextScene >= 0 && nextPortrait != null) {
                    float t = Math.min(1f, (now - fadeAt) / (float) FADE_MS);
                    float eased = t * t * (3f - 2f * t);
                    drawScene(c, nextPortrait, nextBack, nextScene, (int) (255 * eased), seconds);
                    if (t >= 1f) finish(now);
                }
                drawMana(c, now, seconds);
            } catch (RuntimeException ignored) {
                // The surface can disappear while a Home or wallpaper preview changes.
            } finally {
                if (c != null) getSurfaceHolder().unlockCanvasAndPost(c);
            }
        }
        private void drawScene(Canvas c, Bitmap character, Bitmap background, int index, int alpha, float time) {
            if (background != null) {
                artPaint.setAlpha((int) (alpha * .42f));
                c.drawBitmap(background, null, new RectF(0, 0, width, height), artPaint);
            }
            if (character != null) {
                float scale = Math.min(width * .98f / character.getWidth(), height * .93f / character.getHeight());
                float w = character.getWidth() * scale, h = character.getHeight() * scale;
                float drift = (float) Math.sin(time * (index == 2 ? .7f : .5f) + index) * Math.min(width, height) * .006f;
                float bob = (float) Math.sin(time * .62f + index) * Math.min(width, height) * .004f;
                float left = (width - w) * .5f + drift;
                float top = (height - h) * .5f + bob;
                artPaint.setAlpha(alpha);
                c.drawBitmap(character, null, new RectF(left, top, left + w, top + h), artPaint);
            }
            artPaint.setAlpha(255);
        }
        private void drawMana(Canvas c, long now, float time) {
            int tint = TrioScenes.TINT[scene] & 0xffffff;
            for (int i = 0; i < 25; i++) {
                float x = ((i * .618034f + time * (.013f + i % 3 * .003f)) % 1f) * width;
                float y = (1f - ((i * .173f + time * (.045f + i % 4 * .009f)) % 1f)) * height;
                int a = (int) (25 + 39 * (.5f + .5f * Math.sin(time * 1.6f + i)));
                fxPaint.setStyle(Paint.Style.FILL); fxPaint.setColor((a << 24) | tint);
                c.drawCircle(x, y, 1.5f + i % 3, fxPaint);
            }
            float age = (now - pulseAt) / 1000f;
            if (age < 0 || age > 1.5f) return;
            float p = age / 1.5f;
            fxPaint.setStyle(Paint.Style.STROKE);
            fxPaint.setStrokeWidth(2f + 7f * (1f - p));
            fxPaint.setColor(((int) (190 * (1f - p)) << 24) | tint);
            float radius = 24 + (1f - (1f - p) * (1f - p)) * Math.min(width, height) * .34f;
            c.drawCircle(pulseX * width, pulseY * height, radius, fxPaint);
            c.drawCircle(pulseX * width, pulseY * height, radius * .62f, fxPaint);
        }
        private void recycle(Bitmap b) { if (b != null && !b.isRecycled()) b.recycle(); }
        private void release() {
            recycle(portrait); recycle(blurredBack); recycle(nextPortrait); recycle(nextBack);
            portrait = blurredBack = nextPortrait = nextBack = null;
            nextScene = -1;
        }
    }
}
