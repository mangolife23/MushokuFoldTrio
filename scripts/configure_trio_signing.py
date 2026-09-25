#!/usr/bin/env python3
"""Let the isolated prototype's debug APK use a stable private signing key."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: configure_trio_signing.py <duo-source-root>")

gradle = Path(sys.argv[1]) / "app/build.gradle.kts"
s = gradle.read_text()
old = '''    buildTypes {
        getByName("release") {
'''
new = '''    buildTypes {
        getByName("debug") {
            // CI can sign this isolated prototype consistently using a private
            // keystore. Without the configured secret, Gradle's debug key remains.
            if (releaseStoreFile != null) signingConfig = signingConfigs.getByName("release")
        }
        getByName("release") {
'''
if s.count(old) != 1:
    raise SystemExit("Pinned upstream build type block changed; refusing unsafe patch")
gradle.write_text(s.replace(old, new, 1))
print("Enabled optional stable signing for native prototype debug APK")
