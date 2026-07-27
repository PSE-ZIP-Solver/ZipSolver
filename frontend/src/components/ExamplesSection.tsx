// src/components/ExamplesSection.tsx
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

    const filteredExamples = Examples.filter(
        (ex) => ex.config.boardSize === currentBoardSize
    );

    return (
        <div className="bg-white border border-slate-200 rounded-2xl p-4 md:p-6 shadow-sm text-slate-800">
            <div className="flex justify-between items-baseline mb-1">
                <h2 className="text-xl font-bold text-slate-900">Examples</h2>
                <span className="text-xs font-mono bg-orange-50 text-orange-600 border border-orange-200 px-2 py-0.5 rounded-md font-semibold">
                    {currentBoardSize}×{currentBoardSize}
                </span>
            </div>

            <p className="text-xs text-slate-500 mb-4">
                Quick start with {currentBoardSize}×{currentBoardSize} templates – click any to load it
            </p>

            {filteredExamples.length === 0 ? (
                <div className="text-center py-6 text-sm text-slate-400 border border-dashed border-slate-200 rounded-xl">
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