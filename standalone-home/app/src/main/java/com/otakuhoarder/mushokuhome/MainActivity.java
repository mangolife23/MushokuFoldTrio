package com.otakuhoarder.mushokuhome;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.ResolveInfo;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.RenderEffect;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.view.inputmethod.InputMethodManager;
import android.content.Context;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.GridLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.text.Editable;
import android.text.TextWatcher;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

public final class MainActivity extends Activity {
    private static final String[] NAMES = {"Roxy", "Sylphie", "Eris"};
    private static final int[] BACK = {R.drawable.trio_roxy, R.drawable.trio_sylphie, R.drawable.trio_eris};
    private static final int[] REST = {R.drawable.trio_roxy_cutout, R.drawable.trio_sylphie, R.drawable.trio_eris};
    private static final int[] BLINK = {R.drawable.trio_roxy_sneeze, R.drawable.trio_sylphie_blink, R.drawable.trio_eris_blink};
    private static final int[] REACH = {R.drawable.trio_roxy_reach, R.drawable.trio_sylphie_reach, R.drawable.trio_eris_reach};
    private static final int[] TINT = {0xff78b8f6, 0xffb6e9b4, 0xffffb18a};
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final List<ResolveInfo> apps = new ArrayList<>();
    private FrameLayout root, art, drawer;
    private ImageView backdrop, resting, blink, reach;
    private LinearLayout chips, dock;
    private TextView caption;
    private EditText search;
    private GridLayout appGrid;
    private int scene, generation;
    private float downX, downY;
    private boolean active;
    private final Runnable beat = new Runnable() {
        @Override public void run() {
            if (active && drawer == null) playBeat();
            if (active) handler.postDelayed(this, 9200L);
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        if (state != null) scene = state.getInt("scene", 0);
        getWindow().setStatusBarColor(0xff172034);
        getWindow().setNavigationBarColor(0xff111826);
        getWindow().getDecorView().setSystemUiVisibility(0);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        readApps();
        render();
    }
    @Override protected void onSaveInstanceState(Bundle out) {
        out.putInt("scene", scene);
        super.onSaveInstanceState(out);
    }
    @Override public void onConfigurationChanged(Configuration config) {
        super.onConfigurationChanged(config);
        closeDrawer();
        render();
    }
    @Override protected void onResume() {
        super.onResume();
        active = true;
        readApps();
        if (dock != null) populateDock();
        handler.removeCallbacks(beat);
        handler.postDelayed(beat, 5000L);
    }
    @Override protected void onPause() {
        active = false;
        generation++;
        handler.removeCallbacksAndMessages(null);
        super.onPause();
    }
    @Override protected void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
    @Override public void onBackPressed() {
        if (drawer != null) closeDrawer();
        else super.onBackPressed();
    }

    private int dp(float value) { return (int) (value * getResources().getDisplayMetrics().density + .5f); }
    private GradientDrawable panel(int color, int radius) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color);
        d.setCornerRadius(dp(radius));
        return d;
    }
    private TextView label(String text, int size, int color) {
        TextView v = new TextView(this);
        v.setText(text);
        v.setTextSize(size);
        v.setTextColor(color);
        v.setGravity(Gravity.CENTER);
        return v;
    }
    private void readApps() {
        Intent query = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> found = getPackageManager().queryIntentActivities(query, 0);
        apps.clear();
        for (ResolveInfo app : found) {
            if (!app.activityInfo.packageName.equals(getPackageName())) apps.add(app);
        }
        Collections.sort(apps, Comparator.comparing(a ->
            a.loadLabel(getPackageManager()).toString().toLowerCase(Locale.ROOT)));
    }
    private void launch(ResolveInfo app) {
        try {
            Intent intent = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER);
            intent.setComponent(new ComponentName(app.activityInfo.packageName, app.activityInfo.name));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
            startActivity(intent);
            closeDrawer();
        } catch (RuntimeException ignored) { readApps(); if (drawer != null) populateGrid(search.getText().toString()); }
    }
    private void openGoogle() {
        try {
            Intent intent = getPackageManager().getLaunchIntentForPackage("com.google.android.googlequicksearchbox");
            if (intent != null) { startActivity(intent); return; }
        } catch (RuntimeException ignored) { }
        Intent searchIntent = new Intent(Intent.ACTION_WEB_SEARCH);
        if (searchIntent.resolveActivity(getPackageManager()) != null) startActivity(searchIntent);
    }
    private ImageView artwork(int id, ImageView.ScaleType scale) {
        ImageView v = new ImageView(this);
        v.setImageResource(id);
        v.setScaleType(scale);
        return v;
    }
    private void render() {
        generation++;
        root = new FrameLayout(this);
        root.setBackgroundColor(0xff10192a);
        setContentView(root);
        backdrop = artwork(BACK[scene], ImageView.ScaleType.CENTER_CROP);
        backdrop.setAlpha(.46f);
        backdrop.setRenderEffect(RenderEffect.createBlurEffect(dp(38), dp(38), Shader.TileMode.CLAMP));
        root.addView(backdrop, new FrameLayout.LayoutParams(-1, -1));
        View shade = new View(this);
        shade.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
            new int[] {0x99101829, 0x10101829, 0xaa101829}));
        root.addView(shade, new FrameLayout.LayoutParams(-1, -1));

        art = new FrameLayout(this);
        FrameLayout.LayoutParams artParams = new FrameLayout.LayoutParams(-1, -1);
        root.addView(art, artParams);
        boolean portraitCutout = scene == 0;
        ImageView.ScaleType scale = ImageView.ScaleType.FIT_CENTER;
        resting = artwork(REST[scene], scale);
        blink = artwork(BLINK[scene], scale);
        reach = artwork(REACH[scene], scale);
        if (portraitCutout) {
            FrameLayout.LayoutParams portrait = new FrameLayout.LayoutParams(-1, -1);
            portrait.setMargins(dp(8), dp(18), dp(8), dp(75));
            art.addView(resting, portrait);
            art.addView(blink, new FrameLayout.LayoutParams(portrait));
            art.addView(reach, new FrameLayout.LayoutParams(portrait));
        } else {
            art.addView(resting, new FrameLayout.LayoutParams(-1, -1));
            art.addView(blink, new FrameLayout.LayoutParams(-1, -1));
            art.addView(reach, new FrameLayout.LayoutParams(-1, -1));
        }
        blink.setAlpha(0f); reach.setAlpha(0f);
        art.setOnTouchListener((v, event) -> {
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    downX = event.getX(); downY = event.getY(); return true;
                case MotionEvent.ACTION_UP:
                    float dx = event.getX() - downX, dy = event.getY() - downY;
                    if (Math.abs(dx) > dp(55) && Math.abs(dx) > Math.abs(dy)) {
                        if (dx > 0 && scene == 0) openGoogle();
                        else switchScene((scene + (dx < 0 ? 1 : 2)) % 3);
                    } else if (dy < -dp(55)) openDrawer();
                    else if (Math.abs(dx) < dp(24) && Math.abs(dy) < dp(24)) playReach();
                    return true;
                default: return true;
            }
        });
        animateIdle(art, true);

        LinearLayout header = new LinearLayout(this);
        header.setGravity(Gravity.CENTER_VERTICAL);
        header.setPadding(dp(14), dp(8), dp(14), dp(8));
        header.setBackground(panel(0xc91b263a, 20));
        FrameLayout.LayoutParams headerParams = new FrameLayout.LayoutParams(-1, dp(54), Gravity.TOP);
        headerParams.setMargins(dp(12), dp(12), dp(12), 0);
        root.addView(header, headerParams);
        TextView google = label("G", 23, 0xffe5f0ff);
        google.setTypeface(null, Typeface.BOLD);
        header.addView(google, new LinearLayout.LayoutParams(dp(46), -1));
        google.setContentDescription("Open Google app");
        google.setOnClickListener(v -> openGoogle());
        chips = new LinearLayout(this);
        chips.setGravity(Gravity.CENTER);
        header.addView(chips, new LinearLayout.LayoutParams(0, -1, 1));
        populateChips();
        TextView find = label("⌕", 32, 0xffe5f0ff);
        find.setContentDescription("Search apps");
        header.addView(find, new LinearLayout.LayoutParams(dp(46), -1));
        find.setOnClickListener(v -> openDrawer());

        caption = label(NAMES[scene], 19, 0xffffffff);
        caption.setTypeface(null, Typeface.BOLD);
        caption.setShadowLayer(dp(7), 0, dp(2), Color.BLACK);
        FrameLayout.LayoutParams captionParams = new FrameLayout.LayoutParams(dp(180), dp(42), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        captionParams.bottomMargin = dp(104);
        root.addView(caption, captionParams);
        dock = new LinearLayout(this);
        dock.setGravity(Gravity.CENTER);
        dock.setPadding(dp(10), dp(5), dp(10), dp(5));
        dock.setBackground(panel(0xd6202d42, 26));
        FrameLayout.LayoutParams dockParams = new FrameLayout.LayoutParams(-1, dp(76), Gravity.BOTTOM);
        dockParams.setMargins(dp(12), 0, dp(12), dp(12));
        root.addView(dock, dockParams);
        populateDock();
    }
    private void populateChips() {
        chips.removeAllViews();
        for (int i = 0; i < NAMES.length; i++) {
            final int index = i;
            TextView chip = label(NAMES[i], 13, scene == i ? 0xff10192a : 0xffdce6f7);
            chip.setTypeface(null, scene == i ? Typeface.BOLD : Typeface.NORMAL);
            if (scene == i) chip.setBackground(panel(TINT[i], 18));
            LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, dp(34), 1);
            p.setMargins(dp(2), 0, dp(2), 0);
            chips.addView(chip, p);
            chip.setOnClickListener(v -> switchScene(index));
        }
    }
    private void switchScene(int next) {
        if (scene == next) return;
        scene = next;
        closeDrawer();
        render();
    }
    private void animateIdle(FrameLayout target, boolean forward) {
        if (target != art) return;
        float shift = scene == 2 ? 4f : 7f;
        target.animate().translationX(dp(forward ? shift : -shift))
            .translationY(dp(forward ? -5 : 5))
            .rotation(forward && scene == 1 ? .35f : -.22f)
            .setDuration(scene == 2 ? 3900 : 5100)
            .withEndAction(() -> {
                if (active && target == art) animateIdle(target, !forward);
            }).start();
    }
    private void playBeat() {
        int token = ++generation;
        blink.animate().cancel();
        blink.setAlpha(0f);
        blink.animate().alpha(1f).setDuration(110).start();
        handler.postDelayed(() -> { if (token == generation) blink.animate().alpha(0f).setDuration(180).start(); }, 240);
        handler.postDelayed(() -> { if (token == generation) playReach(); }, 640);
    }
    private void playReach() {
        int token = ++generation;
        reach.animate().cancel();
        reach.setAlpha(0f);
        reach.animate().alpha(1f).setDuration(240).start();
        caption.animate().scaleX(1.08f).scaleY(1.08f).setDuration(330).withEndAction(() ->
            caption.animate().scaleX(1f).scaleY(1f).setDuration(300).start()).start();
        handler.postDelayed(() -> { if (token == generation) reach.animate().alpha(0f).setDuration(400).start(); },
            scene == 1 ? 1000 : 750);
    }
    private void populateDock() {
        dock.removeAllViews();
        String[] preferred = {"phone", "messages", "chrome", "camera"};
        List<ResolveInfo> picked = new ArrayList<>();
        for (String item : preferred) {
            for (ResolveInfo app : apps) {
                if (app.loadLabel(getPackageManager()).toString().toLowerCase(Locale.ROOT).contains(item) && !picked.contains(app)) {
                    picked.add(app); break;
                }
            }
        }
        for (ResolveInfo app : apps) {
            if (picked.size() >= 4) break;
            if (!picked.contains(app)) picked.add(app);
        }
        for (ResolveInfo app : picked) {
            ImageView icon = artwork(0, ImageView.ScaleType.FIT_CENTER);
            icon.setImageDrawable(app.loadIcon(getPackageManager()));
            icon.setContentDescription("Open " + app.loadLabel(getPackageManager()));
            icon.setPadding(dp(9), dp(9), dp(9), dp(9));
            dock.addView(icon, new LinearLayout.LayoutParams(0, -1, 1));
            icon.setOnClickListener(v -> launch(app));
        }
        TextView all = label("⋮", 30, Color.WHITE);
        all.setContentDescription("All apps");
        dock.addView(all, new LinearLayout.LayoutParams(0, -1, 1));
        all.setOnClickListener(v -> openDrawer());
    }
    private void openDrawer() {
        if (drawer != null) { search.requestFocus(); return; }
        drawer = new FrameLayout(this);
        drawer.setBackgroundColor(0xf4192334);
        root.addView(drawer, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout sheet = new LinearLayout(this);
        sheet.setOrientation(LinearLayout.VERTICAL);
        sheet.setPadding(dp(16), dp(16), dp(16), dp(8));
        drawer.addView(sheet, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout toolbar = new LinearLayout(this);
        toolbar.setGravity(Gravity.CENTER_VERTICAL);
        sheet.addView(toolbar, new LinearLayout.LayoutParams(-1, dp(54)));
        TextView close = label("‹", 34, Color.WHITE);
        close.setContentDescription("Close all apps");
        toolbar.addView(close, new LinearLayout.LayoutParams(dp(42), -1));
        close.setOnClickListener(v -> closeDrawer());
        search = new EditText(this);
        search.setSingleLine(true);
        search.setHint("Search apps");
        search.setTextColor(Color.WHITE);
        search.setHintTextColor(0xffaab8ca);
        search.setTextSize(18);
        search.setPadding(dp(14), 0, dp(14), 0);
        search.setBackground(panel(0xff34445c, 18));
        toolbar.addView(search, new LinearLayout.LayoutParams(0, dp(48), 1));
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(false);
        sheet.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        appGrid = new GridLayout(this);
        appGrid.setAlignmentMode(GridLayout.ALIGN_BOUNDS);
        appGrid.setColumnCount(getResources().getConfiguration().smallestScreenWidthDp >= 600 ? 7 : 4);
        appGrid.setPadding(0, dp(12), 0, dp(20));
        scroll.addView(appGrid);
        populateGrid("");
        search.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int st, int count, int after) { }
            public void onTextChanged(CharSequence s, int st, int before, int count) { populateGrid(s.toString()); }
            public void afterTextChanged(Editable s) { }
        });
        search.requestFocus();
        search.postDelayed(() -> {
            if (drawer != null) ((InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE))
                .showSoftInput(search, InputMethodManager.SHOW_IMPLICIT);
        }, 180);
    }
    private void populateGrid(String filter) {
        if (appGrid == null) return;
        appGrid.removeAllViews();
        int cols = appGrid.getColumnCount();
        int width = getResources().getDisplayMetrics().widthPixels - dp(32);
        int cell = width / cols;
        int count = 0;
        for (ResolveInfo app : apps) {
            String name = app.loadLabel(getPackageManager()).toString();
            if (!name.toLowerCase(Locale.ROOT).contains(filter.trim().toLowerCase(Locale.ROOT))) continue;
            LinearLayout item = new LinearLayout(this);
            item.setOrientation(LinearLayout.VERTICAL);
            item.setGravity(Gravity.TOP | Gravity.CENTER_HORIZONTAL);
            ImageView icon = artwork(0, ImageView.ScaleType.FIT_CENTER);
            icon.setImageDrawable(app.loadIcon(getPackageManager()));
            item.addView(icon, new LinearLayout.LayoutParams(dp(52), dp(52)));
            TextView nameView = label(name, 12, 0xffedf4ff);
            nameView.setMaxLines(2);
            nameView.setEllipsize(android.text.TextUtils.TruncateAt.END);
            item.addView(nameView, new LinearLayout.LayoutParams(-1, dp(35)));
            GridLayout.LayoutParams p = new GridLayout.LayoutParams(GridLayout.spec(count / cols), GridLayout.spec(count % cols));
            p.width = cell; p.height = dp(105);
            appGrid.addView(item, p);
            item.setOnClickListener(v -> launch(app));
            count++;
        }
        if (count == 0) {
            TextView empty = label("No matching apps", 16, 0xffc7d6e8);
            GridLayout.LayoutParams p = new GridLayout.LayoutParams(GridLayout.spec(0), GridLayout.spec(0, cols));
            p.width = width; p.height = dp(90);
            appGrid.addView(empty, p);
        }
    }
    private void closeDrawer() {
        if (drawer == null) return;
        ((InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE)).hideSoftInputFromWindow(drawer.getWindowToken(), 0);
        root.removeView(drawer);
        drawer = null; search = null; appGrid = null;
    }
}
