import { useMemo } from 'react';

export default function MetricsPanel({ solutions, currentSolutionIndex }) {
  const metrics = useMemo(() => {
    if (solutions.length === 0) {
      return {
        totalSolutions: 0,
        currentSteps: 0,
        solveTime: 0,
        gridCells: 0,
        coverage: 0,
      };
    }

    const current = solutions[currentSolutionIndex];
    const totalCells = current.path.length;
    const timeMs = parseFloat(current.time);

    return {
      totalSolutions: Math.min(solutions.length, 50),
      currentSteps: totalCells,
      solveTime: timeMs,
      gridCells: totalCells,
      coverage: 100,
    };
  }, [solutions, currentSolutionIndex]);

  return (
    <div className="glass rounded-2xl p-4 w-full shadow-md">
      <h3 className="text-sm font-bold text-gray-800 uppercase mb-3 tracking-wide">
        Agent Metrics
      </h3>

      <div className="grid grid-cols-2 gap-2">
        {/* Metric Card: Total Solutions */}
        <div className="glass rounded-xl p-2.5 border">
          <p className="text-xs text-gray-600 font-semibold mb-1">Solutions</p>
          <p className="text-base font-bold text-orange-600">
            {metrics.totalSolutions >= 50 ? '50+' : metrics.totalSolutions}
          </p>
        </div>

        {/* Metric Card: Current Steps */}
        <div className="glass rounded-xl p-2.5 border">
          <p className="text-xs text-gray-600 font-semibold mb-1">Path Steps</p>
          <p className="text-base font-bold text-cyan-600">{metrics.currentSteps}</p>
        </div>

        {/* Metric Card: Solve Time */}
        <div className="glass rounded-xl p-2.5 border">
          <p className="text-xs text-gray-600 font-semibold mb-1">Time (ms)</p>
          <p className="text-base font-bold text-green-600">
            {metrics.solveTime.toFixed(1)}
          </p>
        </div>

        {/* Metric Card: Coverage */}
        <div className="glass rounded-xl p-2.5 border">
          <p className="text-xs text-gray-600 font-semibold mb-1">Coverage</p>
          <p className="text-base font-bold text-purple-600">{metrics.coverage}%</p>
        </div>
      </div>

      {/* Info Message */}
      <div className="mt-3 p-3 bg-blue-100 border border-blue-300 rounded-lg">
        <p className="text-xs text-blue-800 leading-relaxed">
          💡 This is a prototype. The metrics show DFS solver performance. In production, 
          these will display RL agent training metrics.
        </p>
      </div>
    </div>
  );
}
