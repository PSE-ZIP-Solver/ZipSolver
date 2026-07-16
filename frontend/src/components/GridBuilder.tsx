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
    type Wall,
    type SolutionPath,
} from "../types/board";

import {
    type AppMessage,
} from "../types/message";

import {
    solvePuzzle,
} from "../services/apiCalls";


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
                waypoint =>
                    waypoint.position.row === position.row &&
                    waypoint.position.col === position.col
            );


        let updatedWaypoints;


        /*
         * Remove existing waypoint
         */
        if (existing) {

            updatedWaypoints =
                board.waypoints
                    .filter(
                        waypoint =>
                            waypoint !== existing
                    )
                    .map(
                        (waypoint, index) => ({
                            ...waypoint,
                            number: index + 1
                        })
                    );

        }


        /*
         * Add new waypoint
         */
        else {

            updatedWaypoints = [
                ...board.waypoints,
                {
                    number:
                        board.waypoints.length + 1,

                    position
                }
            ];

        }


        setBoard(previous => ({
            ...previous,
            waypoints: updatedWaypoints
        }));


        setSolution(null);
    }



    function handleWallClick(
        wall: Wall
    ) {

        if (editMode !== "WALLS")
            return;


        const exists =
            board.walls.some(
                item =>
                    item.neighborA.row === wall.neighborA.row &&
                    item.neighborA.col === wall.neighborA.col &&
                    item.neighborB.row === wall.neighborB.row &&
                    item.neighborB.col === wall.neighborB.col
            );


        const updatedWalls =
            exists

                ? board.walls.filter(
                    item =>
                        !(
                            item.neighborA.row === wall.neighborA.row &&
                            item.neighborA.col === wall.neighborA.col &&
                            item.neighborB.row === wall.neighborB.row &&
                            item.neighborB.col === wall.neighborB.col
                        )
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


            const response =
                await solvePuzzle(board);



            if (response.success) {

                setSolution(
                    response.solutionPath
                );


                showMessage(
                    "SUCCESS",
                    "Puzzle solved successfully"
                );

            }

            else {

                setSolution(null);


                showMessage(
                    "ERROR",
                    response.message
                );

            }


        }

        catch {

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
                lg:gap-6
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
                    lg:row-span-3
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

            <div
                className="
                    order-5
                    lg:col-span-2
                "
            >

                <MetricsPanel />

            </div>


        </div>
    );
}