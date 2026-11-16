"""Tấn công CPA (Correlation Power Analysis) lên đầu ra S-box vòng 1 của AES-128.

Mô hình: Hamming weight của SBOX[plaintext[b] ^ k].

Ví dụ:
    python cpa_attack.py --prefix lab1
    python cpa_attack.py --prefix sim --key 2b7e151628aed2a6abf7158809cf4f3c
"""
import argparse
import numpy as np
from aes_common import SBOX, HW


def cpa_byte(traces_c, trace_ss, pt_col):
    """Trả về ma trận |hệ số tương quan| kích thước (256 khóa đoán, số mẫu)."""
    n = traces_c.shape[0]
    guesses = np.arange(256, dtype=np.uint8)
    # Giả thuyết: (n, 256)
    hyp = HW[SBOX[pt_col[:, None] ^ guesses[None, :]]].astype(np.float64)
    hyp -= hyp.mean(axis=0)
    hyp_ss = np.sqrt((hyp ** 2).sum(axis=0))              # (256,)
    num = hyp.T @ traces_c                                # (256, samples)
    denom = np.outer(hyp_ss, trace_ss)
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = np.where(denom > 0, num / denom, 0.0)
    return np.abs(corr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="lab1", help="tiền tố file .npy")
    ap.add_argument("--n", type=int, default=None, help="chỉ dùng n trace đầu")
    ap.add_argument("--key", default=None, help="khóa đúng (hex) để so sánh, tùy chọn")
    a = ap.parse_args()

    traces = np.load(f"{a.prefix}_traces.npy").astype(np.float64)
    pt = np.load(f"{a.prefix}_textin.npy").astype(np.uint8)
    if a.n:
        traces, pt = traces[: a.n], pt[: a.n]

    true_key = None
    if a.key:
        true_key = bytes.fromhex(a.key)
    else:
        try:
            true_key = bytes(np.load(f"{a.prefix}_key.npy"))
        except FileNotFoundError:
            pass

    traces_c = traces - traces.mean(axis=0)
    trace_ss = np.sqrt((traces_c ** 2).sum(axis=0))

    print(f"Số trace: {traces.shape[0]}, số mẫu: {traces.shape[1]}\n")
    print("Byte | Đoán | Tương quan | Mẫu  | Hạng khóa đúng")
    print("-----+------+------------+------+---------------")
    recovered = []
    for b in range(16):
        corr = cpa_byte(traces_c, trace_ss, pt[:, b])
        peak = corr.max(axis=1)                    # đỉnh theo từng khóa đoán
        best = int(peak.argmax())
        recovered.append(best)
        rank = "-"
        if true_key is not None:
            order = np.argsort(-peak)
            rank = str(int(np.where(order == true_key[b])[0][0]))
        print(f" {b:3d} | 0x{best:02x} |   {peak[best]:.4f}   | {int(corr[best].argmax()):4d} | {rank}")

    rec = bytes(recovered)
    print(f"\nKhóa khôi phục: {rec.hex()}")
    if true_key is not None:
        ok = sum(x == y for x, y in zip(rec, true_key))
        print(f"Đúng {ok}/16 byte")


if __name__ == "__main__":
    main()
