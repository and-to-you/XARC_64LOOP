# XARC_64LOOP

**XARC_64LOOP** is a lightweight 64‑bit reversible loop transform used inside the XARC archive format.  
It is designed for internal data consistency rather than cryptographic strength.

The transform operates on 64‑bit blocks and applies a simple reversible sequence:

- XOR chaining  
- 1‑bit rotation  
- Zero‑padding for incomplete blocks  
- Fully reversible forward/backward processing  

This module provides two public functions:

- `pack_data_xarc64(data: bytes)` — encode (forward transform)  
- `unpack_data_xarc64(raw: bytes)` — decode (reverse transform)

---

## Algorithm Summary

### 1. Chunking
Input bytes are split into **8‑byte (64‑bit)** blocks.  
If the final block is shorter, it is padded with `0x00`.

### 2. Forward Transform (pack)
For each 64‑bit block:

1. XOR with the previous output  
   - Initial value: `0xA5A5A5A5A5A5A5A5`
2. Rotate left by 1 bit  
3. Output becomes the next “previous” value

### 3. Reverse Transform (unpack)
Reverse of the above:

1. Rotate right by 1 bit  
2. XOR with the previous encrypted block  
3. Restore the original 64‑bit chunk  
4. Remove zero‑padding at the end

---

## Public API

### `pack_data_xarc64(data: bytes) -> dict`
Encodes the input byte sequence.

Returns:
```python
{
    "encoded": <bytes>,
    "pad": <int>  # number of padding bytes added
}
