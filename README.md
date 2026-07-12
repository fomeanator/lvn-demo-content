# Elvin — demo content

The demo novel (“Sovet”) and showcase content for the
[Elvin engine](https://github.com/fomeanator/unity-lvn-vn-engine): scripts
(.lvns/.lvn), art, audio, the content manifest, import templates and the
`_sources/` art archives.

**You do not need this to use the engine.** It exists for the engine's own
development: local dev servers and the release-APK pipeline fetch it into
`server/content` via `scripts/fetch-demo-content.sh` in the main repo.

Layout mirrors what the content server serves (`manifest.json` at the root,
`/content/...` URLs map here). `_sources/` holds third-party art source
archives (LPC/Kenney and the Spine knight sample) used by import staging.
