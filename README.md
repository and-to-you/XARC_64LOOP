# XARC_64LOOP
XARC_64LOOP is a 64‑bit loop cipher core used internally by the XARC archive format.

It processes data in 64‑bit chunks using a lightweight reversible transform based on:

XOR chaining

1‑bit rotation

Zero‑padding for incomplete blocks

The design is intended for internal consistency, not cryptographic strength.

Features
Fixed 64‑bit block processing

Stream‑like chaining structure

XOR + rotate transformation

Zero (0x00) padding

Fully reversible

No external key (XARC‑internal only)

Algorithm Overview
1. Chunking
Input bytes are split into 8‑byte (64‑bit) chunks.
If the final block is shorter, it is padded with 0x00.

2. Encryption
For each 64‑bit chunk:

XOR with previous output

Initial value: 0xA5A5A5A5A5A5A5A5

Rotate left by 1 bit

Output becomes the next “prev” value

3. Decryption
Reverse of encryption:

Rotate right by 1 bit

XOR with previous encrypted block

Restore original 64‑bit chunk

Public Functions
pack_data_xarc64(data: bytes)
Encrypts the input byte sequence

Returns:
{
  "encoded": <encrypted bytes>,
  "pad": <padding size>
}
unpack_data_xarc64(raw: bytes)
Decrypts the encrypted byte sequence

Removes padding and returns the original data

Directory Structure

XARC_64LOOP/
 ├─ XARC_64LOOP.py   # Core implementation
 ├─ _test.py         # Basic test
 └─ __init__.py
Minimal Test

python _test.py
If the output shows OK: True, the implementation is correct.

Usage
Used by XARC for internal file‑data encryption and decryption

Only pack_data_xarc64 and unpack_data_xarc64 are intended for external use

Notes
Not designed for security

Intended for reversible internal transformation

Do not use as a general‑purpose cipher
