package com.otakuhoarder.mushokuhome;

final class TrioScenes {
    static final String PREFS = "trio_control";
    static final String[] NAMES = {"Roxy", "Sylphie", "Eris"};
    static final int[] BACK = {R.drawable.trio_roxy, R.drawable.trio_sylphie_source, R.drawable.trio_eris_source};
    static final int[] SCENERY = {R.drawable.trio_roxy_scenery_4k, R.drawable.trio_sylphie_scenery_4k, R.drawable.trio_eris_scenery_4k};
    static final int[] REST = {R.drawable.trio_roxy_cutout, R.drawable.trio_sylphie_cutout_4k, R.drawable.trio_eris_cutout_4k};
    static final int[] BLINK = {R.drawable.trio_roxy_sneeze, R.drawable.trio_sylphie_blink_4k, R.drawable.trio_eris_blink_4k};
    static final int[] REACH = {R.drawable.trio_roxy_reach, R.drawable.trio_sylphie_reach_4k, R.drawable.trio_eris_reach_4k};
    static final int[] TINT = {0xff78b8f6, 0xffb6e9b4, 0xffffb18a};
    static int bounded(int scene) { return Math.max(0, Math.min(scene, NAMES.length - 1)); }
    private TrioScenes() { }
}
