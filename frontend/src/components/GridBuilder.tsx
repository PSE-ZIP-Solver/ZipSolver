import { useEffect, useRef, useState } from "react";

import Grid from "./Grid";
import ControlPanel from "./ControlPanel";
import DialogPanel from "./DialogPanel";
import ActionPanel from "./ActionPanel";
import MetricsPanel from "./MetricsPanel";
import ExamplesSection from "./ExamplesSection"; // 1. NEUER IMPORT

import {
    type EditMode,
    type GridSize
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

        showMessage(
            "INFO",
            `Grid size changed to ${size}`
        );
    }


    function handleCellClick(
        position: Position
    ) {

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


    /* 2. NEUE HANDLER-FUNKTION FÜR BEISPIEL-SELEKTION */
    function handleSelectExample(exampleBoard: BoardConfig, name: string) {
        setBoard(exampleBoard);
        setSolution(null);
        setMetrics(null);

        showMessage(
            "SUCCESS",
            `Loaded example: ${name}`
        );
    }


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

            {/* --- LINKE SPALTE (Desktop) --- */}

            {/* Grid (Oben links) */}
            <div className="order-3 lg:order-1 lg:col-start-1">
                <Grid
                    board={board}
                    solution={solution}
                    editMode={editMode}
                    onCellClick={handleCellClick}
                    onWallClick={handleWallClick}
                />
            </div>

            {/* Examples Section (Unten links, direkt unter dem Grid) */}
            <div className="order-6 lg:order-2 lg:col-start-1">
                <ExamplesSection
                    currentBoardSize={board.boardSize}
                    onSelectExample={handleSelectExample}
                />
            </div>


            {/* --- RECHTE SPALTE (Desktop Wrapper) --- */}
            
            {/* 
                Auf Desktop (lg) fassen wir alle rechten Panels in einer Spalte zusammen.
                Dadurch rücken Dialog, Actions & Metrics direkt unter das ControlPanel!
            */}
            <div className="contents lg:flex lg:flex-col lg:gap-4 lg:col-start-2 lg:row-span-2 lg:order-1">

                {/* Controls */}
                <div className="order-1">
                    <ControlPanel
                        boardSize={board.boardSize}
                        editMode={editMode}
                        isSolving={isSolving}
                        onGridSizeChange={handleGridSizeChange}
                        onEditModeChange={setEditMode}
                    />
                </div>

                {/* Dialog (Rückt jetzt direkt unter das ControlPanel) */}
                <div className="order-2">
                    <DialogPanel message={message} />
                </div>

                {/* Actions */}
                <div className="order-4 lg:order-3">
                    <ActionPanel
                        canSolve={board.waypoints.length >= 2}
                        isSolving={isSolving}
                        onSolve={handleSolve}
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