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


def main():
    while True:
        show_menu()
        choice = input("گزینه مورد نظر رو وارد کن: ")

        if choice == "0":
            break
        elif choice == "1":
            print("فاز ۱ هنوز پیاده نشده.")
        elif choice == "2":
            print("فاز ۲ هنوز پیاده نشده.")
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