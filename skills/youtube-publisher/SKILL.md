---
name: youtube-publisher
description: Upload or update a video on the user's confirmed YouTube channel with verified metadata, processing state and requested visibility.
---

# Publish the reviewed package

Read the actual final file, title, description, thumbnail and the user's requested visibility/schedule. This skill bundles no uploader, OAuth client or channel connection.

Inspect the connected tool's documented operations and verify the exact channel identity. Keep tokens and OAuth files in the tool's auth store or ignored private files. Missing credentials are not a reason to copy another project's connection.

Build a concrete upload package: final file, metadata, thumbnail, captions, playlist if requested, visibility and schedule/time zone. Check current platform requirements and available quota through official docs/tools. A request to prepare packaging does not authorize publication.

When the user authorized upload, execute that scope. Record the returned video ID before downstream steps. Query existing state after ambiguous results instead of uploading a duplicate. Apply only the requested visibility and schedule.

Verify processing status, final metadata, thumbnail, captions and access state with readback. Report the video URL and distinguish uploaded, processing, scheduled and public. A successful API response is not proof that all processing or public availability has completed.
