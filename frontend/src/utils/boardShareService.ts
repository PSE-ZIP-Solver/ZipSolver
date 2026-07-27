import type { BoardConfig, GridSize, Position, Wall } from "../types/board";

const SHARE_PARAM = "board";
const SHARE_VERSION = "v1";

function isInteger(value: unknown): value is number {
    return typeof value === "number" && Number.isInteger(value) && Number.isFinite(value);
}

function isGridSize(value: unknown): value is GridSize {
    return value === 6 || value === 7 || value === 8;
}

function isPosition(value: unknown): value is Position {
    return Array.isArray(value)
        && value.length === 2
        && isInteger(value[0])
        && isInteger(value[1]);
}

function isWall(value: unknown): value is Wall {
    return typeof value === "object"
        && value !== null
        && "neighborA" in value
        && "neighborB" in value
        && isPosition((value as Wall).neighborA)
        && isPosition((value as Wall).neighborB);
}

function withinBounds([row, col]: Position, size: GridSize): boolean {
    return row >= 0 && row < size && col >= 0 && col < size;
}

function areAdjacent([rowA, colA]: Position, [rowB, colB]: Position): boolean {
    return Math.abs(rowA - rowB) + Math.abs(colA - colB) === 1;
}

function normalizeWallKey(wall: Wall): string {
    const a = `${wall.neighborA[0]}:${wall.neighborA[1]}`;
    const b = `${wall.neighborB[0]}:${wall.neighborB[1]}`;
    return [a, b].sort().join("|");
}

function encodeBase64Url(input: string): string {
    const bytes = new TextEncoder().encode(input);

    let binary = "";
    for (const byte of bytes) {
        binary += String.fromCharCode(byte);
    }

    return btoa(binary)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/g, "");
}

function decodeBase64Url(input: string): string {
    const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);

    const binary = atob(padded);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));

    return new TextDecoder().decode(bytes);
}

export function isBoardConfig(value: unknown): value is BoardConfig {
    if (typeof value !== "object" || value === null) {
        return false;
    }

    const board = value as Record<string, unknown>;

    if (!isGridSize(board.boardSize)) {
        return false;
    }

    if (!Array.isArray(board.waypoints) || !board.waypoints.every(isPosition)) {
        return false;
    }

    if (!Array.isArray(board.walls) || !board.walls.every(isWall)) {
        return false;
    }

    const waypointKeys = new Set<string>();
    for (const waypoint of board.waypoints as Position[]) {
        if (!withinBounds(waypoint, board.boardSize)) {
            return false;
        }

        const key = `${waypoint[0]}:${waypoint[1]}`;
        if (waypointKeys.has(key)) {
            return false;
        }
        waypointKeys.add(key);
    }

    const wallKeys = new Set<string>();
    for (const wall of board.walls as Wall[]) {
        if (!withinBounds(wall.neighborA, board.boardSize) || !withinBounds(wall.neighborB, board.boardSize)) {
            return false;
        }

        if (!areAdjacent(wall.neighborA, wall.neighborB)) {
            return false;
        }

        const key = normalizeWallKey(wall);
        if (wallKeys.has(key)) {
            return false;
        }
        wallKeys.add(key);
    }

    return true;
}

export function encodeBoardToShareToken(board: BoardConfig): string {
    const payload = JSON.stringify(board);
    return `${SHARE_VERSION}.${encodeBase64Url(payload)}`;
}

export function decodeBoardFromShareToken(token: string): BoardConfig | null {
    try {
        const [version, payload] = token.split(".", 2);

        if (version !== SHARE_VERSION || !payload) {
            return null;
        }

        const parsed = JSON.parse(decodeBase64Url(payload)) as unknown;
        return isBoardConfig(parsed) ? parsed : null;
    } catch {
        return null;
    }
}

export function createShareUrl(board: BoardConfig, baseUrl: string = window.location.href): string {
    const url = new URL(baseUrl);
    url.searchParams.set(SHARE_PARAM, encodeBoardToShareToken(board));
    return url.toString();
}

export function loadBoardFromSearch(search: string): BoardConfig | null {
    const params = new URLSearchParams(search);
    const token = params.get(SHARE_PARAM);

    if (!token) {
        return null;
    }

    return decodeBoardFromShareToken(token);
}

export function clearSharedBoardFromUrl(): void {
    const url = new URL(window.location.href);
    url.searchParams.delete(SHARE_PARAM);
    window.history.replaceState({}, "", url.toString());
}