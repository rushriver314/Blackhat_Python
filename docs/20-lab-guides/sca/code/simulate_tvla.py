"""Sinh dữ liệu giả lập fixed-vs-random cho lab TVLA (không cần phần cứng).

- Nhóm 'fixed'  : plaintext cố định  -> rò rỉ HW(SBOX[pt^key]) hằng định
- Nhóm 'random' : plaintext ngẫu nhiên -> rò rỉ thay đổi
Khác biệt trung bình giữa hai nhóm tạo ra đỉnh t.

--leak 0 : tắt rò rỉ (mô phỏng thiết bị có masking tốt) -> t nằm dưới ngưỡng.

Ví dụ:
    python simulate_tvla.py --n 4000 --out tvla_sim
    python simulate_tvla.py --n 4000 --leak 0 --out tvla_safe
"""
import argparse
import numpy as np
from aes_common import SBOX, HW

FIXED_PT = np.frombuffer(bytes.fromhex("da39a3ee5e6b4b0d3255bfef95601890"), dtype=np.uint8)
KEY = np.frombuffer(bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c"), dtype=np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000, help="tổng số trace (chia đôi fixed/random)")
    ap.add_argument("--samples", type=int, default=300)
    ap.add_argument("--noise", type=float, default=3.0)
    ap.add_argument("--leak", type=float, default=1.0, help="hệ số rò rỉ (0 = không rò rỉ)")
    ap.add_argument("--out", default="tvla_sim")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    group = (rng.random(a.n) < 0.5).astype(np.uint8)  # 1 = fixed, 0 = random
    pt = rng.integers(0, 256, size=(a.n, 16), dtype=np.uint8)
    pt[group == 1] = FIXED_PT

    traces = rng.normal(0, a.noise, size=(a.n, a.samples)).astype(np.float32)
    leak = HW[SBOX[pt[:, 0] ^ KEY[0]]].astype(np.float32)
    traces[:, 150] += a.leak * leak

    np.save(f"{a.out}_traces.npy", traces)
    np.save(f"{a.out}_group.npy", group)
    print(f"Đã lưu {a.n} trace ({int(group.sum())} fixed) vào {a.out}_traces.npy / {a.out}_group.npy")


if __name__ == "__main__":
    main()
