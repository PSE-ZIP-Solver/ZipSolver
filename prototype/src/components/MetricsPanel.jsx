import { useMemo } from 'react';

export default function MetricsPanel({ solutions, currentSolutionIndex }) {
  const metrics = useMemo(() => {
    if (solutions.length === 0) {
      return {
        averageReward: 0,
        episodeSteps: 0,
        trainingProgress: 0,
        convergenceRate: 0,
      };
    }

    // Generate realistic RL metrics with some randomness
    const episode = currentSolutionIndex + 1;
    const baseFactor = Math.log(episode + 1);

    return {
      averageReward: (Math.random() * 50 + 30).toFixed(2),
      episodeSteps: Math.floor(Math.random() * 100 + 50),
      trainingProgress: Math.min(95, Math.floor(baseFactor * 15 + Math.random() * 10)),
      convergenceRate: (Math.random() * 0.8 + 0.2).toFixed(3),
    };
  }, [solutions, currentSolutionIndex]);

  return (
    <div className="bg-white/50 backdrop-blur-md border border-white/80 dark:bg-gray-900/50 dark:border-gray-600/80 rounded-2xl p-4 w-full shadow-md">
      <h3 className="text-sm font-bold text-black dark:text-gray-300 uppercase mb-3 tracking-wide">
        Agent Metrics
      </h3>

      <div className="grid grid-cols-2 gap-2">
        {/* Metric Card: Average Reward */}
        <div className="bg-white/50 backdrop-blur-md border border-white/80 dark:bg-gray-900/50 dark:border-gray-600/80 rounded-xl p-2.5 transition-colors">
          <p className="text-xs text-gray-600 dark:text-gray-400 font-semibold mb-1">Avg Reward</p>
          <p className="text-base font-bold text-orange-600 dark:text-orange-400">
            {metrics.averageReward}
          </p>
        </div>

        {/* Metric Card: Episode Steps */}
        <div className="bg-white/50 backdrop-blur-md border border-white/80 dark:bg-gray-900/50 dark:border-gray-600/80 rounded-xl p-2.5 border transition-colors">
          <p className="text-xs text-gray-600 dark:text-gray-400 font-semibold mb-1">Episode Steps</p>
          <p className="text-base font-bold text-cyan-600 dark:text-cyan-400">{metrics.episodeSteps}</p>
        </div>

        {/* Metric Card: Training Progress */}
        <div className="bg-white/50 backdrop-blur-md border border-white/80 dark:bg-gray-900/50 dark:border-gray-600/80 rounded-xl p-2.5 border transition-colors">
          <p className="text-xs text-gray-600 dark:text-gray-400 font-semibold mb-1">Progress</p>
          <p className="text-base font-bold text-green-600 dark:text-green-400">
            {metrics.trainingProgress}%
          </p>
        </div>

        {/* Metric Card: Convergence Rate */}
        <div className="bg-white/50 backdrop-blur-md border border-white/80 dark:bg-gray-900/50 dark:border-gray-600/80 rounded-xl p-2.5 border transition-colors">
          <p className="text-xs text-gray-600 dark:text-gray-400 font-semibold mb-1">Convergence</p>
          <p className="text-base font-bold text-purple-600 dark:text-purple-400">{metrics.convergenceRate}</p>
        </div>
      </div>
    </div>
  );
}
