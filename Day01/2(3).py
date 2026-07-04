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


print("=" * 50)
print("密码强度检查器测试")
print("=" * 50)
print(f'check_password_strength("12345") = "{check_password_strength("12345")}"')
print(f'check_password_strength("abcdefgh") = "{check_password_strength("abcdefgh")}"')
print(f'check_password_strength("abc123XYZ") = "{check_password_strength("abc123XYZ")}"')
print(f'check_password_strength("Password123!") = "{check_password_strength("Password123!")}"')
print(f'check_password_strength("Password") = "{check_password_strength("Password")}"')
print(f'check_password_strength("pass123") = "{check_password_strength("pass123")}"')