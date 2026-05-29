import random, time


def bubbleSort(arr: list):
    n = len(arr)
    for i in range(n):
        sorted = True

        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                sorted = False

        if sorted == True:
            break


array = [i for i in range(10000)]
random.shuffle(array)
print(f"Unsorted array\n{array}")
startTime = time.time()
bubbleSort(array)
endTime = time.time()
print(f"Sorted array\n{array}")

duration = endTime - startTime
print(f"\nDuration: {duration}seconds")
