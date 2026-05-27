# A-star-pathfiding

A* is a graph traversal and path search algorithm. It achieves better performance by using heuristics to guide its search, however, one major drawback is that it has to store every node generated in memory. 

## Mechanism

A* is formulated in terms of weighted graphs: starting from a specific starting node of a graph, it aims to find a path to the given goal node having the smallest cost. It does this by maintaining a tree of paths originating at the start node and extending those paths one edge at a time until its termination criterion is satisfied.

To determine the branch that it wants to visit, it will calculate the path that minimises

> $f(n)=g(n)+h(n)$  

where:  
> $g(n)$ = cost of moving from the start node to node $n$  
> $h(n)$ = heuristic function that estimates the cost of moving from node $n$ to the goal

## Heuristics

The heuristic function, $h(n)$, that I used in my program is called the Euclidean distance, which estimates the cost by using the Pythagoras theorem.  
```Python
def heuristic(node, goal):
    dx = abs(node.x - goal.x)
    dy = abs(node.y - goal.y)
    return math.sqrt(dx*dx + dy*dy)
```

## Cost moving between nodes

Since the map is 2D grid, the cost of moving to horizontally or vertically adjacent node is $1$ while the cost of moving to a diagonally adjacent node is $\sqrt2$


## Implementations

### Nodes
Each node object will store its position, state, $f(n)$, $g(n)$, $h(n)$. It will also keep a reference to its neighbors and parent's coordinate. 

### The algorithm
```
precompute the h_cost for all nodes
set g_cost of all nodes except for the start node to infinity

FRONTIER  //the set of nodes to be evaluated
EXPLORED  //the set of nodes already evaluated
add the start node to FRONTIER

loop until FRONTIER is empty
    current = node in FRONTIER with lowest f_cost
    remove current from FRONTIER
    add current to EXPLORED

    if current is goal //path found
        return

    for each neighbor of current node
        if neighbor in explored
            skip to next neighbor

        calculate new g_cost of neighbor

        if new g_cost to neighbor is shorter OR neighbor is not in FRONTIER
            calculate f_cost
            set parent of neighbor to current
            if neighbor not in FRONTIER
                add neighbor to FRONTIER
```

### Path tracing
Since each node keeps a reference to its parents, we can trace the path by starting with the goal node and keep moving to the parents until we reach the start node. 

## Reflection

* May be I can create a proper maze-making algorithm (another project idea!) and integrate A* into it which would be pretty cool
* Is there a way to implement A* without storing each node as an object? cus this will reduce the memory usage of this algorithm so much
* Implement A* on a non-grid map (?!)
