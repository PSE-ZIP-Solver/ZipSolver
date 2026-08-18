from backend.puzzle_logic import Position, Board
from typing import List
import random


# number of results to generate
RESULTS = 1000

class BoardGenerator:
    """
    A combinatorial synthesis engine for generating fully validated, mathematically solvable puzzle layouts.

    Responsibility:
        Orchestrates the procedural generation of grid constraints. Sequentially applies graph traversal 
        algorithms, strict mathematical parity limits, and geometric bound mappings to reliably output 
        playable domain states without creating structural chokepoints.

    Implementation Details:
        Functions as a completely stateless factory component containing exclusively static mechanisms. 
        It sequentially pairs heuristic pathfinding operations (utilizing Depth-First Search combined 
        with Warnsdorff's heuristic) with strict spatial tracking arrays to synthesize mathematically 
        guaranteed continuous Hamiltonian loops prior to destructively injecting barriers or milestones.
    """
    @staticmethod
    def generate(boardSize: int, intermediateWaypoints: int, walls: int, numberBoards: int = 1) -> List[Board]:
        """
        Constructs a defined batch of procedurally generated, definitively solvable puzzle topologies.

        Args:
            boardSize: The absolute dimensional constraint dictating the generated square layout bounds.
            intermediateWaypoints: The exact target volume of milestone nodes to sequence between the origin and terminus.
            walls: The target quantity of physical barriers to distribute securely across the structural layout.
            numberBoards: The total volumetric batch size of distinct layouts requested.

        Returns:
            A sequence of synthesized, fully constructed topological domain proxies.

        Implementation Details:
            Triggers a continuous procedural loop allocating fresh domain instances natively. Successively synthesizes 
            origin and terminal pairs mapped to strict mathematical parity bounds, constructs a flawless Hamiltonian 
            sequence connecting them securely, and finally decorates the sequence natively with calculated volumes of 
            waypoints and structural walls. Safely continues allocation loops until the exact requested batch volume 
            is populated without failure.
        """
        results: List[Board] = [] 
        
        # genrate resulting boards
        while len(results) < numberBoards:
            board = Board(boardSize)
            start, end = BoardGenerator._generateTwoDistinctRandomPositions(boardSize)
            path = BoardGenerator._findHamiltonianPath(board, start, end)
            
            if path:
                board = BoardGenerator._placeRandomWaypoints(board, path, intermediateWaypoints)
                board = BoardGenerator._placeRandomWalls(board, path, walls)
                results.append(board)
        
        return results
    
    @staticmethod
    def _generateTwoDistinctRandomPositions(boardSize: int) -> tuple[Position, Position]:
        """
        Computes an origin and terminal pair mathematically guaranteed to permit complete contiguous traversal natively.

        Args:
            boardSize: The overriding physical dimension defining the active coordinate bounds.

        Returns:
            A coupled pairing securely mapping the localized mathematical starting point and the absolute terminus.

        Implementation Details:
            Randomly seeds discrete scalar indices and mathematically projects them directly into Cartesian coordinates 
            natively. Enforces strict checkerboard parity equations to unconditionally guarantee Hamiltonian logic: 
            explicitly requires mismatched parity for even-dimensional layouts, and strictly forces identical majority-color 
            parity alignments on odd constraints to definitively preclude mathematically fractured terminal subsets.
        """
        while True:
            # select two distinct 1D-indices for the square grid (0 to boardSize-1)
            idxStart, idxEnd = random.sample(range(boardSize * boardSize), 2)
            # project the two 1D-indices to 2D- coordinates 
            start = Position(idxStart % boardSize, idxStart // boardSize)
            end = Position(idxEnd % boardSize, idxEnd // boardSize)
            
            p_start = (start.getX + start.getY) % 2
            p_end = (end.getX + end.getY) % 2

            if boardSize % 2 == 0:
                # Even board: start and end must be on different "checkerboard colors"
                if p_start != p_end:
                    return start, end
            else:
                # Odd board: both must be on the majority color (parity 0) 
                # to allow a path through all cells
                if p_start == 0 and p_end == 0:
                    return start, end
    
    @staticmethod
    def _findHamiltonianPath(board: Board, start: Position, end: Position) -> List[Position]:
        """
        Executes an exhaustive heuristic search to map a perfectly contiguous, non-overlapping route across the complete grid.

        Args:
            board: The spatial topology actively targeted for combinatorial exhaustion.
            start: The definitively chosen mathematical origin point securely initializing the trace.
            end: The designated physical destination constrained as the ultimate loop closure.

        Returns:
            A chronologically ordered positional array fully encompassing the spatial volume natively, 
            or a null equivalent if exact mathematical exhaustion fails.

        Implementation Details:
            Leverages a deeply nested recursive Depth-First Search coupled directly with a strict Warnsdorff's 
            heuristic evaluation. Dynamically maps all available unvisited adjacencies natively and rigorously 
            sorts them by immediate local degree constraints (prioritizing traversal into sparse topological nodes). 
            Defensively aggressively prunes premature terminal closures directly to strictly guarantee total 
            volumetric saturation before safely unwinding and assembling the final positional track natively.
        """
        total_cells = board.getCellCount()
        visited = {start}
        path: List[Position] = [start]

        def get_degree(p: Position) -> int:
            """Warnsdorff's heuristic: count available unvisited neighbors."""
            count = 0
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nb = Position(p.getX + dx, p.getY + dy)
                if board.isInside(nb) and nb not in visited:
                    count += 1
            return count

        def _dfs(current: Position) -> bool:
            # Break Condition: hamiltonian path found
            if len(path) == total_cells:
                return current == end

            cx, cy = current.getX, current.getY
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = Position(cx + dx, cy + dy)
                if board.isInside(neighbor) and neighbor not in visited:
                    # only visit end as the last move 
                    if neighbor == end and len(path) < total_cells - 1:
                        continue
                    neighbors.append(neighbor)
            
            # Warnsdorff's heuristic: Sort neighbors by their degree (fewer neighbors first)
            # This speeds up finding the first valid path significantly
            neighbors.sort(key=get_degree)

            for neighbor in neighbors:
                visited.add(neighbor)
                path.append(neighbor)

                if _dfs(neighbor):
                    return True
                
                # backtracking
                path.pop()
                visited.remove(neighbor)

            return False

        # start dfs
        if _dfs(start):
            return list(path)
    
        return None
    
    @staticmethod
    def _placeRandomWaypoints(board: Board, path: List[Position], intermediateWaypoints: int) -> Board:
        """
        Decorates a mathematically verified traversal sequence with rigorously ordered structural checkpoints.

        Args:
            board: The localized layout environment securely receiving the sequenced milestone constraints.
            path: The unbroken spatial track safely mapping the complete topological truth.
            intermediateWaypoints: The precise requested count of internal markers to distribute sequentially.

        Returns:
            The mutated base domain actively possessing the ordered sequence milestones securely bound to it.

        Implementation Details:
            Extrapolates a purely scalar index pool representing all available spatial zones natively. Defensively 
            isolates the absolute origin and terminus bounds natively to prevent injection overlaps securely. 
            Selects randomized internal scalar targets, reconverts them directly to formal Cartesian vectors, 
            and forcefully sorts their injection by strictly mapping them against the chronological progression 
            of the underlying trajectory track to definitively ensure absolute sequential solvability safely.
        """
        # Generate positions of intermediate waypoints randomly
        
        # add all possible positions as 1D indices to allowed intermediate positions
        allowedIndices = set(range(board.getSize * board.getSize))
        # remove start and end from from allowed positions
        idxStart = path[0].getX + path[0].getY * board.getSize
        idxEnd = path[-1].getX + path[-1].getY * board.getSize
        allowedIndices.discard(idxStart)
        allowedIndices.discard(idxEnd) 
        # add random waypoints at allowed positions
        samples = min(intermediateWaypoints, len(allowedIndices))
        intermediateIndices = random.sample(list(allowedIndices), samples)
        # convert 1D indices to 2D positions
        intermediatePosition = {Position(idx % board.getSize, idx // board.getSize) for idx in intermediateIndices}
        # sort according to path
        intermediatePosition = [pos for pos in path if pos in intermediatePosition]
        
        # add waypoints

        # add waypoint at start of path
        board.addWaypoint(path[0], 1)
        # add intermediate waypoints
        nextOrder = 2
        for pos in intermediatePosition:
            board.addWaypoint(pos, nextOrder)
            nextOrder += 1
        # add waypoint at end of path
        board.addWaypoint(path[-1], nextOrder)
        
        return board
    
    @staticmethod
    def _placeRandomWalls(board: Board, path: List[Position], walls: int) -> Board:
        """
        Introduces randomized physical barriers exclusively into unutilized adjacent boundaries definitively preserving navigational logic.

        Args:
            board: The primary domain framework accepting the generated physical barrier injections natively.
            path: The strictly verified mathematical tracking sequence securely guaranteeing unbroken traversability.
            walls: The specific target volume of discrete spatial blockades to inject into the layout natively.

        Returns:
            The securely altered layout proxy definitively housing the new internal structural barriers natively.

        Implementation Details:
            Exhaustively mathematically evaluates all possible grid adjacencies natively to build a set of all theoretical 
            dimensional blockades securely formatted as sorted positional structures. Simultaneously evaluates the 
            locked contiguous trajectory mapping strictly utilized transit edges natively. Performs absolute mathematical 
            set-subtractions natively to explicitly strip trajectory-obstructing barrier variants from the pool securely, 
            before randomly sampling and cleanly injecting the resulting safe blockades securely.
        """
        # Find all possible wall positions
        # Store them in sorted tuples, for (A, B) to equal (B, A)
        possibleWalls = set()
        for y in range(board.getSize):
            for x in range(board.getSize):
                current = Position(x, y)
                # right neighbor
                if x + 1 < board.getSize:
                    right = Position(x + 1, y)
                    # sort by coordinate for unique ID
                    wall = tuple(sorted([current, right], key=lambda p: (p.getX, p.getY)))
                    possibleWalls.add(wall)
                # bottom neighbor
                if y + 1 < board.getSize:
                    down = Position(x, y + 1)
                    # sort by coordinate for unique ID
                    wall = tuple(sorted([current, down], key=lambda p: (p.getX, p.getY)))
                    possibleWalls.add(wall)

        # Find wall positions, that obstruct the path
        pathObstructingWalls = set()
        for i in range(len(path) - 1):
            current = path[i]
            next = path[i+1]
            wall = tuple(sorted([current, next], key=lambda p: (p.getX, p.getY)))
            pathObstructingWalls.add(wall)
 
        # Determine allowedWallPositions
        allowedWalls = list(possibleWalls - pathObstructingWalls)

        # Select wall from allowed walls randomly  
        samples = min(walls, len(allowedWalls))
        selectedWalls = random.sample(allowedWalls, samples)

        # Add walls to the board
        for wall in selectedWalls:
            board.addWall(wall[0], wall[1])

        return board