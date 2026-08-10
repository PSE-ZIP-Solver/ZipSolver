import type { BoardConfig, Position } from "../types/board";
import type { SolutionPath } from "../types/solver";

export interface PlayModeState {
    visitedCells: SolutionPath;
}

export function createPlayModeState(startCell: Position | null = null): PlayModeState {
    return {
        visitedCells: startCell ? [startCell] : [],
    };
}

export function resetPlayModeState(startCell: Position | null = null): PlayModeState {
    return createPlayModeState(startCell);
}

export function appendVisitedCell(state: PlayModeState, cell: Position): PlayModeState {
    return {
        ...state,
        visitedCells: [...state.visitedCells, cell],
    };
}

export function undoVisitedCell(state: PlayModeState): PlayModeState {
    return {
        ...state,
        visitedCells: state.visitedCells.slice(0, -1),
    };
}

export function isCellAlreadyVisited(state: PlayModeState, cell: Position) {
    return state.visitedCells.some((position) => position[0] === cell[0] && position[1] === cell[1]);
}

export function getActivePosition(state: PlayModeState, startCell: Position | null) {
    return state.visitedCells[state.visitedCells.length - 1] ?? startCell ?? null;
}

export function getHintPosition(solution: SolutionPath | null, state: PlayModeState, board: BoardConfig) {
    if (!solution || solution.length === 0) {
        return board.waypoints[0] ?? null;
    }

    const offset = state.visitedCells.length > 0 && isSamePosition(state.visitedCells[0], board.waypoints[0] ?? null)
        ? 1
        : 0;

    return solution[state.visitedCells.length - offset] ?? null;
}

export function getExpectedNextWaypoint(state: PlayModeState, board: BoardConfig) {
    if (board.waypoints.length <= 1) {
        return null;
    }

    const startCell = board.waypoints[0] ?? null;
    const visitedWaypoints = state.visitedCells.filter((position) => board.waypoints.some((waypoint) => waypoint[0] === position[0] && waypoint[1] === position[1]));

    if (startCell && !visitedWaypoints.some((position) => isSamePosition(position, startCell))) {
        return startCell;
    }

    for (let index = 1; index < board.waypoints.length; index += 1) {
        const waypoint = board.waypoints[index];
        const isVisited = visitedWaypoints.some((position) => position[0] === waypoint[0] && position[1] === waypoint[1]);

        if (!isVisited) {
            return waypoint;
        }
    }

    return null;
}

function isSamePosition(a: Position | null, b: Position | null) {
    if (!a || !b) {
        return false;
    }

    return a[0] === b[0] && a[1] === b[1];
}

export function hasCompletedAllWaypoints(state: PlayModeState, board: BoardConfig) {
    const totalCells = board.boardSize * board.boardSize;

    if (state.visitedCells.length !== totalCells) {
        return false;
    }

    const visitedCells = new Set(state.visitedCells.map((position) => `${position[0]},${position[1]}`));

    if (visitedCells.size !== totalCells) {
        return false;
    }

    if (board.waypoints.length === 0) {
        return true;
    }

    const visitedWaypoints = state.visitedCells.filter((position) => board.waypoints.some((waypoint) => isSamePosition(position, waypoint)));

    if (visitedWaypoints.length !== board.waypoints.length) {
        return false;
    }

    return board.waypoints.every((waypoint, index) => {
        const visitedWaypoint = visitedWaypoints[index];
        return visitedWaypoint ? isSamePosition(visitedWaypoint, waypoint) : false;
    });
}
