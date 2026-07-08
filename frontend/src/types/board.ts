export type Position = {
    row: number;
    col: number;
};

export type Waypoint = {
    number: number;
    position: Position;
};

export type Wall = {
    neighborA: Position;
    neighborB: Position;
};

export type BoardConfig = {
    boardSize: 6 | 7 | 8;
    waypoints: Waypoint[];
    walls: Wall[];
};

export type SolutionPath = Position[];