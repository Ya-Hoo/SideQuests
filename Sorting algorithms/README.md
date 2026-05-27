# Sorting Algorithms
A Sorting Algorithm is used to rearrange a given array or list of elements according to a comparison operator on the elements.

## Comparison sorts

### Bubble sort
*Algorithm*  
1. Starting from the first index, compare the item at that index and the adjacent item.
2. If they are in the wrong order, swap.
3. Increase the index by one and repeat step 1 and 2.
4. The above process goes on until the last element.
5. Steps 1 to 4 is repeated until every element is sorted.

*Flowchart*  
![bubble sort flowchart](<flowchart/bubble sort flowchart.png>)

*Performance*  
Time complexity: O($n^2$)  
Space complexity: O($1$)


### Merge sort
*Algorithm*  
1. Recursively divide the array into two equal halves until the length of the subarrays equal 1.
2. Compare the element of each array and then combine them into another array in the correct order.
3. Ends when all of the items are successfully merged back all together.

*Flowchart*  
![merge sort flowchart](<flowchart/merge sort flowchart.png>)

*Performance*  
Time complexity: O($n\log n$)  
Space complexity: O($n$)


### Quick sort
*Algorithm*  
1. Select an item in the array as the pivot
2. Set $i$ to the starting index of the array and $j$ to the ending index of the array
3. Increase $i$ by 1 until the item at that index is larger than the pivot
4. Decrease $j$ by 1 until the item at that index is smaller than the pivot
5. After that, if $i \ge j$ then return $j$, otherwise swap the element at $i$ and at $j$ then repeat steps 1 to 4
6. Steps 1 to 5 is done recursively for the array on either side of the pivot

*Flowchart*  
![Alt text](<flowchart/quick sort flowchart.png>)

*Performance*  
Time complexity: O($n\log n$)  
Space complexity: O($\log n$)

## Non-comparison sorts

### Radix sort
*Algorithm*  
1. Find the largest element in the array and get its length
2. Set $n$ equals to 1
3. Sort the elements based on the $n^{th}$ digit
4. Add 1 to $n$
5. Repeat steps 1 to 4 until $n$ equals to the length of the largest number

*Flowchart*  
![Alt text](<flowchart/radix sort flowchart.png>)

*Performance*  
Time complexity: O($nw$)  
Space complexity: O($w+n$)