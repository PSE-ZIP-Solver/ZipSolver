import type { BoardConfig, Position } from "../types/board";
import type { SolutionPath } from "../types/solver";

function isSamePosition(first: Position, second: Position): boolean {
    return first[0] === second[0] && first[1] === second[1];
}

/** Ensures a solver path starts at the board's first waypoint when one exists. */
export function normalizeSolutionPath(solutionPath: SolutionPath, board: BoardConfig): SolutionPath {
    const startCell = board.waypoints[0] ?? null;

    if (!startCell || solutionPath.length === 0 || isSamePosition(solutionPath[0], startCell)) {
        return solutionPath;
    }

    return [startCell, ...solutionPath];
}

/** Returns the path segment from the start cell to the next required waypoint. */
export function getHintPathToNextWaypoint(
    solutionPath: SolutionPath,
    board: BoardConfig,
    nextWaypoint: Position | null,
): SolutionPath | null {
    const startCell = board.waypoints[0] ?? null;

    if (!startCell || !nextWaypoint) {
        return null;
    }

    const normalizedSolution = normalizeSolutionPath(solutionPath, board);
    const startIndex = normalizedSolution.findIndex((position) => isSamePosition(position, startCell));

    if (startIndex < 0) {
        return null;
    }

    const targetIndex = normalizedSolution.findIndex(
        (position, index) => index >= startIndex && isSamePosition(position, nextWaypoint),
    );

    if (targetIndex <= startIndex) {
        return null;
    }

    return normalizedSolution.slice(startIndex, targetIndex + 1);
}
