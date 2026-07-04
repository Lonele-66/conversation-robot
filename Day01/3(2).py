def sort_students(students, sort_key):
    return sorted(students, key=lambda x: x[sort_key])


def sort_students_advanced(students):
    return sorted(students, key=lambda x: (-x['score'], x['age']))


students_list = [
    {'name': 'Alice', 'age': 20, 'score': 85},
    {'name': 'Bob', 'age': 22, 'score': 92},
    {'name': 'Charlie', 'age': 20, 'score': 88},
    {'name': 'David', 'age': 21, 'score': 85},
]

print("=" * 50)
print("按成绩排序 (sort_key='score')")
print("=" * 50)
result = sort_students(students_list, 'score')
for student in result:
    print(student)

print("\n" + "=" * 50)
print("按姓名排序 (sort_key='name')")
print("=" * 50)
result = sort_students(students_list, 'name')
for student in result:
    print(student)

print("\n" + "=" * 50)
print("进阶排序 (成绩降序，年龄升序)")
print("=" * 50)
result = sort_students_advanced(students_list)
for student in result:
    print(student)