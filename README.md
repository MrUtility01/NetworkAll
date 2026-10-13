# NetworkAll — ENGINEER JOKAR

**NetworkAll v1.0.0** is a personal, offline-first networking and IT learning workspace for Windows and Android. It contains a Flask/SQLite Windows host, a Kotlin/Room Android client, and a shared curriculum index for the 68 chapter tree.

> **Release status:** v1.0.0 build candidate. Gradle success alone is not release certification. Check the latest GitHub Actions run for the final APK audit and Windows package artifact; Android installation and Android↔Windows sync still need device-level acceptance tests.

## Downloads

1. Open **[GitHub Actions](https://github.com/MrUtility01/NetworkAll/actions)**.
2. Select **NetworkAll Android APK (validated)** and open a successful run on branch `codex/android-repair-port86-20261013`.
3. Download `NetworkAll-Android-v1.0.0` for Android and `NetworkAll-Windows-v1.0.0` for Windows.
4. The Windows ZIP is a Python source/host bundle, **not a standalone EXE**. Python 3.11+ is required.

A failed workflow must not be treated as a release. Its logs explain whether curriculum validation, compilation, or the packaged-APK audit failed.

## Windows quick start

Prerequisite: Python 3.11+ available on PATH.

Extract the complete Windows ZIP to a writable folder and run:

```bat
windows\start.bat
```

The launcher creates a private `.venv`, installs `server/requirements.txt`, starts the host on TCP/86, and writes a per-install sync token to `server/data/networkall.token`. On first browser access, set a local web password (minimum 8 characters); choose the same password on Android at first launch if you want the same entry experience. The web password is stored as a salted hash, separately from the API token.

- Local browser: `http://127.0.0.1:86`
- Technical diagrams: `http://127.0.0.1:86/diagrams`
- Android host setting: `http://<Windows-LAN-IP>:86`
- Copy the content of `server/data/networkall.token` into Android Settings → API token.
- On Windows Firewall, allow inbound TCP/86 only on the trusted/private LAN profile. Do not expose this service directly to the public Internet.

The bundled Windows database is created on first run from the same generated curriculum asset as Android. Existing databases are intentionally not overwritten. Back up local data before any manual reseed or migration.

## Android quick start

Download the APK from a successful Actions artifact, install it, and open NetworkAll. On first launch, set a local unlock password and confirmation (you can choose your intended personal password here). On first use after entering the app, open Settings, enter the Windows URL and the per-install token, then use Sync. Notification permission must be granted for notifications to appear. The local lock is an access gate, not database encryption.

The application ID remains `com.netenc.app` to support updates to an existing installation. Version metadata for this build is `versionName=1.0.0`, `versionCode=4`.

## Repository layout

| Path | Purpose |
|---|---|
| `android/` | Android application and offline assets |
| `server/` | Flask API, SQLite seed and web UI |
| `windows/` | Windows launcher and setup notes |
| `shared/` | Shared LAN-sync helpers/protocol |
| `tools/packs/` | Content packs and command collections |
| `scripts/export_android_index.py` | Export the curriculum index |
| `scripts/merge_content_packs_into_android.py` | Merge content packs into the index |
| `scripts/validate_android_curriculum.py` | Structural and chapter-68 collection checks |
| `scripts/package_windows_v1.py` | Audit and package the Windows host bundle |
| `docs/V1_RELEASE_AUDIT_FA.md` | Known issues, test evidence, and release gate |

## Content build

From the repository root, in a Python 3.11 environment:

```bat
python scripts\export_android_index.py
python scripts\merge_content_packs_into_android.py
python scripts\validate_android_curriculum.py
python scripts\generate_android_diagrams.py
```

For a Windows ZIP, also run:

```bat
python scripts\package_windows_v1.py
```

The scripts expect the repository's Python modules and content packs to be present. The release workflow performs these steps before compiling Android and packaging Windows.

## Git workflow

```bash
git clone https://github.com/MrUtility01/NetworkAll.git
cd NetworkAll
git switch codex/android-repair-port86-20261013
git pull --ff-only
git status
```

Keep changes in a branch, validate JSON/Python/Android builds, then open a pull request to `main`. Do not commit `.env`, API keys, sync-token files, SQLite databases, APKs, or personal backups.

## Honest capability status

The offline curriculum tree, basic lesson display, search, quizzes/flashcards, scenario area, diagram gallery, local tasks/notes and LAN API are present in the codebase. This does **not** mean all features are equal between Windows and Android:

- Tasks, notes, study progress and reminder schedules are not yet proven end-to-end across both platforms.
- The 100 offline SVG files are generated templates, not 100 separately peer-reviewed network diagrams.
- Persian calendar coverage and notification behavior require device testing.
- Not every lesson has undergone subject-matter, command-version, output, and answer-key review.
- The app-level unlock screen and API sync-token authentication are separate security controls; never use a public repository as a place to store real credentials.

Track the acceptance items in [the v1 audit](docs/V1_RELEASE_AUDIT_FA.md) before calling a build final.
