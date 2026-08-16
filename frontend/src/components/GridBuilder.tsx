import { useEffect, useRef, useState } from "react";

import Grid from "./Grid.tsx";
import ControlPanel from "./ControlPanel";
import DialogPanel from "./DialogPanel";
import ActionPanel from "./ActionPanel";
import MetricsPanel from "./MetricsPanel";
import ExamplesSection from "./ExamplesSection";

import {
    type EditMode,
    type GridSize,
    type ViewMode
} from "../types/grid";

import {
    type BoardConfig,
    type Position,
    type Wall
} from "../types/board";

import {
    type SolutionPath,
    type SolverMetrics,
    type SolverResponse
} from "../types/solver";

import {
    type AppMessage,
} from "../types/message";

import { dialogMessages } from "../data/dialogMessages";

import {
    importPuzzle,
    solvePuzzle,
} from "../api/apiCalls";

import { ApiError } from "../api/apiClient";

import {
    validateImageFile,
} from "../utils/fileValidation";

import {
    clearSharedBoardFromUrl,
    createShareUrl,
    loadBoardFromSearch,
} from "../utils/boardShareService";

import {
    isValidGameMove,
} from "../utils/gameMode";

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


type SolveFlow = "SOLVE" | "PLAY_PRECHECK" | "HINT_RETRY";

const intermediateWaypointMessages = [
    "Nice checkpoint!",
    "Great momentum!",
    "Keep it up!",
] as const;

function getRandomIntermediateWaypointMessage() {
    const randomIndex = Math.floor(Math.random() * intermediateWaypointMessages.length);
    return intermediateWaypointMessages[randomIndex];
}

function createEmptyBoard(size: GridSize): BoardConfig {
    return {
        boardSize: size,
        waypoints: [],
        walls: [],
    };
}

export default function GridBuilder() {

    /*
     * Current puzzle configuration
     */
    const [board, setBoard] = useState<BoardConfig>({
        boardSize: 6,
        waypoints: [],
        walls: [],
    });


    /*
     * Solver result
     */
    const [solution, setSolution] =
        useState<SolutionPath | null>(null);

    const [playSolution, setPlaySolution] =
        useState<SolutionPath | null>(null);

    const [hintPath, setHintPath] =
        useState<SolutionPath | null>(null);

    const [hintPathVersion, setHintPathVersion] =
        useState(0);

    const [metrics, setMetrics] =
        useState<SolverMetrics | null>(null);


    /*
     * UI state
     */
    const [editMode, setEditMode] =
        useState<EditMode>("NUMBERS");

    const [viewMode, setViewMode] =
        useState<ViewMode>("BUILD");


    const [message, setMessage] =
        useState<AppMessage>({
            id: crypto.randomUUID(),

            type: "INFO",

            message:
                dialogMessages.welcome,

            timestamp:
                new Date()
        });


    const [isSolving, setIsSolving] =
        useState(false);

    const [isImporting, setIsImporting] =
        useState(false);

    const [pathShakeVersion, setPathShakeVersion] =
        useState(0);

    const [victoryAnimationVersion, setVictoryAnimationVersion] =
        useState(0);

    const [playModeState, setPlayModeState] =
        useState(createPlayModeState(board.waypoints[0] ?? null));


    const boardsBySizeRef =
        useRef<Record<GridSize, BoardConfig>>({
            6: createEmptyBoard(6),
            7: createEmptyBoard(7),
            8: createEmptyBoard(8),
        });


    const sharedBoardLoadedRef =
        useRef(false);

    useEffect(() => {
        boardsBySizeRef.current[board.boardSize] = board;
    }, [board]);

    useEffect(() => {

        if (sharedBoardLoadedRef.current)
            return;

        sharedBoardLoadedRef.current = true;


        const sharedBoard =
            loadBoardFromSearch(
                window.location.search
            );


        if (!sharedBoard)
            return;


        setBoard(sharedBoard);

        setSolution(null);
        setPlaySolution(null);
        setHintPath(null);
        setMetrics(null);
        setPlayModeState(resetPlayModeState(sharedBoard.waypoints[0] ?? null));


        clearSharedBoardFromUrl();


        showMessage(
            "SUCCESS",
            "Board loaded from shared link"
        );

    }, []);


    function clearDerivedSolverState() {
        setSolution(null);
        setPlaySolution(null);
        setHintPath(null);
        setMetrics(null);
    }


    /*
     * ============================
     * Board manipulation
     * ============================
     */
    function handleGridSizeChange(
        size: GridSize
    ) {

        if (size === board.boardSize)
            return;

        const cachedBoard =
            boardsBySizeRef.current[size] ??
            createEmptyBoard(size);

        setBoard(cachedBoard);

        clearDerivedSolverState();
        setPlayModeState(resetPlayModeState(cachedBoard.waypoints[0] ?? null));
    }


    function handleCellClick(
        position: Position
    ) {

        if (viewMode === "PLAY") {
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
            const targetIsWaypoint = board.waypoints.some((waypoint) => waypoint[0] === position[0] && waypoint[1] === position[1]);

            if (targetIsWaypoint && expectedWaypoint) {
                const isExpectedWaypoint = position[0] === expectedWaypoint[0] && position[1] === expectedWaypoint[1];

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
                ([row, col]) => row === position[0] && col === position[1]
            );

            setPlayModeState((previous) => appendVisitedCell(previous, position));

            if (hasCompletedAllWaypoints(nextState, board)) {
                setVictoryAnimationVersion((previous) => previous + 1);
                showMessage("SUCCESS", dialogMessages.play.solved);
                return;
            }

            const lastWaypoint = board.waypoints[board.waypoints.length - 1] ?? null;
            const reachedLastWaypoint = lastWaypoint
                ? position[0] === lastWaypoint[0] && position[1] === lastWaypoint[1]
                : false;

            if (reachedLastWaypoint) {
                showMessage("INFO", dialogMessages.play.lastWaypointOnly);
                return;
            }

            const isIntermediateWaypoint =
                reachedWaypointIndex > 0 &&
                reachedWaypointIndex < board.waypoints.length - 1;

            if (isIntermediateWaypoint) {
                showMessage("INFO", getRandomIntermediateWaypointMessage());
                return;
            }
            return;
        }

        if (editMode !== "NUMBERS")
            return;


        const existing =
            board.waypoints.find(
                ([row, col]) =>
                    row === position[0] &&
                    col === position[1]
            );


        let updatedWaypoints;


        /*
         * Remove existing waypoint
         */
        if (existing) {

            updatedWaypoints =
                board.waypoints
                    .filter(
                        ([row, col]) =>
                            row !== position[0] ||
                            col !== position[1]
                    );

        }


        /*
         * Add new waypoint
         */
        else {

            updatedWaypoints = [
                ...board.waypoints,
                position
            ];

        }


        setBoard(previous => ({
            ...previous,
            waypoints: updatedWaypoints
        }));


        clearDerivedSolverState();
    }



    function handleWallClick(
        wall: Wall
    ) {

        if (editMode !== "WALLS")
            return;


        const exists =
            board.walls.some(
                item => {

                    const [itemARow, itemACol] = item.neighborA;
                    const [itemBRow, itemBCol] = item.neighborB;
                    const [wallARow, wallACol] = wall.neighborA;
                    const [wallBRow, wallBCol] = wall.neighborB;

                    return (
                        itemARow === wallARow &&
                        itemACol === wallACol &&
                        itemBRow === wallBRow &&
                        itemBCol === wallBCol
                    );
                }
            );


        const updatedWalls =
            exists

                ? board.walls.filter(
                    item => {

                        const [itemARow, itemACol] = item.neighborA;
                        const [itemBRow, itemBCol] = item.neighborB;
                        const [wallARow, wallACol] = wall.neighborA;
                        const [wallBRow, wallBCol] = wall.neighborB;

                        return !(
                            itemARow === wallARow &&
                            itemACol === wallACol &&
                            itemBRow === wallBRow &&
                            itemBCol === wallBCol
                        );
                    }
                )

                : [
                    ...board.walls,
                    wall
                ];



        setBoard(previous => ({
            ...previous,
            walls: updatedWalls
        }));


        clearDerivedSolverState();
    }



    /*
     * ============================
     * Solver
     * ============================
     */
    async function requestSolverResult() {
        try {

            setIsSolving(true);

            const response = await solvePuzzle(board);

            setMetrics(response.metrics ?? null);

            return response;
        }

        catch (error) {

            console.error(error);

            setMetrics(null);

            return null;
        }

        finally {

            setIsSolving(false);

        }
    }


    function handleSolveResponse(response: SolverResponse | null) {

        if (!response) {
            setSolution(null);

            showMessage(
                "ERROR",
                dialogMessages.solve.requestFailed
            );

            return;
        }


        if (response.success && response.solutionPath) {

            setSolution(response.solutionPath);
            setPlaySolution(response.solutionPath);
            setHintPath(null);

            showMessage(
                response.solverUsed === "RLSolver" ? "SUCCESS" : "WARNING",
                response.message
            );

            return;
        }


        if (response.success) {

            setSolution(null);

            showMessage(
                "ERROR",
                response.message
            );

            return;
        }


        setSolution(null);

        switch (response.status) {

            case "UNSOLVABLE":

                showMessage(
                    "WARNING",
                    response.message
                );

                break;


            case "TIMEOUT":

                showMessage(
                    "ERROR",
                    response.message
                );

                break;


            case "FAILED":

                showMessage(
                    "ERROR",
                    response.message
                );

                break;


            default:

                showMessage(
                    "ERROR",
                    response.message
                );

                break;
        }
    }


    function handlePlayPrecheckResponse(response: SolverResponse | null) {

        setSolution(null);
        setHintPath(null);

        if (response?.success && response.solutionPath) {
            setPlaySolution(response.solutionPath);

            showMessage(
                "INFO",
                dialogMessages.mode.playEnabled
            );

            return;
        }

        setPlaySolution(null);

        showMessage(
            "WARNING",
            dialogMessages.mode.playEnabledWithoutGuarantee
        );
    }


    async function handleSolve(flow: SolveFlow) {

        if (flow === "SOLVE" && board.waypoints.length < 2) {

            showMessage(
                "WARNING",
                dialogMessages.solve.addWaypointsFirst
            );

            return null;
        }

        const response = await requestSolverResult();

        if (flow === "SOLVE") {
            handleSolveResponse(response);
        }

        if (flow === "PLAY_PRECHECK") {
            handlePlayPrecheckResponse(response);
        }

        return response;
    }


    function getHintPathToNextWaypoint(solutionPath: SolutionPath) {
        const nextWaypoint = getExpectedNextWaypoint(playModeState, board);
        const startCell = board.waypoints[0] ?? null;

        if (!startCell || !nextWaypoint) {
            return null;
        }

        const normalizedSolution = solutionPath.length > 0
            ? (
                solutionPath[0][0] === startCell[0] && solutionPath[0][1] === startCell[1]
                    ? solutionPath
                    : [startCell, ...solutionPath]
            )
            : solutionPath;

        if (normalizedSolution.length === 0) {
            return null;
        }

        const startIndex = normalizedSolution.findIndex(
            ([row, col]) => row === startCell[0] && col === startCell[1]
        );

        if (startIndex < 0) {
            return null;
        }

        const targetIndex = normalizedSolution.findIndex(
            ([row, col], index) =>
                index >= startIndex &&
                row === nextWaypoint[0] &&
                col === nextWaypoint[1]
        );

        if (targetIndex <= startIndex) {
            return null;
        }

        return normalizedSolution.slice(startIndex, targetIndex + 1);
    }


    function getNormalizedSolutionPath(solutionPath: SolutionPath) {
        const startCell = board.waypoints[0] ?? null;

        if (!startCell || solutionPath.length === 0) {
            return solutionPath;
        }

        if (solutionPath[0][0] === startCell[0] && solutionPath[0][1] === startCell[1]) {
            return solutionPath;
        }

        return [startCell, ...solutionPath];
    }


    async function handleHint() {
        if (viewMode !== "PLAY") {
            showMessage("WARNING", dialogMessages.play.switchToPlayFirst);
            return;
        }

        let availableSolution = playSolution;

        if (!availableSolution) {
            const response = await handleSolve("HINT_RETRY");

            if (response?.success && response.solutionPath) {
                availableSolution = response.solutionPath;
                setPlaySolution(response.solutionPath);
            }
        }

        if (!availableSolution) {
            setHintPath(null);
            showMessage("WARNING", dialogMessages.play.unableToSolveForHint);
            return;
        }

        const nextHintPath = getHintPathToNextWaypoint(availableSolution);

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
        let availableSolution = playSolution;

        if (!availableSolution) {
            const response = await handleSolve("HINT_RETRY");

            if (response?.success && response.solutionPath) {
                availableSolution = response.solutionPath;
                setPlaySolution(response.solutionPath);
            }
        }

        if (!availableSolution) {
            setHintPath(null);
            showMessage("WARNING", dialogMessages.play.unableToSolveForHint);
            return;
        }

        setHintPath(getNormalizedSolutionPath(availableSolution));
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
        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
        setHintPath(null);
    }


    /*
     * ============================
     * Screenshot import
     * ============================
     */
    async function handleImportScreenshot(
        file: File,
        imageBoardSize: GridSize,
    ) {

        if (
            imageBoardSize !== 6 &&
            imageBoardSize !== 7 &&
            imageBoardSize !== 8
        ) {

            showMessage(
                "WARNING",
                "Screenshot size must be 6, 7, or 8"
            );

            return;
        }

        const fileCheck = validateImageFile(file);

        if (!fileCheck.valid) {

            showMessage(
                "WARNING",
                fileCheck.reason
            );

            return;
        }


        try {

            setIsImporting(true);

            showMessage(
                "INFO",
                dialogMessages.import.sizeHint(imageBoardSize)
            );

            showMessage(
                "INFO",
                dialogMessages.import.started
            );


            const result = await importPuzzle(
                file,
                imageBoardSize
            );


            if (!result.board) {

                showMessage(
                    "ERROR",
                    result.message ||
                    dialogMessages.import.noBoardDetected
                );

                return;
            }


            const importedBoard = result.board;

            setBoard(importedBoard);
            setSolution(null);
            setPlaySolution(null);
            setHintPath(null);
            setMetrics(null);
            setEditMode("NUMBERS");
            setViewMode("BUILD");
            setPlayModeState(
                resetPlayModeState(importedBoard.waypoints[0] ?? null)
            );

            if (!result.valid) {

                showMessage(
                    "WARNING",
                    dialogMessages.import.invalidBoard(
                        result.errors[0]?.message ?? result.message
                    )
                );

                return;
            }


            if (result.warnings.length > 0) {

                showMessage(
                    "WARNING",
                    dialogMessages.import.succeededWithWarnings(
                        result.warnings.length
                    )
                );

                return;
            }


            showMessage(
                "SUCCESS",
                dialogMessages.import.succeeded(
                    importedBoard.waypoints.length,
                    importedBoard.walls.length
                )
            );

        }

        catch (error) {

            console.error(error);


            /*
             * The backend already explains the failure in its ErrorResponse; NO_BOARD_DETECTED
             * gets bespoke copy because the remedy ("show the whole grid") is specific
             * and worth spelling out.
             */
            if (error instanceof ApiError) {

                showMessage(
                    "ERROR",
                    error.code === "NO_BOARD_DETECTED"
                        ? dialogMessages.import.noBoardDetected
                        : dialogMessages.import.failed(error.message)
                );

                return;
            }


            showMessage(
                "ERROR",
                dialogMessages.import.failed(
                    "Unexpected error while reading the screenshot"
                )
            );

        }

        finally {

            setIsImporting(false);

        }

    }



    function handleReset() {

        setViewMode("BUILD");
        setEditMode("NUMBERS");

        setBoard(previous => ({
            boardSize: previous.boardSize,
            waypoints: [],
            walls: []
        }));

        clearDerivedSolverState();
        setPlayModeState(resetPlayModeState());


        showMessage(
            "INFO",
            dialogMessages.reset
        );

    }


    async function handleShare() {

        if (
            board.waypoints.length === 0 &&
            board.walls.length === 0
        ) {

            showMessage(
                "WARNING",
                dialogMessages.share.nothingToShare
            );

            return;
        }

        const shareUrl = createShareUrl(board);

        try {

            await navigator.clipboard.writeText(
                shareUrl
            );

            showMessage(
                "SUCCESS",
                dialogMessages.share.copied
            );

        }

        catch (error) {

            console.error(error);

            window.prompt(
                "Copy this share link:",
                shareUrl
            );

            showMessage(
                "WARNING",
                dialogMessages.share.clipboardDenied
            );

        }

    }



    function handleSelectExample(exampleBoard: BoardConfig, name: string) {
        setBoard(exampleBoard);
        clearDerivedSolverState();
        setPlayModeState(resetPlayModeState(exampleBoard.waypoints[0] ?? null));

        showMessage(
            "INFO",
            dialogMessages.examples.loaded(name)
        );
    }


    function handleModeChange(mode: EditMode) {
        setEditMode(mode);
        setPlaySolution(null);
        setHintPath(null);
        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
    }

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
                nextPosition[0] < 0 ||
                nextPosition[0] >= board.boardSize ||
                nextPosition[1] < 0 ||
                nextPosition[1] >= board.boardSize
            ) {
                return;
            }

            handleCellClick(nextPosition);
        };

        window.addEventListener("keydown", handleKeyDown);

        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [board.boardSize, board.waypoints, playModeState, viewMode]);

    function showMessage(
        type: AppMessage["type"],
        text: string
    ) {

        setMessage({
            id: crypto.randomUUID(),
            type,
            message: text,
            timestamp: new Date()
        });

    }

    const nextWaypoint = viewMode === "PLAY"
        ? getExpectedNextWaypoint(playModeState, board)
        : null;


    /*
     * ============================
     * Layout
     * ============================
     *
     * DOM order follows mobile layout:
     *
     * Control
     * Dialog
     * Grid
     * Actions
     * Metrics
     * Examples
     *
     */
    return (

        <div
            className="
                grid
                grid-cols-1
                gap-4
                mx-2

                lg:mx-auto
                lg:w-[70%]

                lg:grid-cols-[2fr_1fr]
                lg:items-start
            "
        >

            {/* --- LEFT COLUMN (Desktop) --- */}

            {/* Grid (top left) */}
            <div className="order-3 lg:order-1 lg:col-start-1">
                <Grid
                    board={board}
                    solution={viewMode === "BUILD" ? solution : null}
                    editMode={editMode}
                    playerPath={playModeState.visitedCells}
                    activePosition={getActivePosition(playModeState, board.waypoints[0] ?? null)}
                    nextWaypoint={nextWaypoint}
                    hintPosition={null}
                    hintPath={hintPath}
                    hintPathVersion={hintPathVersion}
                    isPlayMode={viewMode === "PLAY"}
                    pathShakeVersion={pathShakeVersion}
                    victoryVersion={victoryAnimationVersion}
                    onCellClick={handleCellClick}
                    onWallClick={handleWallClick}
                />
            </div>

            {/* Examples Section (bottom left, under grid) */}
            <div className="order-6 lg:order-2 lg:col-start-1">
                <ExamplesSection
                    currentBoardSize={board.boardSize}
                    onSelectExample={handleSelectExample}
                />
            </div>


            {/* --- RIGHT COLUMN (Desktop Wrapper) --- */}

            <div className="contents lg:flex lg:flex-col lg:gap-4 lg:col-start-2 lg:row-span-2 lg:order-1">

                {/* Controls */}
                <div className="order-1">
                    <ControlPanel
                        boardSize={board.boardSize}
                        editMode={editMode}
                        viewMode={viewMode}
                        isSolving={isSolving}
                        onGridSizeChange={handleGridSizeChange}
                        onEditModeChange={handleModeChange}
                        onHint={handleHint}
                        onClearSolution={handleClearPlayPath}
                        onUndo={() => {
                            setPlayModeState((previous) => undoVisitedCell(previous));
                        }}
                    />
                </div>

                {/* Dialog */}
                <div className="order-2">
                    <DialogPanel message={message} />
                </div>

                {/* Actions */}
                <div className="order-4 lg:order-3">
                    <ActionPanel
                        canSolve={board.waypoints.length >= 2}
                        canPlay={board.waypoints.length >= 2}
                        isSolving={isSolving}
                        isImporting={isImporting}
                        viewMode={viewMode}
                        onSolve={handleSolveClick}
                        onViewModeChange={handleViewModeChange}
                        onReset={handleReset}
                        onShare={handleShare}
                        onImport={handleImportScreenshot}
                    />
                </div>

                {/* Metrics */}
                <div className="order-5 lg:order-4">
                    <MetricsPanel metrics={metrics} />
                </div>

            </div>

        </div>
    );
}
