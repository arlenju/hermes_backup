# pysilk (silk-python) API Reference

Package: `silk-python` on PyPI (`pip install silk-python`)
Import: `import pysilk`
Source: https://github.com/synodriver/pysilk

## Encode (PCM → SILK)

```python
pysilk.encode(input, output, sample_rate, bit_rate,
              max_internal_sample_rate=24000,
              packet_loss_percentage=0,
              complexity=2,
              use_inband_fec=False,
              use_dtx=False,
              tencent=True) -> int
```

| Param | Type | Description |
|-------|------|-------------|
| `input` | BinaryIO | PCM data (file-like, 16-bit signed LE) |
| `output` | BinaryIO | Output stream for SILK data |
| `sample_rate` | int | Input PCM sample rate (8000, 12000, 16000, 24000) |
| `bit_rate` | int | Target bitrate in bps (e.g. 24000 = 24kbps) |
| `max_internal_sample_rate` | int | SILK internal sample rate (default 24000) |
| `tencent` | bool | **Must be True** for WeChat-compatible SILK v3 |

**Both input and output must be file-like objects** (e.g. `io.BytesIO()`).

**Returns:** number of bytes written to output.

### Common Usage

```python
import pysilk
import io

pcm_buf = io.BytesIO(pcm_data)
out_buf = io.BytesIO()
pysilk.encode(pcm_buf, out_buf, sample_rate=24000, bit_rate=24000)

with open('output.silk', 'wb') as f:
    f.write(out_buf.getvalue())
```

## Decode (SILK → PCM)

```python
pysilk.decode(input, output) -> int
```

| Param | Type | Description |
|-------|------|-------------|
| `input` | BinaryIO | SILK data (file-like) |
| `output` | BinaryIO | Output stream for PCM data |

## Notes

- The `tencent=True` parameter is critical — without it, WeChat won't recognize the SILK file as a valid voice message.
- SILK input should be 16-bit signed little-endian PCM.
- Recommended input: 24kHz mono PCM (converted from MP3 via ffmpeg: `-ar 24000 -ac 1 -sample_fmt s16`).
- Bitrate of 24000 (24kbps) provides good voice quality at small file size.
- On first use, the underlying C extension compiles automatically — no separate SDK install needed.
