import Grid from "./Grid.tsx";
import ControlPanel from "./ControlPanel";
import DialogPanel from "./DialogPanel";
import ActionPanel from "./ActionPanel";
import MetricsPanel from "./MetricsPanel";
import ExamplesSection from "./ExamplesSection";
import useGridBuilderState from "../hooks/useGridBuilderState";

/** Composes the grid builder layout from the feature state hook and presentational panels. */
export default function GridBuilder() {
    const {
        board,
        solution,
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
        nextWaypoint,
        activePosition,
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
        handleUndo,
    } = useGridBuilderState();

    /* DOM order is kept aligned with the mobile layout before desktop CSS reorders columns. */
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
            <div className="order-3 lg:order-1 lg:col-start-1">
                <Grid
                    board={board}
                    solution={viewMode === "BUILD" ? solution : null}
                    editMode={editMode}
                    playerPath={playModeState.visitedCells}
                    activePosition={activePosition}
                    nextWaypoint={nextWaypoint}
                    hintPath={hintPath}
                    hintPathVersion={hintPathVersion}
                    isPlayMode={viewMode === "PLAY"}
                    pathShakeVersion={pathShakeVersion}
                    victoryVersion={victoryAnimationVersion}
                    onCellClick={handleCellClick}
                    onWallClick={handleWallClick}
                />
            </div>

            <div className="order-6 lg:order-2 lg:col-start-1">
                <ExamplesSection
                    currentBoardSize={board.boardSize}
                    onSelectExample={handleSelectExample}
                />
            </div>

            <div className="contents lg:flex lg:flex-col lg:gap-4 lg:col-start-2 lg:row-span-2 lg:order-1">
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
                        onUndo={handleUndo}
                    />
                </div>

                <div className="order-2">
                    <DialogPanel message={message} />
                </div>

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

                <div className="order-5 lg:order-4">
                    <MetricsPanel metrics={metrics} />
                </div>
            </div>
        </div>
    );
}
