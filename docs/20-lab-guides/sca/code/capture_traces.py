"""Thu power trace AES-128 bằng ChipWhisperer-Lite (target STM32F3, CWLITEARM).

Yêu cầu:
  - chipwhisperer 5.x hoặc 6.x  (pip install chipwhisperer)
  - Đã build firmware: hardware/victims/firmware/simpleserial-aes
        make PLATFORM=CWLITEARM CRYPTO_TARGET=TINYAES128C SS_VER=SS_VER_2_1

Ví dụ:
    python capture_traces.py --hex simpleserial-aes-CWLITEARM.hex --n 2000 --out lab1

Chỉ chạy trên target học tập hoặc thiết bị đã được phép (xem 00-policies/authorization-scope.md).
"""
import argparse
import numpy as np
import chipwhisperer as cw
from tqdm import trange


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hex", help="đường dẫn firmware .hex (bỏ qua nếu đã nạp)")
    ap.add_argument("--n", type=int, default=2000, help="số trace cần thu")
    ap.add_argument("--samples", type=int, default=5000, help="số mẫu ADC mỗi trace")
    ap.add_argument("--out", default="lab1", help="tiền tố tên file đầu ra")
    ap.add_argument("--ss1", action="store_true", help="dùng SimpleSerial v1 thay vì v2")
    a = ap.parse_args()

    scope = cw.scope()
    target_type = cw.targets.SimpleSerial if a.ss1 else cw.targets.SimpleSerial2
    target = cw.target(scope, target_type)
    try:
        scope.default_setup()
        scope.adc.samples = a.samples

        if a.hex:
            cw.program_target(scope, cw.programmers.STM32FProgrammer, a.hex)

        ktp = cw.ktp.Basic()          # khóa cố định, plaintext ngẫu nhiên
        traces, textin, textout = [], [], []
        key = None
        fails = 0

        for _ in trange(a.n, desc="Thu trace"):
            key, text = ktp.next()
            tr = cw.capture_trace(scope, target, text, key)
            if tr is None:            # timeout hoặc lỗi giao tiếp
                fails += 1
                continue
            traces.append(tr.wave)
            textin.append(list(tr.textin))
            textout.append(list(tr.textout))

        np.save(f"{a.out}_traces.npy", np.asarray(traces, dtype=np.float32))
        np.save(f"{a.out}_textin.npy", np.asarray(textin, dtype=np.uint8))
        np.save(f"{a.out}_textout.npy", np.asarray(textout, dtype=np.uint8))
        # Khóa chỉ lưu để tự kiểm tra kết quả, KHÔNG commit (đã chặn *.npy trong .gitignore)
        np.save(f"{a.out}_key.npy", np.frombuffer(bytes(key), dtype=np.uint8))

        print(f"Xong: {len(traces)} trace, {fails} lần lỗi. Tiền tố file: {a.out}_*")
    finally:
        scope.dis()
        target.dis()


if __name__ == "__main__":
    main()
