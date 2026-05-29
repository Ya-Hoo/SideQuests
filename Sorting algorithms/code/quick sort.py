import random, time


def partition(arr: list, startIndex: int, endIndex: int):
    pivot = arr[(startIndex + endIndex) // 2]
    i, j = startIndex - 1, endIndex + 1

    while True:
        i += 1
        while arr[i] < pivot:
            i += 1

        j -= 1
        while arr[j] > pivot:
            j -= 1

        if i >= j:
            return j

        arr[i], arr[j] = arr[j], arr[i]


def quickSort(arr, startIndex, endIndex):
    if startIndex < endIndex:
        partitioningIndex = partition(arr, startIndex, endIndex)
        quickSort(arr, startIndex, partitioningIndex)
        quickSort(arr, partitioningIndex + 1, endIndex)


array = [i for i in range(10000)]
random.shuffle(array)
print(f"Unsorted array\n{array}")
startTime = time.time()
quickSort(array, 0, len(array) - 1)
endTime = time.time()
print(f"Sorted array\n{array}")

duration = endTime - startTime
print(f"\nDuration: {duration}seconds")
