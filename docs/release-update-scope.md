# Release and update scope

This page is meant to keep the desktop/updater work from turning into one giant
PR. There are already separate threads for update checks, desktop wrappers, and
release builds, so the safest path is to land these pieces in order instead of
mixing updater logic, installers, signing, and server lifecycle changes at once.

## What exists today

- The app exposes `/api/version`, which only reports the local `APP_VERSION`.
- `update_windows.bat` updates a Docker checkout by running `git pull` and
  rebuilding Compose services.
- `launch-windows.ps1` is a source-run Windows launcher. It creates a venv,
  installs requirements, runs setup, and starts Uvicorn.
- `start-macos.sh` is the native macOS source-run launcher.
- `build-macos-app.sh` can build a local `.app` and `.dmg` wrapper for the
  current checkout, but it does not bundle Python and is not a signed release
  artifact.
- The default branch currently has no GitHub Actions release workflow that
  publishes Windows, macOS, and Linux desktop artifacts.

That means a user can start or update a checkout in a few ways, but there is not
yet a supported "new version available, update now?" flow for the web UI or
desktop clients.

## Proposed landing order

1. **Check-only update status.**
   Add an authenticated endpoint/UI surface that can tell an admin whether the
   running checkout is behind GitHub. This should not run shell commands. It
   should fail closed and show network failures as "could not check" rather than
   a 500.

2. **Desktop wrapper proof of concept.**
   Add the smallest possible native wrapper that starts or connects to the
   existing local server and opens the UI. No autostart, updater, signing,
   global hotkeys, or installer workflow in the same PR.

3. **Release artifact workflow.**
   Add an opt-in GitHub Actions workflow for tag or manual builds. Each platform
   should build on its native runner:

   - Windows: `.exe` or installer package, plus checksums.
   - macOS: `.dmg`, with signing/notarization documented before it becomes a
     promoted release artifact.
   - Linux: AppImage or archive first, then distro packages only after the
     runtime paths and service files are stable.

4. **Updater prompt.**
   Once there is a trustworthy release manifest, clients can ask the user before
   applying an update. The default should be "prompt first"; automatic updates
   should only happen after the user opts into them.

5. **Apply/update commands.**
   Command execution belongs behind an admin-only gate. The UI should show the
   exact action it is about to run, keep logs visible, and allow canceling before
   anything destructive starts.

## Hard requirements before auto-update

- The update checker must compare against a stable source: a GitHub release tag,
  signed manifest, or a clearly named branch/commit policy.
- Release artifacts need checksums. Signed artifacts should document where keys
  live and what unsigned local/dev builds do.
- Update actions must not silently change the bind host, exposed ports, auth
  defaults, data directory, or checkout path.
- Docker, source-run, and desktop builds need separate paths. A Docker update
  should not assume the same behavior as a native app update.
- Existing user data needs a backup/rollback story before any in-app updater
  rewrites the checkout or replaces a binary.
- The app should never download and run arbitrary scripts from a moving branch.

## Related work

- #318 asks for update checks from settings.
- #1157 asks for container update support and database export.
- #606 tracks the standalone native app discussion.
- #843 asks for macOS prebuilt binaries.
- #261 tracks CI/CD release builds.
- #1028 is a check-only update status PR.
- #1179 adds companion update-check and export endpoints.
- #1236 explores a Tauri desktop wrapper, but needs to be split before merge.
- #168, #976, and #289 explore macOS, Windows, and broad packaging approaches.

The main thing this page adds is the boundary: update checks, desktop wrapper,
release artifacts, and update execution should be reviewed independently. That
keeps the project moving without asking maintainers to accept the whole desktop
distribution surface in one pass.
