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


def is_palindrome(s):
    cleaned = []
    for char in s.lower():
        if char.isalnum():
            cleaned.append(char)
    cleaned = ''.join(cleaned)

    if not cleaned:
        return True

    left = 0
    right = len(cleaned) - 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1
    return True


def check_password_strength(password):
    has_lower = False
    has_upper = False
    has_digit = False
    has_special = False

    for char in password:
        if char.islower():
            has_lower = True
        elif char.isupper():
            has_upper = True
        elif char.isdigit():
            has_digit = True
        else:
            has_special = True

    type_count = sum([has_lower, has_upper, has_digit, has_special])

    if type_count == 1:
        return "弱"
    elif len(password) >= 8 and type_count >= 3:
        return "强"
    else:
        return "中"


print("\n" + "=" * 50)
print("回文检查器测试")
print("=" * 50)
print(f'is_palindrome("A man, a plan, a canal: Panama") = {is_palindrome("A man, a plan, a canal: Panama")}')
print(f'is_palindrome("race a car") = {is_palindrome("race a car")}')
print(f'is_palindrome("你好好你") = {is_palindrome("你好好你")}')
print(f'is_palindrome("hello") = {is_palindrome("hello")}')

print("\n" + "=" * 50)
print("密码强度检查器测试")
print("=" * 50)
print(f'check_password_strength("12345") = "{check_password_strength("12345")}"')
print(f'check_password_strength("abcdefgh") = "{check_password_strength("abcdefgh")}"')
print(f'check_password_strength("abc123XYZ") = "{check_password_strength("abc123XYZ")}"')
print(f'check_password_strength("Password123!") = "{check_password_strength("Password123!")}"')
print(f'check_password_strength("Password") = "{check_password_strength("Password")}"')
print(f'check_password_strength("pass123") = "{check_password_strength("pass123")}"')