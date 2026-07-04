import random

choices = {
    0: "石头",
    1: "剪刀",
    2: "布"
}

player_input = input("请出拳（石头0、剪刀1、布2）：")

if player_input not in ['0', '1', '2']:
    print("输入无效，请输入0、1或2！")
else:
    player = int(player_input)
    computer = random.randint(0, 2)

    print(f"\n玩家出拳：{choices[player]}")
    print(f"电脑出拳：{choices[computer]}")

    if player == computer:
        print("结果：平局！")
    elif (player == 0 and computer == 1) or (player == 1 and computer == 2) or (player == 2 and computer == 0):
        print("结果：玩家赢！")
    else:
        print("结果：电脑赢！")