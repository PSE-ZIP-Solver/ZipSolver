import type { BoardConfig, Position } from "../types/board";

/** Checks whether a coordinate belongs to the square board. */
export function isInsideBoard(position: Position, size: number) {
    return (
        position[0] >= 0 &&
        position[0] < size &&
        position[1] >= 0 &&
        position[1] < size
    );
}

function getWallKey(a: Position, b: Position) {
    const [first, second] = a[0] !== b[0] ? (a[0] < b[0] ? [a, b] : [b, a]) : (a[1] < b[1] ? [a, b] : [b, a]);
    return `${first[0]},${first[1]}|${second[0]},${second[1]}`;
}

/** Checks whether a wall blocks one orthogonally adjacent move. */
export function hasWallBetween(from: Position, to: Position, walls: BoardConfig["walls"]) {
    if (Math.abs(from[0] - to[0]) + Math.abs(from[1] - to[1]) !== 1) {
        return false;
    }

    const wallKey = getWallKey(from, to);
    return walls.some((wall) => getWallKey(wall.neighborA, wall.neighborB) === wallKey);
}

/** Applies bounds, adjacency, and wall rules to a proposed player move. */
export function isValidGameMove(currentPosition: Position, nextPosition: Position, board: BoardConfig) {
    if (!isInsideBoard(nextPosition, board.boardSize)) {
        return false;
    }

    if (Math.abs(currentPosition[0] - nextPosition[0]) + Math.abs(currentPosition[1] - nextPosition[1]) !== 1) {
        return false;
    }

    return !hasWallBetween(currentPosition, nextPosition, board.walls);
}
