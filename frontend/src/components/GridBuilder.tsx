import { useEffect, useRef, useState } from "react";

import Grid from "./Grid";
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
    type SolverMetrics
} from "../types/solver";

import {
    type AppMessage,
} from "../types/message";

import {
    solvePuzzle,
} from "../api/apiCalls";

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
    getHintPosition as getPlayHintPosition,
    hasCompletedAllWaypoints,
    isCellAlreadyVisited,
    resetPlayModeState,
    undoVisitedCell,
} from "../utils/playMode";


interface GridBuilderProps {
    advancedMode: boolean;
}

export default function GridBuilder({
    advancedMode
}: GridBuilderProps) {

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
                "Welcome to ZipSolver! Start placing waypoints and walls.",

            timestamp:
                new Date()
        });


    const [isSolving, setIsSolving] =
        useState(false);

    const [pathShakeVersion, setPathShakeVersion] =
        useState(0);

    const [playModeState, setPlayModeState] =
        useState(createPlayModeState(board.waypoints[0] ?? null));


    const sharedBoardLoadedRef =
        useRef(false);

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
        setMetrics(null);
        setPlayModeState(resetPlayModeState(sharedBoard.waypoints[0] ?? null));


        clearSharedBoardFromUrl();


        showMessage(
            "SUCCESS",
            "Board loaded from shared link"
        );

    }, []);


    /*
     * ============================
     * Board manipulation
     * ============================
     */
    function handleGridSizeChange(
        size: GridSize
    ) {

        setBoard({
            boardSize: size,
            waypoints: [],
            walls: [],
        });

        setSolution(null);
        setMetrics(null);
        setPlayModeState(resetPlayModeState());

        showMessage(
            "INFO",
            `Grid size changed to ${size}`
        );
    }


    function handleCellClick(
        position: Position
    ) {

        if (viewMode === "PLAY") {
            const currentPosition = getActivePosition(playModeState, board.waypoints[0] ?? null);

            if (!currentPosition) {
                showMessage("WARNING", "Add at least one waypoint before playing");
                return;
            }

            if (position[0] === currentPosition[0] && position[1] === currentPosition[1]) {
                showMessage("INFO", "You are already on this cell");
                return;
            }

            const previousPosition = playModeState.visitedCells.length > 1
                ? playModeState.visitedCells[playModeState.visitedCells.length - 2]
                : null;

            if (previousPosition && position[0] === previousPosition[0] && position[1] === previousPosition[1]) {
                setPlayModeState((previous) => undoVisitedCell(previous));
                showMessage("INFO", "Undid the last move");
                return;
            }

            const expectedWaypoint = getExpectedNextWaypoint(playModeState, board);
            const targetIsWaypoint = board.waypoints.some((waypoint) => waypoint[0] === position[0] && waypoint[1] === position[1]);

            if (targetIsWaypoint && expectedWaypoint) {
                const isExpectedWaypoint = position[0] === expectedWaypoint[0] && position[1] === expectedWaypoint[1];

                if (!isExpectedWaypoint) {
                    showMessage("WARNING", "You must visit the waypoints in order");
                    return;
                }
            }

            if (!isValidGameMove(currentPosition, position, board)) {
                showMessage("WARNING", "This move is not valid");
                return;
            }

            if (isCellAlreadyVisited(playModeState, position)) {
                setPathShakeVersion((previous) => previous + 1);
                showMessage("WARNING", "This cell was already visited");
                return;
            }

            const nextState = {
                ...playModeState,
                visitedCells: [...playModeState.visitedCells, position],
            };

            setPlayModeState((previous) => appendVisitedCell(previous, position));

            if (hasCompletedAllWaypoints(nextState, board)) {
                showMessage("SUCCESS", "Puzzle solved! You visited every cell and all waypoints in order.");
                return;
            }

            const lastWaypoint = board.waypoints[board.waypoints.length - 1] ?? null;
            const reachedLastWaypoint = lastWaypoint
                ? position[0] === lastWaypoint[0] && position[1] === lastWaypoint[1]
                : false;

            if (reachedLastWaypoint) {
                showMessage("INFO", "You reached the last waypoint, but you still need to visit every cell to solve the puzzle.");
                return;
            }

            showMessage("INFO", `Moved to (${position[0] + 1}, ${position[1] + 1})`);
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


        setSolution(null);
        setMetrics(null);
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


        setSolution(null);
        setMetrics(null);
    }



    /*
     * ============================
     * Solver
     * ============================
     */
    async function handleSolve() {

        if (board.waypoints.length < 2) {

            showMessage(
                "WARNING",
                "Add at least two waypoints first"
            );

            return;
        }


        try {

            setIsSolving(true);


            const response = await solvePuzzle(board);

            setMetrics(response.metrics ?? null);


            if (response.success && response.solutionPath) {

                setSolution(response.solutionPath);


                if (response.solverUsed === "RL") {

                    showMessage(
                        "SUCCESS",
                        "Puzzle solved successfully using RL solver"
                    );

                }

                else if (response.solverUsed === "DFS") {

                    showMessage(
                        "WARNING",
                        [
                            "Puzzle solved using DFS fallback",
                            response.message
                        ].join("\n")
                    );

                }


                return;
            }


            setSolution(null);


            switch (response.status) {

                case "UNSOLVABLE":

                    showMessage(
                        "ERROR",
                        [
                            "Puzzle is not solvable",
                            response.message
                        ].join("\n")
                    );

                    break;


                case "TIMEOUT":

                    showMessage(
                        "ERROR",
                        [
                            "Solver timed out",
                            response.message
                        ].join("\n")
                    );

                    break;


                case "FAILED":

                    showMessage(
                        "ERROR",
                        [
                            "Solver failed",
                            response.message
                        ].join("\n")
                    );

                    break;


                default:

                    showMessage(
                        "ERROR",
                        response.message || "Unknown solver error"
                    );

                    break;
            }


        }

        catch (error) {

            console.error(error);


            setSolution(null);
            setMetrics(null);


            showMessage(
                "ERROR",
                "Solver request failed"
            );

        }

        finally {

            setIsSolving(false);

        }

    }



    function handleReset() {

        setBoard(previous => ({
            boardSize: previous.boardSize,
            waypoints: [],
            walls: []
        }));

        setSolution(null);
        setMetrics(null);
        setPlayModeState(resetPlayModeState());


        showMessage(
            "INFO",
            "Puzzle reset"
        );

    }


    async function handleShare() {

        if (
            board.waypoints.length === 0 &&
            board.walls.length === 0
        ) {

            showMessage(
                "WARNING",
                "Nothing to share"
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
                "Share link copied to clipboard"
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
                "Clipboard access denied. Share link opened manually."
            );

        }

    }


    
    function handleSelectExample(exampleBoard: BoardConfig, name: string) {
        setBoard(exampleBoard);
        setSolution(null);
        setMetrics(null);
        setPlayModeState(resetPlayModeState(exampleBoard.waypoints[0] ?? null));

        showMessage(
            "SUCCESS",
            `Loaded example: ${name}`
        );
    }


    function handleHint() {
        if (viewMode !== "PLAY") {
            showMessage("WARNING", "Switch to Play mode first");
            return;
        }

        const currentPosition = getActivePosition(playModeState, board.waypoints[0] ?? null);
        const suggestedPosition = getPlayHintPosition(solution, playModeState, board);

        if (!currentPosition || !suggestedPosition) {
            showMessage("WARNING", "Solve the puzzle to unlock hints");
            return;
        }

        if (suggestedPosition[0] === currentPosition[0] && suggestedPosition[1] === currentPosition[1]) {
            showMessage("INFO", "You are already on the suggested cell");
            return;
        }

        if (!isValidGameMove(currentPosition, suggestedPosition, board)) {
            showMessage("WARNING", "The hinted move is blocked by a wall");
            return;
        }

        setPlayModeState((previous) => appendVisitedCell(previous, suggestedPosition));
        showMessage("INFO", `Hint applied to (${suggestedPosition[0] + 1}, ${suggestedPosition[1] + 1})`);
    }

    function handleModeChange(mode: EditMode) {
        setEditMode(mode);
        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
    }

    function handleViewModeChange(mode: ViewMode) {
        setViewMode(mode);

        if (mode === "PLAY") {
            setPlayModeState(createPlayModeState(board.waypoints[0] ?? null));
            showMessage("INFO", "Play mode started. Choose a neighboring cell to continue");
            return;
        }

        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
    }

    useEffect(() => {
        if (viewMode !== "PLAY") {
            return;
        }

        const handleKeyDown = (event: KeyboardEvent) => {
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
                    solution={solution}
                    editMode={editMode}
                    playerPath={playModeState.visitedCells}
                    activePosition={getActivePosition(playModeState, board.waypoints[0] ?? null)}
                    hintPosition={getPlayHintPosition(solution, playModeState, board)}
                    isPlayMode={viewMode === "PLAY"}
                    pathShakeVersion={pathShakeVersion}
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
                        onUndo={() => {
                            setPlayModeState((previous) => undoVisitedCell(previous));
                            showMessage("INFO", "Last move undone");
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
                        isSolving={isSolving}
                        viewMode={viewMode}
                        onSolve={handleSolve}
                        onViewModeChange={handleViewModeChange}
                        onReset={handleReset}
                        onShare={handleShare}
                    />
                </div>

                {/* Metrics */}
                {advancedMode && (
                    <div className="order-5 lg:order-4">
                        <MetricsPanel metrics={metrics} />
                    </div>
                )}

            </div>

        </div>
    );
}