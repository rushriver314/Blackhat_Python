"""Thu power trace AES-128 bằng ChipWhisperer-Lite (target STM32F3, CWLITEARM).

Yêu cầu:
  - chipwhisperer 5.x hoặc 6.x  (pip install chipwhisperer)
  - Đã build firmware: hardware/victims/firmware/simpleserial-aes
        make PLATFORM=CWLITEARM CRYPTO_TARGET=TINYAES128C SS_VER=SS_VER_2_1

Hai chế độ:
  - CPA (mặc định): plaintext ngẫu nhiên, khóa cố định.
        python capture_traces.py --hex aes.hex --n 2000 --out lab1
  - TVLA (--tvla): xen kẽ ngẫu nhiên nhóm fixed (plaintext cố định) và nhóm random,
    cùng một khóa. Lưu thêm <out>_group.npy (1 = fixed, 0 = random) cho tvla.py.
        python capture_traces.py --hex aes.hex --n 4000 --out lab2 --tvla

Chỉ chạy trên target học tập hoặc thiết bị đã được phép (xem 00-policies/authorization-scope.md).
"""
import argparse
import numpy as np

# Plaintext cố định dùng cho nhóm "fixed" của TVLA (giá trị công khai, không phải bí mật).
# Giống hằng số trong simulate_tvla.py để hai script nhất quán.
TVLA_FIXED_PT = bytes.fromhex("da39a3ee5e6b4b0d3255bfef95601890")


def plan_tvla_groups(n, seed=None):
    """Trả về mảng nhãn nhóm (1 = fixed, 0 = random) xen kẽ ngẫu nhiên.

    Tách riêng khỏi phần phần cứng để kiểm thử được mà không cần ChipWhisperer.
    """
    rng = np.random.default_rng(seed)
    return (rng.random(n) < 0.5).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hex", help="đường dẫn firmware .hex (bỏ qua nếu đã nạp)")
    ap.add_argument("--n", type=int, default=2000, help="số trace cần thu")
    ap.add_argument("--samples", type=int, default=5000, help="số mẫu ADC mỗi trace")
    ap.add_argument("--out", default="lab1", help="tiền tố tên file đầu ra")
    ap.add_argument("--ss1", action="store_true", help="dùng SimpleSerial v1 thay vì v2")
    ap.add_argument("--tvla", action="store_true",
                    help="chế độ TVLA: xen kẽ fixed/random, lưu thêm _group.npy")
    ap.add_argument("--seed", type=int, default=None, help="seed cho việc chia nhóm TVLA")
    a = ap.parse_args()

    import chipwhisperer as cw   # import ở đây để test plan_tvla_groups không cần phần cứng
    from tqdm import trange

    groups = plan_tvla_groups(a.n, a.seed) if a.tvla else None
    fixed_pt = bytearray(TVLA_FIXED_PT)

    scope = cw.scope()
    target_type = cw.targets.SimpleSerial if a.ss1 else cw.targets.SimpleSerial2
    target = cw.target(scope, target_type)
    try:
        scope.default_setup()
        scope.adc.samples = a.samples

        if a.hex:
            cw.program_target(scope, cw.programmers.STM32FProgrammer, a.hex)

        ktp = cw.ktp.Basic()          # khóa cố định, plaintext ngẫu nhiên
        traces, textin, textout, group_kept = [], [], [], []
        key = None
        fails = 0

        for i in trange(a.n, desc="Thu trace"):
            key, text = ktp.next()
            if a.tvla and groups[i] == 1:
                text = bytearray(fixed_pt)   # nhóm fixed: ghi đè bằng plaintext cố định
            tr = cw.capture_trace(scope, target, text, key)
            if tr is None:            # timeout hoặc lỗi giao tiếp
                fails += 1
                continue
            traces.append(tr.wave)
            textin.append(list(tr.textin))
            textout.append(list(tr.textout))
            if a.tvla:
                group_kept.append(int(groups[i]))   # chỉ giữ nhãn của trace thu thành công

        np.save(f"{a.out}_traces.npy", np.asarray(traces, dtype=np.float32))
        np.save(f"{a.out}_textin.npy", np.asarray(textin, dtype=np.uint8))
        np.save(f"{a.out}_textout.npy", np.asarray(textout, dtype=np.uint8))
        # Khóa chỉ lưu để tự kiểm tra kết quả, KHÔNG commit (đã chặn *.npy trong .gitignore)
        np.save(f"{a.out}_key.npy", np.frombuffer(bytes(key), dtype=np.uint8))
        if a.tvla:
            g = np.asarray(group_kept, dtype=np.uint8)
            np.save(f"{a.out}_group.npy", g)
            print(f"TVLA: {int(g.sum())} fixed / {len(g) - int(g.sum())} random. "
                  f"Chạy: python tvla.py --prefix {a.out}")

        print(f"Xong: {len(traces)} trace, {fails} lần lỗi. Tiền tố file: {a.out}_*")
    finally:
        scope.dis()
        target.dis()


if __name__ == "__main__":
    main()
