/** Grid dimensions supported by the backend and screenshot importer. */
export type GridSize = 6 | 7 | 8;

/** A board coordinate stored as [row, column] in the frontend. */
export type Position = [number, number];

/** A wall blocks movement between two orthogonally adjacent cells. */
export interface Wall {
    neighborA: Position;
    neighborB: Position;
}

/** Complete editable puzzle state in frontend coordinate order. */
export interface BoardConfig {
    boardSize: GridSize;
    waypoints: Position[];
    walls: Wall[];
}