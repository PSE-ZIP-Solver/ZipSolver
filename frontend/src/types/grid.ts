/** Re-export the board size type so UI code has one source of truth. */
export type { GridSize } from "./board";

/** Selects which board elements can be edited. */
export type EditMode =
    | "NUMBERS"
    | "WALLS";

/** Selects whether the user is editing a board or playing it. */
export type ViewMode =
    | "BUILD"
    | "PLAY";