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


print("=" * 50)
print("回文检查器测试")
print("=" * 50)
print(f'is_palindrome("A man, a plan, a canal: Panama") = {is_palindrome("A man, a plan, a canal: Panama")}')
print(f'is_palindrome("race a car") = {is_palindrome("race a car")}')
print(f'is_palindrome("你好好你") = {is_palindrome("你好好你")}')
print(f'is_palindrome("hello") = {is_palindrome("hello")}')