# Mushoku Home

A separate native Android HOME app for the Roxy, Sylphie, and Eris artwork. It has its own `com.otakuhoarder.mushokuhome` package, character picker, animated rest/blink/reach frames, app drawer with keyboard search, tappable dock, and an explicit Google app shortcut. It does not include DuoLauncher code or dependencies.

Install the debug APK, open its app drawer, and tap **Make Mushoku Home my default Home app** to bring up Android's Home chooser. The existing Trio prototype can remain installed. Swipe left or right across the artwork to switch characters; swipe up to open all apps; tap the art for a reach beat. On the Roxy page, swiping right opens the Google app when available. The Google shortcut opens the Google app rather than embedding Discover.

The app displays each character as a transparent portrait over a softly blurred scene. Sylphie and Eris now use the two supplied portrait references for rest, blink, and action frames. Their WebP assets are 2160×3840 with alpha. Image generation produced about 940×1672 pixels of original detail; these files were upscaled to a 4K portrait canvas for display, so they are not natively generated 4K detail. All packaged art is self-contained under `app/src/main/res/drawable-nodpi/`.

This first build is a functional starting point for a separate project. It does not yet have persistent icon positions, widgets, folders, or a dedicated Google Discover integration. APKs built with a fresh Actions runner debug key generally require uninstalling the previous build before installing an update.
