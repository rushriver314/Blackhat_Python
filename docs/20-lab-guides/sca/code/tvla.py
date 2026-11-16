"""TVLA bậc 1 — Welch's t-test (fixed-vs-random) để phát hiện rò rỉ kênh kề.

TVLA là phương pháp ĐÁNH GIÁ: nó không khôi phục khóa, chỉ trả lời câu hỏi
"thiết bị có rò rỉ dữ liệu phụ thuộc bí mật hay không".

Quy ước: |t| > 4.5 tại bất kỳ điểm mẫu nào => có rò rỉ đáng kể (ngưỡng tiêu chuẩn).

Dữ liệu vào: hai nhóm trace đã đánh nhãn trong một file .npy nhãn (0 = random, 1 = fixed).

Ví dụ:
    python tvla.py --prefix tvla_sim
"""
import argparse
import numpy as np


def welch_t(a, b):
    """t-test Welch theo từng điểm mẫu giữa hai tập trace a và b."""
    na, nb = a.shape[0], b.shape[0]
    ma, mb = a.mean(axis=0), b.mean(axis=0)
    va, vb = a.var(axis=0, ddof=1), b.var(axis=0, ddof=1)
    denom = np.sqrt(va / na + vb / nb)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(denom > 0, (ma - mb) / denom, 0.0)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="tvla", help="tiền tố: <prefix>_traces.npy, <prefix>_group.npy")
    ap.add_argument("--threshold", type=float, default=4.5)
    ap.add_argument("--out", default=None, help="lưu mảng t ra file .npy (tùy chọn)")
    a = ap.parse_args()

    traces = np.load(f"{a.prefix}_traces.npy").astype(np.float64)
    group = np.load(f"{a.prefix}_group.npy").astype(np.uint8)
    fixed = traces[group == 1]
    random = traces[group == 0]
    print(f"Nhóm fixed: {fixed.shape[0]} trace | nhóm random: {random.shape[0]} trace | {traces.shape[1]} mẫu")

    t = welch_t(fixed, random)
    peak = int(np.abs(t).argmax())
    tmax = float(np.abs(t).max())
    n_over = int((np.abs(t) > a.threshold).sum())

    print(f"\n|t| lớn nhất = {tmax:.2f} tại mẫu {peak}")
    print(f"Số điểm mẫu vượt ngưỡng {a.threshold}: {n_over}")
    if tmax > a.threshold:
        print(">> KẾT LUẬN: CÓ rò rỉ đáng kể (|t| vượt ngưỡng).")
    else:
        print(">> KẾT LUẬN: KHÔNG phát hiện rò rỉ ở số trace này (chưa khẳng định là an toàn).")

    if a.out:
        np.save(a.out, t)
        print(f"Đã lưu mảng t vào {a.out}")


if __name__ == "__main__":
    main()
