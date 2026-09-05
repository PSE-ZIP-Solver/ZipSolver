import { type BoardConfig } from "../types/board";

/** Data and callback needed to render one selectable example board. */
interface ExampleCardProps {
    title: string;
    config: BoardConfig;
    onSelect: () => void;
}

export default function ExampleCard({
    title,
    config,
    onSelect
}: ExampleCardProps) {
    return (
        <button
            type="button"
            onClick={onSelect}
            className="
                flex flex-col items-center p-3 w-full
                bg-board-cell hover:bg-board-cell-hover
                border border-board-border hover:border-primary
                rounded-xl shadow-xs hover:shadow-md
                transition-all ui-transition group cursor-pointer
            "
        >
            {/* Mini Grid Preview */}
            <div className="w-32 h-32 bg-background border border-board-border rounded-lg relative mb-3 flex items-center justify-center p-1 overflow-hidden">
                <MiniGridPreview config={config} />
            </div>

            {/* Title and Gridsize */}
            <span className="font-semibold text-sm text-text group-hover:text-primary transition-colors ui-transition">
                {title}
            </span>
            <span className="text-xs opacity-60">
                {config.boardSize}×{config.boardSize}
            </span>
        </button>
    );
}

function MiniGridPreview({ config }: { config: BoardConfig }) {
    const size = config.boardSize;

    const hasWall = (r: number, c: number, direction: 'right' | 'bottom') => {
        const nextR = direction === 'bottom' ? r + 1 : r;
        const nextC = direction === 'right' ? c + 1 : c;

        return config.walls.some((wall) => {
            const [aR, aC] = wall.neighborA;
            const [bR, bC] = wall.neighborB;

            const isA = aR === r && aC === c;
            const isB = bR === nextR && bC === nextC;

            const isA_rev = aR === nextR && aC === nextC;
            const isB_rev = bR === r && bC === c;

            return (isA && isB) || (isA_rev && isB_rev);
        });
    };

    const badgeSizeClass = size === 8 
        ? "w-2.5 h-2.5 text-[7px]" 
        : size === 7 
        ? "w-3 h-3 text-[8px]" 
        : "w-3.5 h-3.5 text-[9px]";

    return (
        <div
            className="grid w-full h-full gap-px bg-board-gridline rounded overflow-hidden relative"
            style={{
                gridTemplateColumns: `repeat(${size}, minmax(0, 1fr))`,
                gridTemplateRows: `repeat(${size}, minmax(0, 1fr))`,
            }}
        >
            {Array.from({ length: size * size }).map((_, idx) => {
                const r = Math.floor(idx / size);
                const c = idx % size;

                const wpIndex = config.waypoints.findIndex(
                    ([row, col]) => row === r && col === c
                );

                const wallRight = hasWall(r, c, 'right');
                const wallBottom = hasWall(r, c, 'bottom');

                return (
                    <div key={idx} className="bg-board-cell relative flex items-center justify-center">
                        
                        {wallRight && (
                            <div className="grid-wall absolute right-0 top-0 bottom-0 w-0.5 z-20 translate-x-1/2 pointer-events-none" />
                        )}

                        {wallBottom && (
                            <div className="grid-wall absolute bottom-0 left-0 right-0 h-0.5 z-20 translate-y-1/2 pointer-events-none" />
                        )}

                        {wpIndex !== -1 && (
                            <span 
                                className={`
                                    ${badgeSizeClass} 
                                    grid-waypoint rounded-full font-bold text-on-primary 
                                    flex items-center justify-center z-10 leading-none
                                `}
                            >
                                {wpIndex + 1}
                            </span>
                        )}
                    </div>
                );
            })}
        </div>
    );
}