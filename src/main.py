import source
import huffman
import hamming
import channel
import evaluate


def show_menu():
    print("\n--- سیستم شبیه‌سازی هافمن/همینگ روی BSC ---")
    print("1) فاز ۱ - تعریف منبع و تولید دنباله")
    print("2) فاز ۲ - کدگذاری هافمن")
    print("3) فاز ۳ - کدگذاری کانال (همینگ)")
    print("4) فاز ۴ - شبیه‌سازی کانال و کدگشایی")
    print("5) فاز ۵ - ارزیابی و رسم نمودار")
    print("0) خروج")


def run_phase1():
    q = int(input("تعداد نمادهای منبع (q): "))
    probs_str = input(f"بردار احتمالات را با کاما جدا کن ({q} مقدار): ")

    try:
        probs = [float(x.strip()) for x in probs_str.split(",")]
    except ValueError:
        print("فرمت ورودی درست نیست، مقادیر باید عددی باشند.")
        return

    if len(probs) != q:
        print(f"تعداد مقادیر وارد شده ({len(probs)}) با q={q} مطابقت نداره.")
        return

    ok, msg = source.validate_probabilities(probs)
    if not ok:
        print("خطا:", msg)
        return

    N = int(input("طول رشته منبع (N): "))
    sequence = source.generate_sequence(probs, N)

    print(f"\nدنباله به طول {N} تولید شد.")
    print("۲۰ نماد اول:", [int(x) for x in sequence[:20]])

    stats = source.sequence_stats(sequence, probs)
    print("\nمقایسه فراوانی تجربی و تئوری هر نماد:")
    for symbol, data in sorted(stats.items()):
        print(f"  S{symbol}: تجربی={data['empirical']:.4f}  تئوری={data['theoretical']:.4f}")


def run_phase2():
    q = int(input("تعداد نمادهای منبع (q): "))
    probs_str = input(f"بردار احتمالات را با کاما جدا کن ({q} مقدار): ")

    try:
        probs = [float(x.strip()) for x in probs_str.split(",")]
    except ValueError:
        print("فرمت ورودی درست نیست، مقادیر باید عددی باشند.")
        return

    if len(probs) != q:
        print(f"تعداد مقادیر وارد شده ({len(probs)}) با q={q} مطابقت نداره.")
        return

    ok, msg = source.validate_probabilities(probs)
    if not ok:
        print("خطا:", msg)
        return

    L = int(input("مرتبه توسعه منبع (L) [پیش‌فرض ۱]: ") or "1")
    if L < 1:
        print("L باید حداقل ۱ باشه.")
        return

    N = int(input("طول رشته منبع برای تست (N): "))
    if N % L != 0:
        print(f"خطا: N={N} باید مضربی از L={L} باشد.")
        return

    sequence = source.generate_sequence(probs, N)
    seq_list = [int(x) for x in sequence]

    combos, ext_probs = huffman.extend_source(probs, L)
    codebook = huffman.build_huffman_codes(ext_probs)

    bits = huffman.encode_sequence(seq_list, L, codebook, combos)
    decoded = huffman.decode_bits(bits, codebook, combos)

    avg_len = huffman.average_length(ext_probs, codebook) / L
    H = huffman.entropy(probs)

    print(f"\nتعداد نمادهای منبع توسعه‌یافته (q^L): {len(combos)}")
    print(f"طول رشته باینری خروجی: {len(bits)} بیت (به‌جای {N * 8} بیت خام)")
    print(f"میانگین طول کد به‌ازای هر نماد اصلی: {avg_len:.4f} بیت")
    print(f"آنتروپی منبع: {H:.4f} بیت (کران پایین طبق شانون)")
    print("رمزگشایی با دنباله اصلی یکسان است:", decoded == seq_list)


def run_phase3():
    r = int(input("تعداد بیت‌های توازن (r): "))
    if r < 2:
        print("r باید حداقل ۲ باشه.")
        return

    n, k, R = hamming.hamming_params(r)
    print(f"\nn (طول کل بلوک) = {n}")
    print(f"k (طول بلوک پیام) = {k}")
    print(f"نرخ کد R = k/n = {R:.4f}")

    H = hamming.build_H(r)
    H_std = hamming.standard_form(H, r, n)
    G = hamming.build_G(H_std, k)

    print(f"\nماتریس H (فرم استاندارد، {n}x{r}):")
    for row in H_std:
        print("  ", row)

    print(f"\nماتریس G (فرم استاندارد، {k}x{n}):")
    for row in G:
        print("  ", row)

    bits_str = input("\nیک رشته باینری برای تست کدگذاری وارد کن (خالی=تولید خودکار): ").strip()
    if not bits_str:
        bits_str = "".join(str(b) for b in [1, 0, 1, 1, 0, 0, 1, 0, 1, 1])

    encoded, pad = hamming.encode_blocks(bits_str, G, k)
    print(f"\nرشته ورودی ({len(bits_str)} بیت): {bits_str}")
    print(f"بیت‌های پد شده: {pad}")
    print(f"رشته کدگذاری‌شده ({len(encoded)} بیت): {encoded}")


def run_phase4():
    r = int(input("تعداد بیت‌های توازن (r): "))
    if r < 2:
        print("r باید حداقل ۲ باشه.")
        return

    n, k, R = hamming.hamming_params(r)
    H = hamming.build_H(r)
    H_std = hamming.standard_form(H, r, n)
    G = hamming.build_G(H_std, k)

    bits_str = input("رشته باینری پیام برای تست (خالی = تولید تصادفی ۱۰۰ بیتی): ").strip()
    if not bits_str:
        import random
        bits_str = "".join(random.choice("01") for _ in range(100))

    p_str = input("احتمال خطای کانال P̄ (مثلا 0.05): ")
    p_error = float(p_str)
    if not (0 <= p_error < 0.5):
        print("P̄ باید در بازه [0, 0.5) باشه.")
        return

    # سناریو ۱: بدون کدگذاری کانال، دنباله مستقیم وارد کانال می‌شود
    received_raw, _ = channel.bsc_transmit(bits_str, p_error)
    errors_raw = sum(1 for a, b in zip(bits_str, received_raw) if a != b)

    # سناریو ۲: با کدگذاری کانال همینگ
    encoded, pad = hamming.encode_blocks(bits_str, G, k)
    received_encoded, _ = channel.bsc_transmit(encoded, p_error)
    channel_errors = sum(1 for a, b in zip(encoded, received_encoded) if a != b)

    decoded_bits, num_corrected, _ = channel.syndrome_decode(received_encoded, H_std, n, r, k)
    decoded_bits = decoded_bits[:len(bits_str)]  # حذف بیت‌های پد
    errors_remaining = sum(1 for a, b in zip(bits_str, decoded_bits) if a != b)

    print(f"\n--- سناریو ۱: بدون حفاظت کانال ---")
    print(f"بیت‌های خطادار از {len(bits_str)} بیت ارسالی: {errors_raw}")

    print(f"\n--- سناریو ۲: با کد همینگ (n={n}, k={k}, R={R:.4f}) ---")
    print(f"تعداد بلوک‌های ارسالی: {len(encoded) // n}")
    print(f"بیت‌های خطادار وارد شده توسط کانال: {channel_errors}")
    print(f"بلوک‌های تصحیح‌شده توسط کدگشا: {num_corrected}")
    print(f"بیت‌های خطای باقی‌مانده بعد از تصحیح: {errors_remaining}")


def run_phase5():
    q = int(input("تعداد نمادهای منبع (q): "))
    probs_str = input(f"بردار احتمالات را با کاما جدا کن ({q} مقدار): ")

    try:
        probs = [float(x.strip()) for x in probs_str.split(",")]
    except ValueError:
        print("فرمت ورودی درست نیست.")
        return

    if len(probs) != q:
        print(f"تعداد مقادیر وارد شده ({len(probs)}) با q={q} مطابقت نداره.")
        return

    ok, msg = source.validate_probabilities(probs)
    if not ok:
        print("خطا:", msg)
        return

    L = int(input("مرتبه توسعه منبع (L) [پیش‌فرض ۱]: ") or "1")
    r = int(input("تعداد بیت‌های توازن کد همینگ (r): "))

    N = int(input("طول دنباله منبع برای شبیه‌سازی (N) [پیشنهاد: عدد بزرگ مثل 5000]: "))
    if N % L != 0:
        print(f"خطا: N باید مضربی از L={L} باشه.")
        return

    num_points = int(input("تعداد نقاط محور SNR [پیش‌فرض ۱۲]: ") or "12")

    n, k, R = hamming.hamming_params(r)
    H = hamming.build_H(r)
    H_std = hamming.standard_form(H, r, n)
    G = hamming.build_G(H_std, k)

    combos, ext_probs = huffman.extend_source(probs, L)
    codebook = huffman.build_huffman_codes(ext_probs)

    sequence = source.generate_sequence(probs, N)
    seq_list = [int(x) for x in sequence]

    huffman_bits = huffman.encode_sequence(seq_list, L, codebook, combos)
    encoded, pad = hamming.encode_blocks(huffman_bits, G, k)

    # مقادیر p به‌صورت لگاریتمی بین یک مقدار کوچک تا نزدیک ۰.۵ پخش می‌شن
    # تا هم ناحیه‌ی خطای زیاد و هم ناحیه‌ی سقوط منحنی پوشش داده بشه
    p_min, p_max = 1e-3, 0.49
    if num_points == 1:
        p_values = [p_max]
    else:
        p_values = [p_min * (p_max / p_min) ** (i / (num_points - 1)) for i in range(num_points)]

    print(f"\nطول رشته کدگذاری‌شده (N''): {len(encoded)} بیت")
    print(f"{'p':>10} {'SNR(dB)':>10} {'Pe':>14}")

    pe_values = []
    snr_values = []
    for p in p_values:
        received, _ = channel.bsc_transmit(encoded, p)
        _, _, corrected_full = channel.syndrome_decode(received, H_std, n, r, k)

        pe = evaluate.bit_error_rate(encoded, corrected_full)
        snr = evaluate.snr_db(p)

        pe_values.append(pe)
        snr_values.append(snr)
        print(f"{p:>10.4f} {snr:>10.2f} {pe:>14.6f}")

    p_star = evaluate.shannon_threshold(R)
    snr_star = evaluate.snr_db(p_star)
    print(f"\nنرخ کد R = {R:.4f}")
    print(f"آستانه شانون: p* = {p_star:.6f}  ->  SNR* = {snr_star:.2f} dB")

    # مقادیری که Pe صفر شدن رو برای نمایش روی مقیاس لگاریتمی محدود می‌کنیم
    pe_values_for_plot = [max(pe, 1e-6) for pe in pe_values]

    save_path = "ber_curve.png"
    evaluate.plot_results(snr_values, pe_values_for_plot, snr_star, save_path)
    print(f"\nنمودار در فایل {save_path} ذخیره شد.")


def main():
    while True:
        show_menu()
        choice = input("گزینه مورد نظر رو وارد کن: ")

        if choice == "0":
            break
        elif choice == "1":
            run_phase1()
        elif choice == "2":
            run_phase2()
        elif choice == "3":
            run_phase3()
        elif choice == "4":
            run_phase4()
        elif choice == "5":
            run_phase5()
        else:
            print("گزینه نامعتبره، دوباره امتحان کن.")


if __name__ == "__main__":
    main()