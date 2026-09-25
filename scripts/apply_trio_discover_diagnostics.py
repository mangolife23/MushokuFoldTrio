#!/usr/bin/env python3
"""Expose the Google feed bind rejection on the prototype recovery screen."""
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
                if (descriptor != OVERLAY) {
                    Log.w(TAG, "Google feed binder rejected: descriptor=${descriptor ?: "unavailable"}")
                    failed("Google returned ${descriptor ?: "no feed interface"} instead of its launcher feed. Open Google, then retry.", attempt)
                    return
                }
'''
if s.count(old) != 1:
    raise SystemExit("Pinned upstream feed binder check changed; refusing unsafe patch")
client.write_text(s.replace(old, new, 1))
print("Added prototype Discover bind diagnostics without changing the accepted protocol")
