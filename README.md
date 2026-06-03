# XARC_64LOOP

**XARC_64LOOP** is a reversible 64‑bit loop transform designed for internal data consistency and experimental encryption.  
It demonstrates how minimal bitwise operations can achieve full reversibility without relying on external keys or complex state machines.

---

## Concept

The algorithm processes data in 64‑bit chunks, applying XOR chaining and bit rotation.  
Each block depends on the previous output, forming a deterministic reversible stream.

- **Block size:** 8 bytes (64 bits)  
- **Initial value:** `0xA5A5A5A5A5A5A5A5`  
- **Operations:** XOR → Rotate → Chain  
- **Padding:** Zero‑padding for incomplete blocks  
- **Reversibility:** Guaranteed for all byte patterns

---

## API

### `encrypt_xarc64(data: bytes) -> dict`
Encodes the input bytes using the loop transform.

Returns:
```python
{
    "encoded": <bytes>,
    "pad": <int>,
    "mode": "loop64"
}
```
`decrypt_xarc64(encoded: bytes, pad: int) -> bytes`
Decodes the transformed bytes and removes padding.
---
Example
```python
from XARC_64LOOP import encrypt_xarc64, decrypt_xarc64

def test_once(msg: bytes):
    print("---- TEST ----")
    print("orig:", msg)

    res = encrypt_xarc64(msg)
    enc = res["encoded"]
    pad = res["pad"]
    mode = res.get("mode", "unknown")

    print("mode:", mode)
    print("enc :", enc.hex())

    dec = decrypt_xarc64(enc, pad)
    print("dec :", dec)
    print("OK :", msg == dec)
    print()

if __name__ == "__main__":
    test_once(b"Hello Vulkan XARC!!!")
    test_once(b"12345678ABCDEFGH")
    test_once(b"AB#$%*&()_+-=~" * 10)
```
---
Usage
Run directly:
```bash
python _test.py
```
Expected output:
```
---- TEST ----
orig: b'Hello Vulkan XARC!!!'
mode: loop64
enc : 7a3f...
dec : b'Hello Vulkan XARC!!!'
OK : True
```
---
Purpose
To verify that the XARC_64LOOP algorithm correctly restores the original data after encryption and decryption,
ensuring full reversibility across different byte patterns.
---
Notes
Not for security use.  
This transform is experimental and intended for internal data processing only.

Deterministic behavior.  
Every encoded sequence can be perfectly restored.

Cross‑platform.  
Works on both CPU and GPU (Vulkan Compute implementation available).
---
License
MIT License. See LICENSE for details.
