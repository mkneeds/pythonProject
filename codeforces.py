n = int(input())
names = []

for i in range(n):
    name = input().strip()
    if name not in names:
        names.append(name)
        print("OK")
    else:
        left = 1
        right = len(names) - 1
        while left <= right:
            mid = (left + right) // 2
            if names[mid] == name:
                left = mid + 1
            else:
                right = mid - 1
        new_name = name + str(left)
        while new_name in names:
            left += 1
            new_name = name + str(left)
        names.append(new_name)
        print(new_name)
