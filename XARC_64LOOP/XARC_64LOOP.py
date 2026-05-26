# XARC_64LOOP.py
import os
import struct
from typing import List, Tuple

# Vulkan GPU 実装（あれば使う）
try:
    import XARC_64LOOP_vk
    HAS_VK = True
except ImportError:
    HAS_VK = False


# ========= 共通ユーティリティ =========

def _to_chunks(data: bytes) -> Tuple[List[int], int]:
    """bytes → 64bitチャンク配列 + pad長"""
    pad = (8 - (len(data) % 8)) % 8
    if pad:
        data = data + b"\x00" * pad
    chunks = [
        struct.unpack(">Q", data[i:i+8])[0]
        for i in range(0, len(data), 8)
    ]
    return chunks, pad


def _from_chunks(chunks: List[int], pad: int) -> bytes:
    """64bitチャンク配列 + pad長 → bytes"""
    data = b"".join(struct.pack(">Q", c) for c in chunks)
    if pad:
        data = data[:-pad]
    return data


# ========= CPU 実装（ループ版） =========

def _loop_encrypt_cpu(chunks: List[int]) -> List[int]:
    """XARC_64LOOP の CPU 暗号ループ（ダミー実装例）"""
    out = []
    for i, v in enumerate(chunks):
        # ここはあなたの元のロジックに合わせて書き換えてOK
        k = 0x9E3779B97F4A7C15  # 例: 適当な定数
        out.append((v ^ (k + i)) & 0xFFFFFFFFFFFFFFFF)
    return out


def _loop_decrypt_cpu(chunks: List[int]) -> List[int]:
    """XARC_64LOOP の CPU 復号ループ（ダミー実装例）"""
    out = []
    for i, v in enumerate(chunks):
        k = 0x9E3779B97F4A7C15
        out.append((v ^ (k + i)) & 0xFFFFFFFFFFFFFFFF)
    return out


# ========= 公開API：暗号化 / 復号 =========

from XARC_64LOOP_vk import VulkanXarc64

def encrypt_xarc64(data: bytes):
    chunks, pad = _to_chunks(data)
    try:
        vk = VulkanXarc64()
        encoded = vk.run_encrypt(chunks)
        return {"encoded": b"".join(struct.pack(">Q", c) for c in encoded), "pad": pad, "mode": "GPU"}
    except Exception as e:
        print("[XARC][GPU FAIL encrypt]", e)
        enc_chunks = _loop_encrypt_cpu(chunks)
        raw = b"".join(struct.pack(">Q", c) for c in enc_chunks)
        return {"encoded": raw, "pad": pad, "mode": "CPU"}



def decrypt_xarc64(raw: bytes, pad: int) -> bytes:
    """
    XARC-64LOOP 復号
    戻り値: 復号済み bytes
    ※ mode は今は返さず、必要なら dict で返す形にしてもOK
    """
    # bytes → 64bitチャンク
    chunks = [
        struct.unpack(">Q", raw[i:i+8])[0]
        for i in range(0, len(raw), 8)
    ]

    use_vk_env = os.environ.get("USE_VULKAN", "auto")
    want_vk = HAS_VK and use_vk_env != "0"

    if want_vk and hasattr(XARC_64LOOP_vk, "decrypt_vk"):
        try:
            dec_bytes = XARC_64LOOP_vk.decrypt_vk(raw, pad)
            return dec_bytes
        except Exception as e:
            print("[XARC][GPU FAIL decrypt]", e)

    # CPU フォールバック
    dec_chunks = _loop_decrypt_cpu(chunks)
    data = _from_chunks(dec_chunks, pad)
    return data
