from datetime import datetime

while True:
    pet_name = input("请输入你的宠物名字: ")
    diary_content = input("请输入今天的日记内容: ")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    diary_line = f"{current_time} - [{pet_name}]: {diary_content}\n"

    try:
        with open("pet_diary.txt", "a", encoding="utf-8") as file:
            file.write(diary_line)
        print("日记已成功保存到 pet_diary.txt！")
    except Exception:
        print("糟糕！无法写入日记。请检查文件权限或磁盘空间。")

    continue_input = input("是否要再写一条日记？(y/n): ")
    if continue_input.lower() != 'y':
        print("好的，下次再见！")
        break