---
description: Use when the user shares a drive.google.com link or asks to read files from Google Drive. Read-only access to publicly shared resources only.
---

# Google Drive (read-only, public links)

Drive access is via a worker-side proxy. The real API key never enters the sandbox — it's appended server-side. You only need:

- `$GOOGLE_DRIVE_BASE_URL` — proxy base, e.g. `.../google-drive-proxy`
- `$GOOGLE_DRIVE_PROXY_KEY` — value for the `x-proxy-key` header

**Only resources shared "Anyone with the link can view" are reachable.** Private files return 404 — tell the user to update the sharing setting and retry.

## Extract the ID from a Drive URL

| URL form | ID |
|---|---|
| `drive.google.com/drive/folders/<ID>` | `<ID>` |
| `drive.google.com/file/d/<ID>/view`   | `<ID>` |
| `drive.google.com/open?id=<ID>`       | `<ID>` |
| `docs.google.com/document/d/<ID>/edit`| `<ID>` |

## List files in a public folder

```bash
curl -s -H "x-proxy-key: $GOOGLE_DRIVE_PROXY_KEY" \
  "$GOOGLE_DRIVE_BASE_URL/drive/v3/files?q='FOLDER_ID'+in+parents+and+trashed%3Dfalse&fields=files(id,name,mimeType,size,modifiedTime)&pageSize=100" | jq
```

If listing returns empty for a folder you know is shared, the user likely set sharing to "Restricted" — only "Anyone with the link" works for API-key access.

## Get file metadata

```bash
curl -s -H "x-proxy-key: $GOOGLE_DRIVE_PROXY_KEY" \
  "$GOOGLE_DRIVE_BASE_URL/drive/v3/files/FILE_ID?fields=id,name,mimeType,size" | jq
```

## Download a binary file (images, PDFs, zips, etc.)

```bash
mkdir -p /workspace/downloads
curl -sL -H "x-proxy-key: $GOOGLE_DRIVE_PROXY_KEY" \
  "$GOOGLE_DRIVE_BASE_URL/drive/v3/files/FILE_ID?alt=media" \
  -o /workspace/downloads/NAME.ext
```

Use the file name from `files.get` to pick `NAME.ext`. The proxy passes the binary body through unchanged.

## Export Google Workspace docs

Native Docs/Sheets/Slides cannot be downloaded with `alt=media`. Use `/export`:

| Source mimeType | Export to | exportMimeType |
|---|---|---|
| application/vnd.google-apps.document     | PDF / docx | `application/pdf` / `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| application/vnd.google-apps.spreadsheet  | XLSX / CSV | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` / `text/csv` |
| application/vnd.google-apps.presentation | PDF / pptx | `application/pdf` / `application/vnd.openxmlformats-officedocument.presentationml.presentation` |

```bash
curl -sL -H "x-proxy-key: $GOOGLE_DRIVE_PROXY_KEY" \
  "$GOOGLE_DRIVE_BASE_URL/drive/v3/files/FILE_ID/export?mimeType=application%2Fpdf" \
  -o /workspace/downloads/doc.pdf
```

## Search by name across reachable files

```bash
curl -s -H "x-proxy-key: $GOOGLE_DRIVE_PROXY_KEY" \
  "$GOOGLE_DRIVE_BASE_URL/drive/v3/files?q=name+contains+'photo'&fields=files(id,name,mimeType)" | jq
```

Searching only finds public files the API key can already see (no global Drive search).

## Failure handling

- **404 / `notFound`** → file or folder is private. Tell the user: *"Open the share dialog in Drive and set 'General access' to 'Anyone with the link'."*
- **403 / `dailyLimitExceeded` or `userRateLimitExceeded`** → quota hit. Wait and retry.
- **403 / `cannotDownloadAbusiveFile`** → rare; Drive flagged the file. No workaround via API.
- Empty file list on a folder you can open in browser → likely the folder is shared but its *contents* are not, or sharing is "Restricted" with viewer access for specific people only. API-key access cannot impersonate users.

## What you cannot do here

This integration is read-only: no upload, no rename, no permission changes, no access to files that aren't publicly shared. If the user wants any of those, tell them this requires the (future) "Connect Drive" OAuth flow.
