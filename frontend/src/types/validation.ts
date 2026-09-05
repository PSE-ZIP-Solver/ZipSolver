import { type BoardConfig } from "./board";

/** One machine-readable semantic validation problem returned by the backend. */
export interface ValidationError {
    /*
     * The backend emits `errorCode` (see ValidationResult.py), not `code`.
     * The previous name silently resolved to undefined at runtime.
     */
    errorCode: string;
    affectedField?: string | null;
    message: string;
}

/** Summary returned by board validation. */
export interface ValidationResult {
    valid: boolean;
    message: string;
    errors: ValidationError[];
}

/** Non-fatal screenshot extraction issue that still allows board import. */
export interface ImportWarning {
    code:
        | "WAYPOINT_NUMBER_UNREADABLE"
        | "WAYPOINT_NUMBER_DUPLICATE"
        | "WAYPOINT_ORDER_INFERRED"
        | "IMPORT_WARNING";
    message: string;
    cell?: [number, number] | null;
}

/*
 * Body of POST /api/import.
 *
 * `board` is populated even when `valid` is false, so the user can see and correct
 * what was read instead of starting the import over.
 */
/** Body returned by POST /api/import, including partially readable boards. */
export interface ImportResult {
    board: BoardConfig | null;
    valid: boolean;
    message: string;
    errors: ValidationError[];
    warnings: ImportWarning[];
}