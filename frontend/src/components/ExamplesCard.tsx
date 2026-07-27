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
                bg-[#121926] hover:bg-[#1b263b]
                border border-[#233044] hover:border-orange-500/50
                rounded-lg transition-all duration-150 group cursor-pointer
            "
        >
            {/* Mini Grid Vorschau */}
            <div className="w-32 h-32 bg-[#0d131d] border border-gray-800 rounded relative mb-3 flex items-center justify-center">
                <MiniGridPreview config={config} />
            </div>

            {/* Titel & Größengabe */}
            <span className="font-semibold text-sm text-gray-200 group-hover:text-orange-400 transition-colors">
                {title}
            </span>
            <span className="text-xs text-gray-500">
                {config.boardSize}×{config.boardSize}
            </span>
        </button>
    );
}

// helper for rendering the mini grid
function MiniGridPreview({ config }: { config: BoardConfig }) {
    const size = config.boardSize;

    // Hilfsfunktion: Prüft, ob zwischen der aktuellen Zelle (r, c) und ihren Nachbarn eine Wand steht
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

    return (
        <div
            className="grid w-full h-full p-1 gap-[1px] bg-gray-800/40 relative"
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
                    <div key={idx} className="bg-[#0d131d] relative flex items-center justify-center">
                        {/* Rechte Wand */}
                        {wallRight && (
                            <div className="absolute right-0 top-0 bottom-0 w-[2px] bg-gray-300 z-10" />
                        )}
                        {/* Untere Wand */}
                        {wallBottom && (
                            <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gray-300 z-10" />
                        )}

                        {/* Waypoint Kreis */}
                        {wpIndex !== -1 && (
                            <span className="w-3.5 h-3.5 rounded-full bg-orange-600 text-[9px] font-bold text-white flex items-center justify-center z-20">
                                {wpIndex + 1}
                            </span>
                        )}
                    </div>
                );
            })}
        </div>
    );
}