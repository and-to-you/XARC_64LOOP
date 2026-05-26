# _test.py
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
    print("OK  :", msg == dec)
    print()

if __name__ == "__main__":
    test_once(b"Hello Vulkan XARC!!!")
    test_once(b"12345678ABCDEFGH")
    test_once(b"AB#$%^&*()_+-=~`" * 10)
