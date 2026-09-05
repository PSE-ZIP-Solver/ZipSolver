import type { EditMode, GridSize, ViewMode } from "../types/grid";


/** Controls for switching edit modes, board sizes, and play actions. */
interface ControlPanelProps {

    boardSize: GridSize;

    editMode: EditMode;

    viewMode: ViewMode;

    isSolving: boolean;

    onGridSizeChange:
    (size: GridSize) => void;

    onEditModeChange:
    (mode: EditMode) => void;

    onHint: () => void;

    onClearSolution: () => void;

    onUndo: () => void;
}


const availableSizes: GridSize[] = [
    6,
    7,
    8,
];


const editModes: EditMode[] = [
    "NUMBERS",
    "WALLS",
];


/** Renders controls whose available actions depend on the current view mode. */
export default function ControlPanel({
    boardSize,
    editMode,
    viewMode,
    isSolving,
    onGridSizeChange,
    onEditModeChange,
    onHint,
    onClearSolution,
    onUndo,
}: ControlPanelProps) {


    return (
        <section className="panel-card flex flex-col gap-4 rounded-xl p-4">
            {viewMode === "BUILD" ? (
                <div className="flex flex-col gap-2">
                    <h2 className="text-sm font-semibold text-text">Edit mode</h2>

                    <div className="flex overflow-hidden rounded-lg ring-1 ring-board-border">
                        {editModes.map((mode) => (
                            <button
                                key={mode}
                                type="button"
                                disabled={isSolving}
                                onClick={() => onEditModeChange(mode)}
                                className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ui-transition ${editMode === mode
                                    ? "bg-primary text-on-primary"
                                    : "bg-background/80 text-text hover:bg-primary-hover hover:text-on-primary"
                                    } disabled:cursor-not-allowed disabled:opacity-50`}
                            >
                                {mode === "NUMBERS" ? "Numbers" : "Walls"}
                            </button>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="flex flex-col gap-2">
                    <h2 className="text-sm font-semibold text-text">Play mode</h2>
                    <button
                        type="button"
                        onClick={onHint}
                        disabled={isSolving}
                        className="w-full rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-on-primary transition-colors ui-transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        Take Hint
                    </button>
                    <div className="grid grid-cols-2 gap-2">
                        <button
                            type="button"
                            onClick={onClearSolution}
                            disabled={isSolving}
                            className="rounded-lg border border-board-border bg-background/80 px-4 py-2 text-sm font-semibold text-text transition-colors ui-transition hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            Clear Solution
                        </button>
                        <button
                            type="button"
                            onClick={onUndo}
                            disabled={isSolving}
                            className="rounded-lg border border-board-border bg-background/80 px-4 py-2 text-sm font-semibold text-text transition-colors ui-transition hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            Undo
                        </button>
                    </div>
                </div>
            )}

            <div className="flex justify-center">
                {viewMode === "BUILD" && (
                    <div className="flex flex-wrap justify-center gap-2">
                        {availableSizes.map((size) => (
                            <button
                                key={size}
                                type="button"
                                disabled={isSolving}
                                onClick={() => onGridSizeChange(size)}
                                className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ui-transition ${boardSize === size
                                    ? "bg-primary text-on-primary"
                                    : "bg-background/80 text-text ring-1 ring-board-border hover:bg-primary-hover hover:text-on-primary"
                                    } disabled:cursor-not-allowed disabled:opacity-50`}
                            >
                                {size}×{size}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
}