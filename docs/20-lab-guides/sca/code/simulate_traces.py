"""Sinh trace giả lập (không cần phần cứng) để kiểm tra script CPA.

Mô hình rò rỉ: tại một mẫu cố định cho mỗi byte, công suất = HW(SBOX[pt ^ key]) + nhiễu Gauss.

Ví dụ:
    python simulate_traces.py --n 2000 --noise 2.0 --out sim
"""
import argparse
import numpy as np
from aes_common import SBOX, HW

# Khóa kiểm thử công khai trong FIPS-197 (không phải bí mật)
DEFAULT_KEY = "2b7e151628aed2a6abf7158809cf4f3c"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000, help="số trace")
    ap.add_argument("--samples", type=int, default=500, help="số mẫu mỗi trace")
    ap.add_argument("--noise", type=float, default=2.0, help="độ lệch chuẩn nhiễu")
    ap.add_argument("--key", default=DEFAULT_KEY)
    ap.add_argument("--out", default="sim", help="tiền tố tên file đầu ra")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    key = np.frombuffer(bytes.fromhex(a.key), dtype=np.uint8)
    pt = rng.integers(0, 256, size=(a.n, 16), dtype=np.uint8)
    traces = rng.normal(0, a.noise, size=(a.n, a.samples)).astype(np.float32)

    # Mỗi byte rò rỉ tại một vị trí riêng, cách nhau 20 mẫu, bắt đầu từ mẫu 100
    for b in range(16):
        leak = HW[SBOX[pt[:, b] ^ key[b]]].astype(np.float32)
        traces[:, 100 + 20 * b] += leak

    np.save(f"{a.out}_traces.npy", traces)
    np.save(f"{a.out}_textin.npy", pt)
    print(f"Đã lưu {a.n} trace vào {a.out}_traces.npy và {a.out}_textin.npy")


if __name__ == "__main__":
    main()
