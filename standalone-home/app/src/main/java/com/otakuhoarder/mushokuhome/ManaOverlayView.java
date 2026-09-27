package com.otakuhoarder.mushokuhome;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.os.SystemClock;
import android.view.View;

/** Decorative, non-clickable mana. Touches stay with the Home artwork and controls. */
final class ManaOverlayView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private long origin = SystemClock.uptimeMillis();
    private long burstAt = -10000L;
    private float burstX = .5f, burstY = .5f;
    private int scene;

    ManaOverlayView(Context context) { super(context); setClickable(false); }
    void setScene(int value) { scene = TrioScenes.bounded(value); invalidate(); }
    void burst(float x, float y) {
        burstX = x; burstY = y; burstAt = SystemClock.uptimeMillis(); invalidate();
    }
    @Override protected void onDraw(Canvas c) {
        int w = getWidth(), h = getHeight();
        if (w == 0 || h == 0) return;
        long now = SystemClock.uptimeMillis();
        float t = (now - origin) / 1000f;
        int color = TrioScenes.TINT[scene] & 0x00ffffff;
        for (int i = 0; i < 24; i++) {
            float seed = (i * .618034f) % 1f;
            float x = ((seed + t * (.009f + i % 3 * .003f)) % 1f) * w;
            float y = h * (1f - ((i * .173f + t * (.035f + i % 4 * .008f)) % 1f));
            int alpha = (int) (30 + 34 * (.5f + .5f * Math.sin(t * 1.7f + i)));
            paint.setStyle(Paint.Style.FILL); paint.setColor((alpha << 24) | color);
            c.drawCircle(x, y, 1.5f + i % 3, paint);
        }
        float age = (now - burstAt) / 1000f;
        if (age >= 0 && age < 1.25f) {
            float eased = 1f - (1f - age / 1.25f) * (1f - age / 1.25f);
            float radius = (24f + eased * Math.min(w, h) * .35f);
            int alpha = (int) (175 * (1f - age / 1.25f));
            paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(2f + 6f * (1f - age / 1.25f));
            paint.setColor((alpha << 24) | color);
            c.drawCircle(burstX * w, burstY * h, radius, paint);
            c.drawCircle(burstX * w, burstY * h, radius * .62f, paint);
        }
        if (isAttachedToWindow() && getVisibility() == VISIBLE) postInvalidateDelayed(40L);
    }
}
