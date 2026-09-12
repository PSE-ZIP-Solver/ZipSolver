import random
import sys
from typing import List
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position

class UnsolvableBoardGenerator:
    """
    Manages the programmatic mass-generation of structurally unresolvable puzzle boards.

    Responsibility:
        Serves as a robust utility to rapidly synthesize vast datasets of invalid puzzle permutations
        specifically engineered to rigorously stress-test the false positive rates of reinforcement
        learning solvers.

    Implementation Details:
        Harnesses five mathematically absolute graph theory constraints:
        1. Bipartite Parity Mismatch (Color parity exhaustion)
        2. Topological Isolation (Trapped cell)
        3. Degree Violation (Three or more dead-end cells)
        4. Graph Fragmentation (Complete bisection)
        5. Sequence Trap (Bottleneck traversal contradiction)
        
        Operations are highly optimized using spatial coordinate mathematics to maintain an
        extremely fast manageable runtime, easily generating tens of thousands of instances.
    """

    def generateUnsolvableBoards(
        self,
        boardSize: int,
        numberOfMaximumWaypoints: int,
        numberOfMaximumWalls: int,
        numberOfBoards: int
    ) -> List[Board]:
        """
        Mass-produces a specified volume of mathematically unsolvable puzzle configurations.

        Args:
            boardSize: The uniform numerical span defining the grid (strictly 6, 7, or 8).
            numberOfMaximumWaypoints: The uppermost limit of milestone constraints to sequence.
            numberOfMaximumWalls: The maximum allowable impassable internal barriers to scatter.
            numberOfBoards: The absolute total number of unique invalid boards to generate.

        Returns:
            A populated list comprising the newly generated, definitively unresolvable Board instances.
        """
        if boardSize not in [6, 7, 8]:
            raise ValueError("Invalid configuration: boardSize must be strictly restricted to 6, 7, or 8.")

        generated_boards: List[Board] = []
        percent_step = max(1, numberOfBoards // 100)

        # Determine available strategies dynamically based on user limits to prevent parameter violation
        available_strategies = ["PARITY"]
        if numberOfMaximumWalls >= 4:
            available_strategies.append("INACCESSIBLE")
        if numberOfMaximumWalls >= 9:
            available_strategies.append("DEAD_END")
        if numberOfMaximumWalls >= boardSize:
            available_strategies.append("BISECTION")
        if numberOfMaximumWalls >= boardSize - 1 and numberOfMaximumWaypoints >= 3:
            available_strategies.append("SEQUENCE_TRAP")

        for i in range(numberOfBoards):
            board = Board(boardSize)
            all_positions = list(board.getAllPositions())
            
            # Dynamically select constraints
            max_wp = max(2, min(numberOfMaximumWaypoints, board.getCellCount()))
            num_waypoints = random.randint(2, max_wp)
            target_walls = random.randint(0, numberOfMaximumWalls)
            
            strategy = random.choice(available_strategies)
            walls_added_by_strategy = 0
            wp_positions = []

            # ==========================================
            # STRATEGY 1: INACCESSIBLE (Topological Trap)
            # ==========================================
            if strategy == "INACCESSIBLE":
                trap_pos = random.choice(all_positions)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    neighbor = Position(trap_pos.getX + dx, trap_pos.getY + dy)
                    if board.isInside(neighbor):
                        board.addWall(trap_pos, neighbor)
                        walls_added_by_strategy += 1

                wp_positions = random.sample(all_positions, num_waypoints)
                if trap_pos not in wp_positions:
                    wp_positions[0] = trap_pos
                    random.shuffle(wp_positions)

            # ==========================================
            # STRATEGY 2: PARITY (Bipartite Mismatch)
            # ==========================================
            elif strategy == "PARITY":
                parity0 = [p for p in all_positions if (p.getX + p.getY) % 2 == 0]
                parity1 = [p for p in all_positions if (p.getX + p.getY) % 2 == 1]

                if len(parity0) == len(parity1):
                    chosen_parity = random.choice([parity0, parity1])
                    start_pos, end_pos = random.sample(chosen_parity, 2)
                else:
                    minority = parity1 if len(parity0) > len(parity1) else parity0
                    start_pos = random.choice(minority)
                    remaining_for_end = [p for p in all_positions if p != start_pos]
                    end_pos = random.choice(remaining_for_end)

                wp_positions.append(start_pos)
                remaining_for_mid = [p for p in all_positions if p != start_pos and p != end_pos]
                wp_positions.extend(random.sample(remaining_for_mid, num_waypoints - 2))
                wp_positions.append(end_pos)

            # ==========================================
            # STRATEGY 3: DEAD END (Degree Violation)
            # ==========================================
            elif strategy == "DEAD_END":
                # Sample grid spacing of 2 to guarantee traps do not share borders/walls
                valid_centers = [Position(x, y) for x in range(0, boardSize, 2) for y in range(0, boardSize, 2)]
                trap_centers = random.sample(valid_centers, 3)
                
                for trap in trap_centers:
                    neighbors = []
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        pos = Position(trap.getX + dx, trap.getY + dy)
                        if board.isInside(pos):
                            neighbors.append(pos)
                    
                    # FIX: Dynamically block all neighbors EXCEPT one.
                    # Corners (2 neighbors) -> block 1. Edges (3) -> block 2. Center (4) -> block 3.
                    num_to_block = len(neighbors) - 1
                    to_block = random.sample(neighbors, num_to_block)
                    
                    for n in to_block:
                        if not board.hasWallBetween(trap, n):
                            board.addWall(trap, n)
                            walls_added_by_strategy += 1
                            
                wp_positions = random.sample(all_positions, num_waypoints)
                
            # ==========================================
            # STRATEGY 4: BISECTION (Graph Fragmentation)
            # ==========================================
            elif strategy == "BISECTION":
                is_horizontal = random.choice([True, False])
                cut_idx = random.randint(0, boardSize - 2)
                
                for j in range(boardSize):
                    if is_horizontal:
                        board.addWall(Position(j, cut_idx), Position(j, cut_idx + 1))
                    else:
                        board.addWall(Position(cut_idx, j), Position(cut_idx + 1, j))
                    walls_added_by_strategy += 1
                    
                wp_positions = random.sample(all_positions, num_waypoints)

            # ==========================================
            # STRATEGY 5: SEQUENCE TRAP (Bottleneck Contradiction)
            # ==========================================
            elif strategy == "SEQUENCE_TRAP":
                num_waypoints = max(3, num_waypoints)
                is_horizontal = random.choice([True, False])
                cut_idx = random.randint(1, boardSize - 2)
                gap_idx = random.randint(0, boardSize - 1)
                
                top_half = []
                bottom_half = []
                
                # Build the bisecting wall with exactly ONE gap
                for j in range(boardSize):
                    if j != gap_idx:
                        if is_horizontal:
                            board.addWall(Position(j, cut_idx), Position(j, cut_idx + 1))
                        else:
                            board.addWall(Position(cut_idx, j), Position(cut_idx + 1, j))
                        walls_added_by_strategy += 1
                        
                # Geographically split the coordinate space
                for p in all_positions:
                    if is_horizontal:
                        if p.getY <= cut_idx: top_half.append(p)
                        else: bottom_half.append(p)
                    else:
                        if p.getX <= cut_idx: top_half.append(p)
                        else: bottom_half.append(p)
                        
                # Trap the sequence (Top -> Bottom -> Top) forcing a double bridge-cross
                wp1, wp3 = random.sample(top_half, 2)
                wp2 = random.choice(bottom_half)
                wp_positions = [wp1, wp2, wp3]
                
                remaining_pos = [p for p in all_positions if p not in wp_positions]
                if num_waypoints > 3:
                    wp_positions.extend(random.sample(remaining_pos, num_waypoints - 3))

            # ==========================================
            # FINALIZE CONSTRAINTS & VISUAL SCATTERING
            # ==========================================
            for idx, pos in enumerate(wp_positions):
                board.addWaypoint(pos, idx + 1)

            # Mask the unsolvability by filling up remaining permitted walls with random noise
            remaining_walls_to_add = target_walls - walls_added_by_strategy
            if remaining_walls_to_add > 0:
                potential_walls = []
                for x in range(boardSize):
                    for y in range(boardSize):
                        pA = Position(x, y)
                        pRight = Position(x + 1, y)
                        pDown = Position(x, y + 1)
                        if board.isInside(pRight) and not board.hasWallBetween(pA, pRight):
                            potential_walls.append((pA, pRight))
                        if board.isInside(pDown) and not board.hasWallBetween(pA, pDown):
                            potential_walls.append((pA, pDown))

                walls_to_add = min(remaining_walls_to_add, len(potential_walls))
                if walls_to_add > 0:
                    chosen_walls = random.sample(potential_walls, walls_to_add)
                    for pA, pB in chosen_walls:
                        board.addWall(pA, pB)

            generated_boards.append(board)

            # Report execution progress
            if (i + 1) % percent_step == 0 or (i + 1) == numberOfBoards:
                percent = int(((i + 1) / numberOfBoards) * 100)
                sys.stdout.write(f"\rGenerating invalid puzzle variants... {percent}% Complete ({i + 1}/{numberOfBoards})")
                sys.stdout.flush()

        print("\nDataset generation successfully finalized.")
        return generated_boards