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

import { dialogMessages } from "../data/dialogMessages";

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
                dialogMessages.welcome,

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
                showMessage("INFO", dialogMessages.play.lastMoveUndone);
                return;
            }

            const expectedWaypoint = getExpectedNextWaypoint(playModeState, board);
            const targetIsWaypoint = board.waypoints.some((waypoint) => waypoint[0] === position[0] && waypoint[1] === position[1]);

            if (targetIsWaypoint && expectedWaypoint) {
                const isExpectedWaypoint = position[0] === expectedWaypoint[0] && position[1] === expectedWaypoint[1];

                if (!isExpectedWaypoint) {
                    showMessage("WARNING", dialogMessages.play.waypointOrder);
                    return;
                }
            }

            if (!isValidGameMove(currentPosition, position, board)) {
                showMessage("WARNING", dialogMessages.play.invalidMove);
                return;
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

            setPlayModeState((previous) => appendVisitedCell(previous, position));

            if (hasCompletedAllWaypoints(nextState, board)) {
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

            showMessage("INFO", dialogMessages.play.movedTo(position));
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
                dialogMessages.solve.addWaypointsFirst
            );

            return;
        }


        try {

            setIsSolving(true);


            const response = await solvePuzzle(board);

            setMetrics(response.metrics ?? null);


            if (response.success && response.solutionPath) {

                setSolution(response.solutionPath);

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

        catch (error) {

            console.error(error);


            setSolution(null);
            setMetrics(null);


            showMessage(
                "ERROR",
                dialogMessages.solve.requestFailed
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
        setSolution(null);
        setMetrics(null);
        setPlayModeState(resetPlayModeState(exampleBoard.waypoints[0] ?? null));

        showMessage(
            "INFO",
            dialogMessages.examples.loaded(name)
        );
    }


    function handleHint() {
        if (viewMode !== "PLAY") {
            showMessage("WARNING", dialogMessages.play.switchToPlayFirst);
            return;
        }

        const currentPosition = getActivePosition(playModeState, board.waypoints[0] ?? null);
        const suggestedPosition = getPlayHintPosition(solution, playModeState, board);

        if (!currentPosition || !suggestedPosition) {
            showMessage("WARNING", dialogMessages.play.hintLocked);
            return;
        }

        if (suggestedPosition[0] === currentPosition[0] && suggestedPosition[1] === currentPosition[1]) {
            showMessage("INFO", dialogMessages.play.hintAlreadyHere);
            return;
        }

        if (!isValidGameMove(currentPosition, suggestedPosition, board)) {
            showMessage("WARNING", dialogMessages.play.hintBlocked);
            return;
        }

        setPlayModeState((previous) => appendVisitedCell(previous, suggestedPosition));
        showMessage("INFO", dialogMessages.play.hintApplied(suggestedPosition));
    }

    function handleModeChange(mode: EditMode) {
        setEditMode(mode);
        setPlayModeState(resetPlayModeState(board.waypoints[0] ?? null));
    }

    function handleViewModeChange(mode: ViewMode) {
        setViewMode(mode);

        if (mode === "PLAY") {
            setPlayModeState(createPlayModeState(board.waypoints[0] ?? null));
            showMessage("INFO", dialogMessages.mode.playEnabled);
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