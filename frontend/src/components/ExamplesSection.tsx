import { Examples } from "../data/examplesData";
import { type BoardConfig, type GridSize } from "../types/board";
import ExampleCard from "./ExamplesCard";

interface ExamplesSectionProps {
    currentBoardSize: GridSize;
    onSelectExample: (board: BoardConfig, name: string) => void;
}

export default function ExamplesSection({
    currentBoardSize,
    onSelectExample
}: ExamplesSectionProps) {

    // Gefilterte Beispiele nach aktueller Grid-Größe
    const filteredExamples = Examples.filter(
        (ex) => ex.config.boardSize === currentBoardSize
    );

    return (
        <div className="bg-[#1a1514] border border-[#2a201e] rounded-xl p-4 text-white">
            <div className="flex justify-between items-baseline mb-1">
                <h2 className="text-xl font-bold">Examples</h2>
                <span className="text-xs font-mono bg-orange-950/60 text-orange-400 border border-orange-800/40 px-2 py-0.5 rounded">
                    {currentBoardSize}×{currentBoardSize}
                </span>
            </div>

            <p className="text-xs text-gray-400 mb-4">
                Quick start with {currentBoardSize}×{currentBoardSize} templates – click any to load it
            </p>

            {filteredExamples.length === 0 ? (
                <div className="text-center py-6 text-sm text-gray-500 border border-dashed border-gray-800 rounded-lg">
                    No templates available for {currentBoardSize}×{currentBoardSize} yet.
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {filteredExamples.map((example) => (
                        <ExampleCard
                            key={example.id}
                            title={example.name}
                            config={example.config}
                            onSelect={() => onSelectExample(example.config, example.name)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}