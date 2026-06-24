# Hermes WeChat Gateway Voice Architecture

Reference: how `gateway/platforms/weixin.py` handles outbound voice/SILK messages.

## Send Flow

```
Response with MEDIA:/path/to/file.silk
    ↓
send() [line 1744]
    ├─ extract_media(content) → [(path, is_voice), ...]
    └─ _deliver_media(path, is_voice) [line 1767]
         └─ ext = Path(path).suffix.lower()
            ext in _AUDIO_EXTS (.ogg/.opus/.mp3/.wav/.m4a/.flac/.silk)
              → send_voice(chat_id, audio_path)
                    ├─ .silk → _send_file(force_file_attachment=False)
                    │           → _outbound_media_builder(path, force_file_attachment=False)
                    │             → path.endswith(".silk") → MEDIA_VOICE + ITEM_VOICE builder
                    │           → CDN upload (AES-128-ECB encrypted)
                    │           → iLink API send with encode_type=6, sample_rate=24000
                    │           → Native voice bubble 🎵
                    │
                    └─ non-.silk → _send_file(force_file_attachment=True)
                                  → _outbound_media_builder → MEDIA_FILE
                                  → File attachment 📎
```

## Key Constants (weixin.py)

```python
MEDIA_IMAGE = 1
MEDIA_VIDEO = 2
MEDIA_FILE  = 3
MEDIA_VOICE = 4

_AUDIO_EXTS = {".ogg", ".opus", ".mp3", ".wav", ".m4a", ".flac", ".silk"}
_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".3gp"}
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
```

## CDN Upload Process

1. File read as bytes → random 16-byte AES key generated
2. `getUploadUrl` API call → gets `upload_param` / `upload_full_url`
3. AES-128-ECB encrypt file content with the generated key
4. POST ciphertext to CDN upload URL
5. Build media item with `encrypt_query_param`, `aes_key` (base64 of hex string), metadata
6. Send via iLink `sendmessage` API

## SILK-specific Parameters

When `media_type == MEDIA_VOICE and path.endswith(".silk")`:

```python
item_kwargs["encode_type"] = 6        # SILK codec type
item_kwargs["sample_rate"] = 24000    # 24 kHz
item_kwargs["bits_per_sample"] = 16   # 16-bit
```

These are passed to the `ITEM_VOICE` builder which creates:

```python
{
    "type": 5,  # ITEM_VOICE
    "voice_item": {
        "media": {
            "encrypt_query_param": "...",
            "aes_key": "...",
            "encrypt_type": 1,
        },
        "encode_type": 6,
        "bits_per_sample": 16,
        "sample_rate": 24000,
        "playtime": 0,
    }
}
```

## Gateway Dual-Instance Detection

The gateway uses a PID file + process scan at startup. If another gateway is detected:

```
ERROR gateway.run: Another gateway instance (PID X) started during our startup.
```

This prevents both instances from polling iLink simultaneously (which would cause duplicate responses / token conflicts). **Consequence:** `send_message` reports success but the media never leaves the dying instance. Always kill stale processes before restarting:

```bash
pkill -f "hermes.*gateway"
hermes gateway start    # or: hermes gateway run
```

## Diagnostics

To verify a SILK file is properly formed:

```bash
# Check file header (should start with \x02#!SILK_V3)
xxd file.silk | head -1
# Expected: 00000000: 0223 2153 494c 4b5f 5633  ...

# Check file command recognizes it
file file.silk
# Expected: "data" (file command doesn't have a SILK magic entry)
```
