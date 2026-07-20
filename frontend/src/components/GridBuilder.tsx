import { useState } from "react";

import Grid from "./Grid";
import ControlPanel from "./ControlPanel";
import DialogPanel from "./DialogPanel";
import ActionPanel from "./ActionPanel";
import MetricsPanel from "./MetricsPanel";

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

        setBoard({
            boardSize: 6,
            waypoints: [],
            walls: []
        });


        setSolution(null);
        setMetrics(null);


        showMessage(
            "INFO",
            "Puzzle reset"
        );

    }

    function handleImport() {
        // TODO
    }


    function handleExport() {
        // TODO
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
            "
        >


            {/* Controls */}

            <div
                className="
                    order-1
                    lg:order-2
                "
            >

                <ControlPanel
                    boardSize={board.boardSize}
                    editMode={editMode}
                    isSolving={isSolving}

                    onGridSizeChange={
                        handleGridSizeChange
                    }

                    onEditModeChange={
                        setEditMode
                    }
                />

            </div>



            {/* Dialog */}

            <div
                className="
                    order-2

                    lg:order-2
                "
            >

                <DialogPanel
                    message={message}
                />

            </div>



            {/* Grid */}

            <div
                className="
                    order-3

                    lg:order-1
                    lg:row-span-4
                "
            >

                <Grid
                    board={board}
                    solution={solution}
                    editMode={editMode}

                    onCellClick={
                        handleCellClick
                    }

                    onWallClick={
                        handleWallClick
                    }
                />

            </div>



            {/* Actions */}

            <div
                className="
                    order-4

                    lg:order-3
                "
            >

                <ActionPanel
                    canSolve={board.waypoints.length >= 2}

                    isSolving={isSolving}

                    onSolve={
                        handleSolve
                    }

                    onReset={
                        handleReset
                    }

                    onImport={
                        handleImport
                    }

                    onExport={
                        handleExport
                    }
                />

            </div>


            {/* Metrics */}

            {
                advancedMode && (
                    <div
                        className="
                order-5
                lg:order-4
            "
                    >
                        <MetricsPanel
                            metrics={metrics}
                        />
                    </div>
                )
            }


        </div>
    );
}