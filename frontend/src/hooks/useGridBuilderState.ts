import { useEffect, useEffectEvent, useRef, useState } from "react";

import {
    importPuzzle,
    solvePuzzle,
} from "../api/apiCalls";
import { ApiError } from "../api/apiClient";
import { dialogMessages } from "../data/dialogMessages";
import {
    clearSharedBoardFromUrl,
    createShareUrl,
    loadBoardFromSearch,
} from "../utils/boardShareService";
import { createEmptyBoard, toggleWall, toggleWaypoint } from "../utils/boardEditor";
import { validateImageFile } from "../utils/fileValidation";
import { isValidGameMove } from "../utils/gameMode";
import {
    appendVisitedCell,
    createPlayModeState,
    getActivePosition,
    getExpectedNextWaypoint,
    hasCompletedAllWaypoints,
    isCellAlreadyVisited,
    resetPlayModeState,
    undoVisitedCell,
} from "../utils/playMode";
import { getHintPathToNextWaypoint, normalizeSolutionPath } from "../utils/solutionPath";
import type { BoardConfig, Position, Wall } from "../types/board";
import type { EditMode, GridSize, ViewMode } from "../types/grid";
import type { AppMessage } from "../types/message";
import type { SolutionPath, SolverMetrics, SolverResponse } from "../types/solver";

type SolveFlow = "SOLVE" | "PLAY_PRECHECK" | "HINT_RETRY";

type SolverRequestResult = {
    response: SolverResponse | null;
    current: boolean;
};

const intermediateWaypointMessages = [
    "Nice checkpoint!",
    "Great momentum!",
    "Keep it up!",
] as const;

function getRandomIntermediateWaypointMessage() {
    const randomIndex = Math.floor(Math.random() * intermediateWaypointMessages.length);
    return intermediateWaypointMessages[randomIndex];
}

/**
 * Owns the board builder's state transitions and async workflows.
 * The returned values are intentionally shaped for `GridBuilder`'s layout only.
 */
export default function useGridBuilderState() {
    const [board, setBoard] = useState<BoardConfig>(() => createEmptyBoard(6));
    const [solution, setSolution] = useState<SolutionPath | null>(null);
    const [playSolution, setPlaySolution] = useState<SolutionPath | null>(null);
    const [hintPath, setHintPath] = useState<SolutionPath | null>(null);
    const [hintPathVersion, setHintPathVersion] = useState(0);
    const [metrics, setMetrics] = useState<SolverMetrics | null>(null);
    const [editMode, setEditMode] = useState<EditMode>("NUMBERS");
    const [viewMode, setViewMode] = useState<ViewMode>("BUILD");
    const [message, setMessage] = useState<AppMessage>(() => ({
        id: crypto.randomUUID(),
        type: "INFO",
        message: dialogMessages.welcome,
        timestamp: new Date(),
    }));
    const [isSolving, setIsSolving] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [pathShakeVersion, setPathShakeVersion] = useState(0);
    const [victoryAnimationVersion, setVictoryAnimationVersion] = useState(0);
    const [playModeState, setPlayModeState] = useState(() => createPlayModeState());

    const boardsBySizeRef = useRef<Record<GridSize, BoardConfig>>({
        6: createEmptyBoard(6),
        7: createEmptyBoard(7),
        8: createEmptyBoard(8),
    });
    const sharedBoardLoadedRef = useRef(false);
    const solverRequestVersionRef = useRef(0);

    useEffect(() => {
        boardsBySizeRef.current[board.boardSize] = board;
    }, [board]);

    function showMessage(type: AppMessage["type"], text: string) {
        setMessage({
            id: crypto.randomUUID(),
            type,
            message: text,
            timestamp: new Date(),
        });
    }

    function invalidateSolverRequest() {
        solverRequestVersionRef.current += 1;
        setIsSolving(false);
    }

    function clearDerivedSolverState() {
        invalidateSolverRequest();
        setSolution(null);
        setPlaySolution(null);
        setHintPath(null);
        setMetrics(null);
    }

    useEffect(() => {
        if (sharedBoardLoadedRef.current) {
            return;
        }

        sharedBoardLoadedRef.current = true;
        const sharedBoard = loadBoardFromSearch(window.location.search);

        if (!sharedBoard) {
            return;
        }

        setBoard(sharedBoard);
        clearDerivedSolverState();
        setPlayModeState(resetPlayModeState(sharedBoard.waypoints[0] ?? null));
        clearSharedBoardFromUrl();
        showMessage("SUCCESS", "Board loaded from shared link");
    }, []);

    function handleGridSizeChange(size: GridSize) {
        if (size === board.boardSize) {
            return;
        }

        const cachedBoard = boardsBySizeRef.current[size] ?? createEmptyBoard(size);
        setBoard(cachedBoard);
        clearDerivedSolverState();
        setPlayModeState(resetPlayModeState(cachedBoard.waypoints[0] ?? null));
    }

    function handleCellClick(position: Position) {
        if (viewMode === "PLAY") {
            if (hasCompletedAllWaypoints(playModeState, board)) {
                return;
            }

            const currentPosition = getActivePosition(playModeState, board.waypoints[0] ?? null);

            if (!currentPosition) {
                showMessage("WARNING", dialogMessages.play.addWaypointFirst);
                return;
            }

            if (position[0] === currentPosition[0] && position[1] === currentPosition[1]) {
                showMessage("INFO", dialogMessages.play.alreadyOnCell);
                return;
            }

            const previousPosition = playModeState.visitedCells.length > 1
                ? playModeState.visitedCells[playModeState.visitedCells.length - 2]
                : null;

            if (previousPosition && position[0] === previousPosition[0] && position[1] === previousPosition[1]) {
                setPlayModeState((previous) => undoVisitedCell(previous));
                return;
            }

            if (!isValidGameMove(currentPosition, position, board)) {
                setPathShakeVersion((previous) => previous + 1);
                showMessage("WARNING", dialogMessages.play.invalidMove);
                return;
            }

            const expectedWaypoint = getExpectedNextWaypoint(playModeState, board);
            const targetIsWaypoint = board.waypoints.some(
                (waypoint) => waypoint[0] === position[0] && waypoint[1] === position[1],
            );

            if (targetIsWaypoint && expectedWaypoint) {
                const isExpectedWaypoint = position[0] === expectedWaypoint[0]
                    && position[1] === expectedWaypoint[1];

                if (!isExpectedWaypoint) {
                    setPathShakeVersion((previous) => previous + 1);
                    showMessage("WARNING", dialogMessages.play.waypointOrder);
                    return;
                }
            }

            if (isCellAlreadyVisited(playModeState, position)) {
                setPathShakeVersion((previous) => previous + 1);
                showMessage("WARNING", dialogMessages.play.alreadyVisited);
                return;
            }

            const nextState = {
                ...playModeState,
                visitedCells: [...playModeState.visitedCells, position],
            };
            const reachedWaypointIndex = board.waypoints.findIndex(
                ([row, col]) => row === position[0] && col === position[1],
            );

            setPlayModeState((previous) => appendVisitedCell(previous, position));

            if (hasCompletedAllWaypoints(nextState, board)) {
                setVictoryAnimationVersion((previous) => previous + 1);
                showMessage("SUCCESS", dialogMessages.play.solved);
                return;
            }

            const lastWaypoint = board.waypoints[board.waypoints.length - 1] ?? null;
            const reachedLastWaypoint = lastWaypoint !== null
                && position[0] === lastWaypoint[0]
                && position[1] === lastWaypoint[1];

            if (reachedLastWaypoint) {
                showMessage("INFO", dialogMessages.play.lastWaypointOnly);
                return;
            }

            const isIntermediateWaypoint = reachedWaypointIndex > 0
                && reachedWaypointIndex < board.waypoints.length - 1;

            if (isIntermediateWaypoint) {
                showMessage("INFO", getRandomIntermediateWaypointMessage());
            }
            return;
        }

        if (editMode === "NUMBERS") {
            setBoard((previous) => toggleWaypoint(previous, position));
            clearDerivedSolverState();
        }
    }

    function handleWallClick(wall: Wall) {
        if (editMode !== "WALLS") {
            return;
        }

        setBoard((previous) => toggleWall(previous, wall));
        clearDerivedSolverState();
    }

    async function requestSolverResult(): Promise<SolverRequestResult> {
        const requestVersion = solverRequestVersionRef.current + 1;
        solverRequestVersionRef.current = requestVersion;
        const requestBoard = board;
        setIsSolving(true);

        try {
            const response = await solvePuzzle(requestBoard);

            if (requestVersion !== solverRequestVersionRef.current) {
                return { response: null, current: false };
            }

            setMetrics(response.metrics ?? null);
            return { response, current: true };
        } catch (error) {
            console.error(error);

            if (requestVersion !== solverRequestVersionRef.current) {
                return { response: null, current: false };
            }

            setMetrics(null);
            return { response: null, current: true };
        } finally {
            if (requestVersion === solverRequestVersionRef.current) {
                setIsSolving(false);
            }
        }
    }

    function handleSolveResponse(response: SolverResponse | null) {
        if (!response) {
            setSolution(null);
            showMessage("ERROR", dialogMessages.solve.requestFailed);
            return;
        }

        if (response.success && response.solutionPath) {
            setSolution(response.solutionPath);
            setPlaySolution(response.solutionPath);
            setHintPath(null);
            showMessage(response.solverUsed === "RLSolver" ? "SUCCESS" : "WARNING", response.message);
            return;
        }

        if (response.success) {
            setSolution(null);
            showMessage("ERROR", response.message);
            return;
        }

        setSolution(null);
        showMessage(response.status === "UNSOLVABLE" ? "WARNING" : "ERROR", response.message);
    }

    function handlePlayPrecheckResponse(response: SolverResponse | null) {
        setSolution(null);
        setHintPath(null);

        if (response?.success && response.solutionPath) {
            setPlaySolution(response.solutionPath);
            showMessage("INFO", dialogMessages.mode.playEnabled);
            return;
        }

        setPlaySolution(null);
        showMessage("WARNING", dialogMessages.mode.playEnabledWithoutGuarantee);
    }

    async function handleSolve(flow: SolveFlow) {
        if (flow === "SOLVE" && board.waypoints.length < 2) {
            showMessage("WARNING", dialogMessages.solve.addWaypointsFirst);
            return null;
        }

        const result = await requestSolverResult();

        if (!result.current) {
            return null;
        }

        if (flow === "SOLVE") {
            handleSolveResponse(result.response);
        }

        if (flow === "PLAY_PRECHECK") {
            handlePlayPrecheckResponse(result.response);
        }

        return result.response;
    }

    async function ensurePlaySolution() {
        let availableSolution = playSolution;

        if (!availableSolution) {
            const response = await handleSolve("HINT_RETRY");

            if (response?.success && response.solutionPath) {
                availableSolution = response.solutionPath;
                setPlaySolution(response.solutionPath);
            }
        }

        return availableSolution;
    }

    async function handleHint() {
        if (viewMode !== "PLAY") {
            showMessage("WARNING", dialogMessages.play.switchToPlayFirst);
            return;
        }

        if (hasCompletedAllWaypoints(playModeState, board)) {
            return;
        }

        const availableSolution = await ensurePlaySolution();

        if (!availableSolution) {
            setHintPath(null);
            showMessage("WARNING", dialogMessages.play.unableToSolveForHint);
            return;
        }

        const nextHintPath = getHintPathToNextWaypoint(
            availableSolution,
            board,
            getExpectedNextWaypoint(playModeState, board),
        );

        if (!nextHintPath || nextHintPath.length < 2) {
            setHintPath(null);
            showMessage("WARNING", dialogMessages.play.hintUnavailableForCurrentPath);
            return;
        }

        setHintPath(nextHintPath);
        setHintPathVersion((previous) => previous + 1);
        showMessage("INFO", dialogMessages.play.hintPathShown);
    }

    async function handleShowSolutionInPlay() {
        if (hasCompletedAllWaypoints(playModeState, board)) {
            return;
        }

        const availableSolution = await ensurePlaySolution();

        if (!availableSolution) {
            setHintPath(null);
            showMessage("WARNING", dialogMessages.play.unableToSolveForHint);
            return;
        }

        setHintPath(normalizeSolutionPath(availableSolution, board));
        setHintPathVersion((previous) => previous + 1);
    }

    async function handleSolveClick() {
        if (viewMode === "PLAY") {
            await handleShowSolutionInPlay();
            return;
        }

        await handleSolve("SOLVE");
    }

    async function handlePlayModeEnter() {
        setEditMode("NUMBERS");
        await handleSolve("PLAY_PRECHECK");
    }

    function handleClearPlayPath() {
        if (hasCompletedAllWaypoints(playModeState, board)) {
            return;
        }

        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
        setHintPath(null);
    }

    async function handleImportScreenshot(file: File, imageBoardSize: GridSize) {
        if (imageBoardSize !== 6 && imageBoardSize !== 7 && imageBoardSize !== 8) {
            showMessage("WARNING", "Screenshot size must be 6, 7, or 8");
            return;
        }

        const fileCheck = validateImageFile(file);
        if (!fileCheck.valid) {
            showMessage("WARNING", fileCheck.reason);
            return;
        }

        invalidateSolverRequest();
        setIsImporting(true);
        showMessage("INFO", dialogMessages.import.sizeHint(imageBoardSize));
        showMessage("INFO", dialogMessages.import.started);

        try {
            const result = await importPuzzle(file, imageBoardSize);

            if (!result.board) {
                showMessage("ERROR", result.message || dialogMessages.import.noBoardDetected);
                return;
            }

            const importedBoard = result.board;
            setBoard(importedBoard);
            clearDerivedSolverState();
            setEditMode("NUMBERS");
            setViewMode("BUILD");
            setPlayModeState(resetPlayModeState(importedBoard.waypoints[0] ?? null));

            if (!result.valid) {
                showMessage(
                    "WARNING",
                    dialogMessages.import.invalidBoard(result.errors[0]?.message ?? result.message),
                );
                return;
            }

            if (result.warnings.length > 0) {
                showMessage("WARNING", dialogMessages.import.succeededWithWarnings(result.warnings.length));
                return;
            }

            showMessage(
                "SUCCESS",
                dialogMessages.import.succeeded(importedBoard.waypoints.length, importedBoard.walls.length),
            );
        } catch (error) {
            console.error(error);

            if (error instanceof ApiError) {
                showMessage(
                    "ERROR",
                    error.code === "NO_BOARD_DETECTED"
                        ? dialogMessages.import.noBoardDetected
                        : dialogMessages.import.failed(error.message),
                );
                return;
            }

            showMessage("ERROR", dialogMessages.import.failed("Unexpected error while reading the screenshot"));
        } finally {
            setIsImporting(false);
        }
    }

    function handleReset() {
        setViewMode("BUILD");
        setEditMode("NUMBERS");
        setBoard((previous) => createEmptyBoard(previous.boardSize));
        clearDerivedSolverState();
        setPlayModeState(resetPlayModeState());
        showMessage("INFO", dialogMessages.reset);
    }

    async function handleShare() {
        if (board.waypoints.length === 0 && board.walls.length === 0) {
            showMessage("WARNING", dialogMessages.share.nothingToShare);
            return;
        }

        const shareUrl = createShareUrl(board);

        try {
            await navigator.clipboard.writeText(shareUrl);
            showMessage("SUCCESS", dialogMessages.share.copied);
        } catch (error) {
            console.error(error);
            window.prompt("Copy this share link:", shareUrl);
            showMessage("WARNING", dialogMessages.share.clipboardDenied);
        }
    }

    function handleSelectExample(exampleBoard: BoardConfig, name: string) {
        setBoard(exampleBoard);
        clearDerivedSolverState();
        setPlayModeState(resetPlayModeState(exampleBoard.waypoints[0] ?? null));
        showMessage("INFO", dialogMessages.examples.loaded(name));
    }

    function handleModeChange(mode: EditMode) {
        setEditMode(mode);
        setPlaySolution(null);
        setHintPath(null);
        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
    }

    const handleCellClickEvent = useEffectEvent(handleCellClick);

    async function handleViewModeChange(mode: ViewMode) {
        if (mode === viewMode) {
            return;
        }

        setViewMode(mode);
        setHintPath(null);

        if (mode === "PLAY") {
            setEditMode("NUMBERS");
            setPlayModeState(createPlayModeState(board.waypoints[0] ?? null));
            await handlePlayModeEnter();
            return;
        }

        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
        showMessage("INFO", dialogMessages.mode.buildEnabled);
    }

    useEffect(() => {
        if (viewMode !== "PLAY") {
            return;
        }

        const handleKeyDown = (event: KeyboardEvent) => {
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") {
                event.preventDefault();
                setPlayModeState((previous) => undoVisitedCell(previous));
                return;
            }

            const currentPosition = getActivePosition(playModeState, board.waypoints[0] ?? null);
            if (!currentPosition) {
                return;
            }

            const directionMap: Record<string, Position> = {
                ArrowUp: [-1, 0],
                ArrowDown: [1, 0],
                ArrowLeft: [0, -1],
                ArrowRight: [0, 1],
            };
            const delta = directionMap[event.key];

            if (!delta) {
                return;
            }

            event.preventDefault();
            const nextPosition: Position = [currentPosition[0] + delta[0], currentPosition[1] + delta[1]];

            if (
                nextPosition[0] < 0
                || nextPosition[0] >= board.boardSize
                || nextPosition[1] < 0
                || nextPosition[1] >= board.boardSize
            ) {
                return;
            }

            handleCellClickEvent(nextPosition);
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [board.boardSize, board.waypoints, playModeState, viewMode]);

    const nextWaypoint = viewMode === "PLAY" ? getExpectedNextWaypoint(playModeState, board) : null;
    const isPlayCompleted = viewMode === "PLAY" && hasCompletedAllWaypoints(playModeState, board);

    return {
        board,
        solution,
        playSolution,
        hintPath,
        hintPathVersion,
        metrics,
        editMode,
        viewMode,
        message,
        isSolving,
        isImporting,
        pathShakeVersion,
        victoryAnimationVersion,
        playModeState,
        isPlayCompleted,
        nextWaypoint,
        activePosition: getActivePosition(playModeState, board.waypoints[0] ?? null),
        handleGridSizeChange,
        handleCellClick,
        handleWallClick,
        handleHint,
        handleClearPlayPath,
        handleSolveClick,
        handleViewModeChange,
        handleReset,
        handleShare,
        handleImportScreenshot,
        handleSelectExample,
        handleModeChange,
        handleUndo: () => setPlayModeState((previous) => undoVisitedCell(previous)),
    };
}
