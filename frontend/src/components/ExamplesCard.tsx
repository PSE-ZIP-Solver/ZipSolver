// src/components/ExampleCard.tsx
import { type BoardConfig } from "../types/board";

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
            onClick={onSelect}
            className="
                flex flex-col items-center p-3 w-full
                bg-white hover:bg-slate-50
                border border-slate-200 hover:border-orange-500
                rounded-xl shadow-sm hover:shadow
                transition-all duration-150 group cursor-pointer
            "
        >
            {/* Mini Grid Vorschau */}
            <div className="w-32 h-32 bg-slate-100 border border-slate-200 rounded-lg relative mb-3 flex items-center justify-center p-1 overflow-hidden">
                <MiniGridPreview config={config} />
            </div>

            {/* Titel & Größenangabe */}
            <span className="font-semibold text-sm text-slate-800 group-hover:text-orange-600 transition-colors">
                {title}
            </span>
            <span className="text-xs text-slate-500">
                {config.boardSize}×{config.boardSize}
            </span>
        </button>
    );
}

// Helper for displaying the mini grid
function MiniGridPreview({ config }: { config: BoardConfig }) {
    const size = config.boardSize;

    // checks if a wall exists
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

    // The size of the waypoints gets adjusted dynamically for the preview
    const badgeSizeClass = size === 8 
        ? "w-2.5 h-2.5 text-[7px]" 
        : size === 7 
        ? "w-3 h-3 text-[8px]" 
        : "w-3.5 h-3.5 text-[9px]";

    return (
        <div
            className="grid w-full h-full gap-[1px] bg-slate-200 rounded overflow-hidden relative"
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
                    <div key={idx} className="bg-white relative flex items-center justify-center">
                        
                        {/* right wall */}
                        {wallRight && (
                            <div className="absolute right-0 top-0 bottom-0 w-[2px] bg-slate-800 z-20 translate-x-1/2 pointer-events-none" />
                        )}

                        {/* bottom wall */}
                        {wallBottom && (
                            <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-slate-800 z-20 translate-y-1/2 pointer-events-none" />
                        )}

                        {/* Waypoint Badge */}
                        {wpIndex !== -1 && (
                            <span 
                                className={`
                                    ${badgeSizeClass} 
                                    rounded-full bg-orange-500 font-bold text-white 
                                    flex items-center justify-center z-10 shadow-xs leading-none
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