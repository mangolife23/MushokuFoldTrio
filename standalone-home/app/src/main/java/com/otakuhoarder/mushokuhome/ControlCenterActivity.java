package com.otakuhoarder.mushokuhome;

import android.app.Activity;
import android.app.WallpaperManager;
import android.content.ComponentName;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;

/** Launcher icon entry: a control center inspired by the earlier Roxy companion. */
public final class ControlCenterActivity extends Activity {
    private SharedPreferences prefs;
    private ImageView backdrop;
    private ManaOverlayView mana;
    private TextView device, current, rotationStatus;
    private LinearLayout selector;
    private int scene;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs = getSharedPreferences(TrioScenes.PREFS, MODE_PRIVATE);
        scene = TrioScenes.bounded(prefs.getInt("active_scene", 0));
        getWindow().setStatusBarColor(0xff172034);
        getWindow().setNavigationBarColor(0xff111826);
        getWindow().getDecorView().setSystemUiVisibility(0);
        render();
    }
    @Override public void onConfigurationChanged(Configuration config) {
        super.onConfigurationChanged(config); render();
    }
    @Override protected void onResume() {
        super.onResume();
        int selected = TrioScenes.bounded(prefs.getInt("active_scene", scene));
        if (selected != scene) select(selected);
        if (device != null) device.setText(deviceState());
    }
    private int dp(float value) { return (int) (value * getResources().getDisplayMetrics().density + .5f); }
    private GradientDrawable panel(int color, int radius) {
        GradientDrawable d = new GradientDrawable(); d.setColor(color); d.setCornerRadius(dp(radius)); return d;
    }
    private TextView text(String value, int size, int color, boolean bold) {
        TextView v = new TextView(this);
        v.setText(value); v.setTextSize(size); v.setTextColor(color);
        if (bold) v.setTypeface(null, Typeface.BOLD);
        return v;
    }
    private String deviceState() {
        return getResources().getConfiguration().smallestScreenWidthDp >= 600
            ? "Unfolded display • Expanded mana mode" : "Cover display • Compact mana mode";
    }
    private void render() {
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(0xff121a29);
        setContentView(root);
        backdrop = new ImageView(this);
        backdrop.setImageResource(TrioScenes.BACK[scene]);
        backdrop.setScaleType(ImageView.ScaleType.CENTER_CROP);
        backdrop.setAlpha(.55f);
        root.addView(backdrop, new FrameLayout.LayoutParams(-1, -1));
        View shade = new View(this);
        shade.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
            new int[] {0x99111b2d, 0x50111b2d, 0xcc111b2d}));
        root.addView(shade, new FrameLayout.LayoutParams(-1, -1));
        mana = new ManaOverlayView(this);
        mana.setScene(scene);
        root.addView(mana, new FrameLayout.LayoutParams(-1, -1));

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        root.addView(scroll, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(20), dp(22), dp(20), dp(34));
        int maxWidth = Math.min(getResources().getDisplayMetrics().widthPixels, dp(760));
        FrameLayout centered = new FrameLayout(this);
        scroll.addView(centered);
        FrameLayout.LayoutParams contentParams = new FrameLayout.LayoutParams(maxWidth, -2, Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        centered.addView(content, contentParams);

        TextView brand = text("MUSHOKU HOME", 14, 0xffc3edff, true);
        content.addView(brand);
        TextView heading = text("TRIO CONTROL CENTER", 29, Color.WHITE, true);
        LinearLayout.LayoutParams headP = new LinearLayout.LayoutParams(-1, -2);
        headP.topMargin = dp(8); content.addView(heading, headP);
        device = text(deviceState(), 15, 0xffdef3ff, false);
        device.setPadding(dp(12), dp(12), dp(12), dp(12));
        device.setBackground(panel(0xc72b4055, 3));
        LinearLayout.LayoutParams deviceP = new LinearLayout.LayoutParams(-1, -2);
        deviceP.topMargin = dp(14); content.addView(device, deviceP);

        View spacer = new View(this);
        content.addView(spacer, new LinearLayout.LayoutParams(1, dp(190)));
        selector = new LinearLayout(this);
        selector.setGravity(Gravity.CENTER);
        selector.setPadding(dp(6), dp(6), dp(6), dp(6));
        selector.setBackground(panel(0xd019263b, 12));
        content.addView(selector, new LinearLayout.LayoutParams(-1, dp(57)));
        fillSelector();

        LinearLayout live = card(content);
        live.addView(text("LIVE MANA WALLPAPER", 14, 0xffaee8ff, true));
        current = text("", 24, Color.WHITE, true);
        LinearLayout.LayoutParams currentP = new LinearLayout.LayoutParams(-1, -2);
        currentP.topMargin = dp(9); live.addView(current, currentP);
        updateCurrent();
        TextView info = text("Three character scenes with gentle motion, responsive mana, and magical transitions.", 15, 0xffd2e1ee, false);
        LinearLayout.LayoutParams infoP = new LinearLayout.LayoutParams(-1, -2);
        infoP.topMargin = dp(10); infoP.bottomMargin = dp(14); live.addView(info, infoP);
        button(live, "PREVIEW & APPLY LIVE TRIO", this::openLive);
        button(live, "NEXT SCENE NOW", () -> select((scene + 1) % TrioScenes.NAMES.length));
        button(live, "CAST MANA PULSE", () -> mana.burst(.5f, .45f));
        button(live, "OPEN HOME UI", () -> startActivity(new Intent(this, MainActivity.class)));

        LinearLayout rotation = card(content);
        rotation.addView(text("TRIO ROTATION", 14, 0xffaee8ff, true));
        LinearLayout row = new LinearLayout(this);
        row.setGravity(Gravity.CENTER_VERTICAL);
        LinearLayout.LayoutParams rowP = new LinearLayout.LayoutParams(-1, dp(52));
        rowP.topMargin = dp(6); rotation.addView(row, rowP);
        TextView toggleLabel = text("Rotate character scenes automatically", 16, Color.WHITE, false);
        row.addView(toggleLabel, new LinearLayout.LayoutParams(0, -2, 1));
        Switch enabled = new Switch(this);
        enabled.setChecked(prefs.getBoolean("rotation_enabled", true));
        row.addView(enabled);
        rotationStatus = text("", 14, 0xffc7d7e8, false);
        rotation.addView(rotationStatus); updateRotation(enabled.isChecked());
        enabled.setOnCheckedChangeListener((button, checked) -> {
            prefs.edit().putBoolean("rotation_enabled", checked).apply();
            updateRotation(checked); mana.burst(.5f, .5f);
        });

        LinearLayout staticCard = card(content);
        staticCard.addView(text("STATIC ARTWORK", 14, 0xffaee8ff, true));
        TextView staticInfo = text("Apply the selected original scene to your wallpaper.", 14, 0xffc7d7e8, false);
        LinearLayout.LayoutParams staticP = new LinearLayout.LayoutParams(-1, -2);
        staticP.topMargin = dp(8); staticCard.addView(staticInfo, staticP);
        LinearLayout actions = new LinearLayout(this);
        LinearLayout.LayoutParams actionsP = new LinearLayout.LayoutParams(-1, dp(50));
        actionsP.topMargin = dp(10); staticCard.addView(actions, actionsP);
        staticButton(actions, "HOME", () -> apply(WallpaperManager.FLAG_SYSTEM));
        staticButton(actions, "LOCK", () -> apply(WallpaperManager.FLAG_LOCK));
        staticButton(actions, "BOTH", () -> {
            apply(WallpaperManager.FLAG_SYSTEM); apply(WallpaperManager.FLAG_LOCK);
        });
        TextView version = text("Mushoku Home • Trio Live Mana", 12, 0xffaebcd0, false);
        LinearLayout.LayoutParams versionP = new LinearLayout.LayoutParams(-1, -2);
        versionP.topMargin = dp(18); content.addView(version, versionP);
    }
    private LinearLayout card(LinearLayout parent) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(18), dp(18), dp(18), dp(18));
        card.setBackground(panel(0xe51a273b, 4));
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2);
        p.topMargin = dp(14); parent.addView(card, p);
        return card;
    }
    private void button(LinearLayout parent, String title, Runnable action) {
        TextView v = text(title, 16, Color.WHITE, false);
        v.setGravity(Gravity.CENTER);
        v.setBackground(panel(0xff586070, 4));
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, dp(50));
        p.topMargin = dp(8); parent.addView(v, p);
        v.setOnClickListener(view -> action.run());
    }
    private void staticButton(LinearLayout parent, String title, Runnable action) {
        TextView v = text(title, 15, Color.WHITE, false);
        v.setGravity(Gravity.CENTER); v.setBackground(panel(0xff586070, 4));
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, -1, 1);
        p.setMargins(dp(3), 0, dp(3), 0); parent.addView(v, p);
        v.setOnClickListener(view -> action.run());
    }
    private void fillSelector() {
        selector.removeAllViews();
        for (int i = 0; i < TrioScenes.NAMES.length; i++) {
            final int chosen = i;
            TextView chip = text(TrioScenes.NAMES[i], 15, scene == i ? 0xff142033 : Color.WHITE, scene == i);
            chip.setGravity(Gravity.CENTER);
            if (scene == i) chip.setBackground(panel(TrioScenes.TINT[i], 9));
            LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, -1, 1);
            p.setMargins(dp(2), 0, dp(2), 0); selector.addView(chip, p);
            chip.setOnClickListener(v -> select(chosen));
        }
    }
    private void select(int selected) {
        scene = selected; prefs.edit().putInt("active_scene", scene).apply();
        if (backdrop != null) backdrop.setImageResource(TrioScenes.BACK[scene]);
        if (mana != null) { mana.setScene(scene); mana.burst(.5f, .46f); }
        if (selector != null) fillSelector();
        updateCurrent();
    }
    private void updateCurrent() {
        if (current != null) current.setText(TrioScenes.NAMES[scene] + " • Motion Reactive");
    }
    private void updateRotation(boolean on) {
        rotationStatus.setText(on ? "3-scene gallery active • transition every 12 seconds"
            : "Rotation paused • selected character stays active");
    }
    private void openLive() {
        try {
            Intent intent = new Intent(WallpaperManager.ACTION_CHANGE_LIVE_WALLPAPER);
            intent.putExtra(WallpaperManager.EXTRA_LIVE_WALLPAPER_COMPONENT,
                new ComponentName(this, TrioLiveWallpaperService.class));
            startActivity(intent);
        } catch (RuntimeException unavailable) {
            try { startActivity(new Intent(WallpaperManager.ACTION_LIVE_WALLPAPER_CHOOSER)); }
            catch (RuntimeException ignored) { Toast.makeText(this, "Live wallpaper preview unavailable", Toast.LENGTH_LONG).show(); }
        }
    }
    private void apply(int target) {
        try (InputStream image = getResources().openRawResource(TrioScenes.BACK[scene])) {
            WallpaperManager.getInstance(this).setStream(image, null, true, target);
            mana.burst(.5f, .5f);
            Toast.makeText(this, TrioScenes.NAMES[scene] + " wallpaper applied", Toast.LENGTH_SHORT).show();
        } catch (IOException | SecurityException failure) {
            Toast.makeText(this, "Could not apply wallpaper", Toast.LENGTH_LONG).show();
        }
    }
}
