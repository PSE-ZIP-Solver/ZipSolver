export type GridSize =
    | 6
    | 7
    | 8;

export type Position = [number, number];

export interface Wall {
    neighborA: Position;
    neighborB: Position;
}

export interface BoardConfig {
    boardSize: GridSize;
    waypoints: Position[];
    walls: Wall[];
}