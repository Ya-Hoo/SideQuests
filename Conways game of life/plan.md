# Future plans (optimisations)

## Map

| Improvement  | Version |
| ------------- | ---: |
| Instead of iterating through every single cell, we should skip over dead cells with no neighbors  | 2.0 |
| Maybe try to use a one-dimension array only with all the rows joined together into one single array  | n/a |
| Mapless approach: store only the live cells and then write a function that fills the rest of the map with dead cells  | 2.1 |
| Quadtree but im not smart enough yet so gotta wait  | n/a  |
| Divide maps into halves and halves, check if the portion of map is empty (sum of values), if yes then skip else evaluate | n/a |
| Keep track of changed cells --> only need to iterate over those | n/a |

## Cells

| Improvement  | Version |
| ------------- | ---: |
| Represent each cell as a 4-bit integer, with the integer representing the total number of neighbors (including itself) that the cell has.  | n/a |
| Each cell is just a binary integer: 1 = alive, 0 = dead  | 2.0 |
| Better method of counting neighbors | 2.0 |

## Patterns and rendering

| Improvement  | Version |
| ------------- | ---: |
| Make an RLE decoder to import patterns directly from the database of [Conway Life Wiki](https://conwaylife.com/wiki/)  | 1.1 |
| Maybe try render using matplotlib, pygame or other libraries  | n/a |
| For mapless approach - write a function to fill remaining with dead cells | 2.1 |

## Other

| Improvement  | Version |
| ------------- | ---: |
| Find still life objects and skip over them when calculating the next generation of the world  | n/a |
| Find oscillators and render them using pre-calculated results  | n/a |
| Certain patterns, such as the glider are quite predeterminate, therefore we can also pre-celculate their results  | n/a |
