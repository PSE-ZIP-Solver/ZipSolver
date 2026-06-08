import ExampleCard from './ExampleCard';
import { getExamplesForSize } from '../data/examplesData';

export default function ExamplesSection({ gridSize, onExampleSelect }) {
  const examples = getExamplesForSize(gridSize);

  // Only show section if there are examples for this grid size
  if (!examples || examples.length === 0) {
    return null;
  }

  return (
    <section className="w-full py-8">
      <div className="max-w-7xl mx-auto px-6">
        <div className="bg-white/50 backdrop-blur-md dark:bg-gray-900/50 border border-white/80 dark:border-gray-600/80 rounded-2xl p-8 transition-colors duration-200">
          {/* Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Examples
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Quick start with {gridSize}×{gridSize} maze templates - click any to load it
            </p>
          </div>

          {/* Examples grid */}
          <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-2 gap-4">
            {examples.map((example) => (
              <ExampleCard
                key={example.id}
                example={example}
                onSelect={onExampleSelect}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
