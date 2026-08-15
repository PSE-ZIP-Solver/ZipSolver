import { type BoardConfig } from "./board";

export interface ValidationError {
    /*
     * The backend emits `errorCode` (see ValidationResult.py), not `code`.
     * The previous name silently resolved to undefined at runtime.
     */
    errorCode: string;
    affectedField?: string | null;
    message: string;
}

export interface ValidationResult {
    valid: boolean;
    message: string;
    errors: ValidationError[];
}

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
export interface ImportResult {
    board: BoardConfig | null;
    valid: boolean;
    message: string;
    errors: ValidationError[];
    warnings: ImportWarning[];
}