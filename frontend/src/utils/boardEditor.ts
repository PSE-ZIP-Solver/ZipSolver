import type { BoardConfig, Position, Wall } from "../types/board";
import type { GridSize } from "../types/grid";

/** Creates a board with no waypoints or walls for the requested grid size. */
export function createEmptyBoard(size: GridSize): BoardConfig {
    return {
        boardSize: size,
        waypoints: [],
        walls: [],
    };
}

function isSamePosition(first: Position, second: Position): boolean {
    return first[0] === second[0] && first[1] === second[1];
}

function isSameWall(first: Wall, second: Wall): boolean {
    return isSamePosition(first.neighborA, second.neighborA)
        && isSamePosition(first.neighborB, second.neighborB);
}

/** Toggles one numbered waypoint without mutating the source board. */
export function toggleWaypoint(board: BoardConfig, position: Position): BoardConfig {
    const exists = board.waypoints.some((waypoint) => isSamePosition(waypoint, position));

    return {
        ...board,
        waypoints: exists
            ? board.waypoints.filter((waypoint) => !isSamePosition(waypoint, position))
            : [...board.waypoints, position],
    };
}

/** Toggles one wall without mutating the source board. */
export function toggleWall(board: BoardConfig, wall: Wall): BoardConfig {
    const exists = board.walls.some((item) => isSameWall(item, wall));

    return {
        ...board,
        walls: exists
            ? board.walls.filter((item) => !isSameWall(item, wall))
            : [...board.walls, wall],
    };
}
