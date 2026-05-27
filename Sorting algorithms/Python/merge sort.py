import random, time


def mergeSort(arr: list):
    if len(arr) > 1:
        mid = len(arr) // 2
        left, right = arr[:mid], arr[mid:]
        mergeSort(left)
        mergeSort(right)

    leftIndex = rightIndex = mainIndex = 0
    while leftIndex < len(left) and rightIndex < len(right):
        if left[leftIndex] <= right[rightIndex]:
            arr[mainIndex] = left[leftIndex]
            leftIndex += 1
        else:
            arr[mainIndex] = right[rightIndex]
            rightIndex += 1
        mainIndex += 1

    while leftIndex < len(left):
        arr[mainIndex] = left[leftIndex]
        leftIndex += 1
        mainIndex += 1

    while rightIndex < len(right):
        arr[mainIndex] = right[rightIndex]
        rightIndex += 1
        mainIndex += 1


array = [i for i in range(10000)]
random.shuffle(array)
print(f"Unsorted array\n{array}")
startTime = time.time()
mergeSort(array)
endTime = time.time()
print(f"Sorted array\n{array}")

duration = endTime - startTime
print(f"\nDuration: {duration}seconds")
