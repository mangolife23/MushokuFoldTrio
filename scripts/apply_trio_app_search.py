#!/usr/bin/env python3
"""Make Trio's on-screen search control open and focus the local app library."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_app_search.py <duo-source-root>")

root = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher"

def replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise SystemExit(f"Pinned upstream {label} changed; refusing unsafe patch")
    return source.replace(old, new, 1)

main = root / "LauncherScreen.kt"
s = main.read_text()
s = replace_once(s, '    var libraryQuery by rememberSaveable { mutableStateOf("") }\n',
    '    var libraryQuery by rememberSaveable { mutableStateOf("") }\n'
    '    var trioSearchRequest by remember { mutableIntStateOf(0) }\n', "search state")
s = replace_once(s,
    '    val openLibrary = { scope.launch { pager.animateScrollToPage(homePages) }; Unit }\n',
    '    val openLibrary = { scope.launch { pager.animateScrollToPage(homePages) }; Unit }\n'
    '    val openAppSearch = {\n'
    '        scope.launch {\n'
    '            pager.scrollToPage(homePages)\n'
    '            trioSearchRequest++\n'
    '        }\n'
    '        Unit\n'
    '    }\n', "search action")
s = replace_once(s,
    '                        libraryQuery = libraryQuery, onLibraryQuery = { libraryQuery = it },\n'
    '                        onLaunch = onLaunch, onLaunchFrom = onLaunchFrom, onPinned = model::setPinned,',
    '                        libraryQuery = libraryQuery, onLibraryQuery = { libraryQuery = it },\n'
    '                        trioSearchRequest = trioSearchRequest, onTrioSearchFocused = { trioSearchRequest = 0 },\n'
    '                        onLaunch = onLaunch, onLaunchFrom = onLaunchFrom, onPinned = model::setPinned,',
    "expanded call")
s = replace_once(s,
    '                            drag = drag, page = visibleHomePages, onLaunchFrom = onLaunchFrom, onTurnOnWork = { model.turnOnWork(it) })',
    '                            drag = drag, page = visibleHomePages, onLaunchFrom = onLaunchFrom, onTurnOnWork = { model.turnOnWork(it) },\n'
    '                            focusRequest = trioSearchRequest, onFocusConsumed = { trioSearchRequest = 0 })',
    "compact library")
s = replace_once(s,
    '                val searchBounds = remember { android.graphics.Rect() }\n'
    '                Box(Modifier.onGloballyPositioned { searchBounds.set(it.boundsInWindow().toAndroidBounds()) }) {\n'
    '                    CircleControl(Icons.Rounded.Search, if (state.googleSearch) "Search Google" else "Search apps", "search", controlSize) {\n'
    '                        if (!state.googleSearch || !onGoogleSearch(searchBounds)) openLibrary()\n'
    '                    }\n'
    '                }',
    '                CircleControl(Icons.Rounded.Search, "Search apps", "search", controlSize) { openAppSearch() }',
    "screen search control")
s = replace_once(s,
    '            Text("Search button opens Google", Modifier.weight(1f))',
    '            Text("Google search for external shortcuts", Modifier.weight(1f))',
    "search preference label")
s = replace_once(s,
    '    libraryQuery: String,\n    onLibraryQuery: (String) -> Unit,\n    onLaunch: (AppEntry) -> Unit,',
    '    libraryQuery: String,\n    onLibraryQuery: (String) -> Unit,\n'
    '    trioSearchRequest: Int, onTrioSearchFocused: () -> Unit,\n    onLaunch: (AppEntry) -> Unit,',
    "expanded arguments")
s = replace_once(s,
    '                        drag = drag, page = visibleHomePages, onLaunchFrom = onLaunchFrom, onTurnOnWork = onTurnOnWork)',
    '                        drag = drag, page = visibleHomePages, onLaunchFrom = onLaunchFrom, onTurnOnWork = onTurnOnWork,\n'
    '                        focusRequest = trioSearchRequest, onFocusConsumed = onTrioSearchFocused)',
    "expanded library")
main.write_text(s)

library = root / "AppLibrary.kt"
s = library.read_text()
s = replace_once(s, 'import androidx.compose.ui.platform.testTag\n',
    'import androidx.compose.ui.platform.testTag\n'
    'import androidx.compose.ui.platform.LocalSoftwareKeyboardController\n'
    'import androidx.compose.ui.focus.FocusRequester\n'
    'import androidx.compose.ui.focus.focusRequester\n', "focus imports")
s = replace_once(s,
    '    onTurnOnWork: (Long) -> Unit = {},\n) {',
    '    onTurnOnWork: (Long) -> Unit = {},\n'
    '    focusRequest: Int = 0, onFocusConsumed: () -> Unit = {},\n) {', "focus arguments")
s = replace_once(s,
    '    val glass = !editing\n',
    '    val focusRequester = remember { FocusRequester() }\n'
    '    val keyboard = LocalSoftwareKeyboardController.current\n'
    '    LaunchedEffect(focusRequest) {\n'
    '        if (focusRequest > 0) {\n'
    '            withFrameNanos { }\n'
    '            focusRequester.requestFocus()\n'
    '            keyboard?.show()\n'
    '            onFocusConsumed()\n'
    '        }\n'
    '    }\n'
    '    val glass = !editing\n', "focus effect")
s = replace_once(s,
    'OutlinedTextField(query, onQuery, Modifier.fillMaxWidth().padding(vertical = 12.dp).testTag(if (editing) "pin-search" else "library-search"),',
    'OutlinedTextField(query, onQuery, Modifier.fillMaxWidth().padding(vertical = 12.dp)\n'
    '                .focusRequester(focusRequester).testTag(if (editing) "pin-search" else "library-search"),',
    "search field")
library.write_text(s)
print("Applied prototype local app search and keyboard focus")
