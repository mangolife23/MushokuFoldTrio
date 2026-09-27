# Mushoku Home

A separate native Android HOME app for the Roxy, Sylphie, and Eris artwork. It has its own `com.otakuhoarder.mushokuhome` package, character picker, animated rest/blink/reach frames, app drawer with keyboard search, tappable dock, and an explicit Google app shortcut. It does not include DuoLauncher code or dependencies.

Install the debug APK, open its app drawer, and tap **Make Mushoku Home my default Home app** to bring up Android's Home chooser. The existing Trio prototype can remain installed. Swipe left or right across the artwork to switch characters; swipe up to open all apps; tap the art for a reach beat. On the Roxy page, swiping right opens the Google app when available. The Google shortcut opens the Google app rather than embedding Discover.

The app displays all three characters without cropping the original scene. The artwork also comes from the Trio repository at present; copy the ten `trio_*` art files to `app/src/main/res/drawable-nodpi/` when moving this subproject into its own repository.

This first build is a functional starting point for a separate project. It does not yet have persistent icon positions, widgets, folders, or a dedicated Google Discover integration. APKs built with a fresh Actions runner debug key generally require uninstalling the previous build before installing an update.
