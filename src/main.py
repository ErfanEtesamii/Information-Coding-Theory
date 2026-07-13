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
            print("فاز ۳ هنوز پیاده نشده.")
        elif choice == "4":
            print("فاز ۴ هنوز پیاده نشده.")
        elif choice == "5":
            print("فاز ۵ هنوز پیاده نشده.")
        else:
            print("گزینه نامعتبره، دوباره امتحان کن.")


if __name__ == "__main__":
    main()