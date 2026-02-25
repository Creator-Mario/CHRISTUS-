# CHRISTUS – Standalone Build Guide

This document explains how to build the **CHRISTUS** app as a standalone
distribution for **Windows** (Electron desktop) and **Android** (Capacitor).

The existing GitHub Pages PWA remains fully unchanged and independently deployable.

---

## Prerequisites

### All platforms
- **Node.js** ≥ 20 (recommended: 20 LTS or 22 LTS)  
  Download: <https://nodejs.org/>

### Windows build only
- A machine running Windows, macOS, or Linux (cross-compilation is possible but Windows builds are most reliable on Windows)
- `npm` (bundled with Node.js)

### Android build
- **Java Development Kit (JDK) 17** or 21  
  Download: <https://adoptium.net/>
- **Android Studio** (includes the Android SDK and build tools)  
  Download: <https://developer.android.com/studio>  
  After installing Android Studio, open **SDK Manager** and install:
  - Android SDK Platform 34 (or later)
  - Android SDK Build-Tools 34
  - Android SDK Command-line Tools
- Set the `ANDROID_SDK_ROOT` (or `ANDROID_HOME`) environment variable to your SDK location:
  - Windows: `C:\Users\<you>\AppData\Local\Android\Sdk`
  - macOS/Linux: `~/Library/Android/sdk` or `~/Android/Sdk`

---

## Windows Desktop Build (Electron)

### What you get
| Artifact | Description |
|----------|-------------|
| `CHRISTUS-<version>-portable.exe` | Single-file portable EXE – just run it, no install needed |
| `CHRISTUS-<version>-win.zip` | ZIP archive containing the portable build |
| `CHRISTUS-<version>-setup.exe` | NSIS installer with optional installation directory |

### Build steps

```bash
# 1. Enter the Electron wrapper directory
cd desktop-electron

# 2. Install dependencies
npm install

# 3. Build (the prebuild script copies web assets automatically)
npm run build
```

Output files appear in `desktop-electron/dist/`.

### What the build does
1. `scripts/bundle.js` copies `index.html`, `app/`, `sw.js`, and all CSVs from
   the repo root into `desktop-electron/www/`.
2. `electron-builder` packages `main.js` + `www/` into the installers.
3. The Electron app loads files from the local `www/` directory – **no internet
   connection required** during normal operation.

### Development / preview

```bash
cd desktop-electron
npm install
node scripts/bundle.js   # copy web assets once
npx electron .           # launch the app locally
```

---

## Android Build (Capacitor)

### What you get
| Artifact | Description |
|----------|-------------|
| `app-debug.apk` | Debug APK for sideloading / testing (signed with debug key) |
| `app-release.aab` | Unsigned release AAB for Google Play Store upload |
| `app-release-unsigned.apk` | Unsigned release APK (needs manual signing for distribution) |

### Build steps

```bash
# 1. Enter the Capacitor wrapper directory
cd mobile-capacitor

# 2. Install Capacitor dependencies
npm install

# 3. Copy web assets and add the Android platform (first time only)
node scripts/bundle.js
npx cap add android

# 4. Sync web assets into the Android project
npx cap sync android

# 5a. Build debug APK (no signing required)
cd android
./gradlew assembleDebug
# Output: android/app/build/outputs/apk/debug/app-debug.apk

# 5b. Build release AAB (unsigned – sign before Play Store upload)
./gradlew bundleRelease
# Output: android/app/build/outputs/bundle/release/app-release.aab

# 5c. Build release APK (unsigned)
./gradlew assembleRelease
# Output: android/app/build/outputs/apk/release/app-release-unsigned.apk
```

### Subsequent builds (after `npx cap add android` was already run)

```bash
cd mobile-capacitor
node scripts/bundle.js
npx cap sync android
cd android && ./gradlew assembleDebug
```

Or use the convenience npm scripts:

```bash
npm run build:apk      # debug APK
npm run build:aab      # release AAB
```

---

## Signing (Android release builds)

> **Never hardcode keystore passwords or paths in source files.**  
> Use environment variables or CI secrets instead.

### Generate a keystore (one-time)

```bash
keytool -genkey -v \
  -keystore christus.keystore \
  -alias christus \
  -keyalg RSA -keysize 2048 \
  -validity 10000
```

Store the keystore file securely (e.g. in a password manager or CI secrets store).

### Sign the release APK manually

```bash
# Align
zipalign -v 4 app-release-unsigned.apk app-release-aligned.apk

# Sign
apksigner sign \
  --ks christus.keystore \
  --ks-key-alias christus \
  --out app-release-signed.apk \
  app-release-aligned.apk
```

### Sign via environment variables in CI

Set the following secrets in your GitHub repository
(**Settings → Secrets and variables → Actions**):

| Secret | Description |
|--------|-------------|
| `KEYSTORE_BASE64` | Base64-encoded keystore file (`base64 christus.keystore`) |
| `KEYSTORE_PASSWORD` | Password for the keystore |
| `KEY_ALIAS` | Key alias (e.g. `christus`) |
| `KEY_PASSWORD` | Password for the key |

The provided `build-android.yml` workflow will automatically sign the APK when
these secrets are present.

---

## CI / GitHub Actions

Two optional workflows are included:

| Workflow file | Trigger | Output |
|---------------|---------|--------|
| `.github/workflows/build-electron.yml` | `workflow_dispatch`, tag `v*` | Windows ZIP + EXE artifacts |
| `.github/workflows/build-android.yml`  | `workflow_dispatch`, tag `v*` | APK + AAB artifacts |

Trigger a build manually via **Actions → (workflow name) → Run workflow**.

---

## Notes

- The **GitHub Pages PWA** (`deploy.yml`) is completely independent and
  unaffected by these standalone builds.
- The `desktop-electron/www/` and `mobile-capacitor/www/` directories are
  generated at build time and are excluded from version control via `.gitignore`.
- Service Workers are not active in the Electron context (the `file://` protocol
  does not support SW), but this is harmless because all assets are bundled
  locally and loaded directly from disk.
