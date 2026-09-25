#!/usr/bin/env python3
"""Diagnose Google feed binds and probe an empty overlay descriptor."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_trio_discover_diagnostics.py <duo-source-root>")

client = Path(sys.argv[1]) / "app/src/main/java/com/jake/duolauncher/DiscoverClient.kt"
s = client.read_text()
old = '''                if (runCatching { service.interfaceDescriptor }.getOrNull() != OVERLAY) {
                    failed("Google didn't accept the feed connection. Restart Google, then retry.", attempt)
                    return
                }
'''
new = '''                val descriptor = runCatching { service.interfaceDescriptor }.getOrNull()
                if (name.packageName != GOOGLE_PACKAGE || (!descriptor.isNullOrBlank() && descriptor != OVERLAY)) {
                    Log.w(TAG, "Google feed binder rejected: package=${name.packageName}, descriptor=${descriptor ?: "unavailable"}")
                    failed("Google returned ${descriptor?.takeIf { it.isNotBlank() } ?: "no feed interface"} instead of its launcher feed. Open Google, then retry.", attempt)
                    return
                }
                // Some Google builds provide an empty descriptor for this service.
                // Probe only Google's bound service and require its ready callback;
                // the existing timeout keeps an unresponsive binder recoverable.
                if (descriptor.isNullOrBlank()) Log.w(TAG, "Google feed binder has no descriptor; probing launcher overlay")
'''
if s.count(old) != 1:
    raise SystemExit("Pinned upstream feed binder check changed; refusing unsafe patch")
client.write_text(s.replace(old, new, 1))
print("Added Discover diagnostics and a guarded empty-descriptor overlay probe")
