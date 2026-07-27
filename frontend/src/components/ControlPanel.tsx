import type { EditMode, GridSize } from "../types/grid";


interface ControlPanelProps {

    boardSize: GridSize;

    editMode: EditMode;

    isSolving: boolean;

    onGridSizeChange:
    (size: GridSize) => void;

    onEditModeChange:
    (mode: EditMode) => void;
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


export default function ControlPanel({
    boardSize,
    editMode,
    isSolving,
    onGridSizeChange,
    onEditModeChange,
}: ControlPanelProps) {


    return (
        <section
            className="panel-card flex flex-col gap-4 rounded-xl p-4"
        >
            {/* Edit mode selection */}

            <div
                className="
                    flex
                    flex-col
                    gap-2
                "
            >

                <h2
                    className="
                        text-sm
                        font-semibold
                        text-text
                    "
                >
                    Edit mode
                </h2>


                <div
                    className="
                        flex
                        overflow-hidden
                        rounded-lg
                        ring-1
                        ring-board-border
                    "
                >

                    {editModes.map((mode) => (

                        <button
                            key={mode}
                            type="button"
                            disabled={isSolving}
                            onClick={() =>
                                onEditModeChange(mode)
                            }

                            className={`
                                flex-1
                                px-4
                                py-2
                                text-sm
                                font-medium
                                transition-colors

                                ${editMode === mode

                                    ? `
                                        bg-primary
                                        text-white
                                    `

                                    : `
                                        bg-background/80
                                        text-text
                                        hover:bg-primary-hover
                                        hover:text-white
                                    `
                                }

                                disabled:cursor-not-allowed
                                disabled:opacity-50
                            `}
                        >
                            {
                                mode === "NUMBERS"
                                    ? "Numbers"
                                    : "Walls"
                            }

                        </button>

                    ))}

                </div>

            </div>



            <div
                className="
                    flex
                    justify-center
                "
            >

                <div
                    className="
                        flex
                        gap-2
                        flex-wrap
                        justify-center
                    "
                >

                    {availableSizes.map((size) => (

                        <button
                            key={size}
                            type="button"
                            disabled={isSolving}
                            onClick={() =>
                                onGridSizeChange(size)
                            }

                            className={`
                                rounded-lg
                                px-4
                                py-2
                                text-sm
                                font-medium
                                transition-colors

                                ${boardSize === size

                                    ? `
                                        bg-primary
                                        text-white
                                    `

                                    : `
                                        bg-background/80
                                        text-text
                                        ring-1
                                        ring-board-border
                                        hover:bg-primary-hover
                                        hover:text-white
                                    `
                                }

                                disabled:cursor-not-allowed
                                disabled:opacity-50
                            `}
                        >
                            {size}×{size}

                        </button>

                    ))}

                </div>

            </div>

        </section>
    );
}