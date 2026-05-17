import { useState, useEffect } from 'react';
import Grid from './Grid';
import Controls from './Controls';
import MetricsPanel from './MetricsPanel';
import ZipSolver from '../utils/zipSolver';
import { exportGridToJSON, downloadJSON } from '../utils/jsonExporter';

export default function GridBuilder() {
  // State
  const [gridSize, setGridSize] = useState(6);
  const [wayPoints, setWayPoints] = useState({});
  const [walls, setWalls] = useState({ h: {}, v: {} });
  const [editMode, setEditMode] = useState('numbers');
  const [solutions, setSolutions] = useState([]);
  const [currentSolutionIndex, setCurrentSolutionIndex] = useState(0);
  const [solverRunning, setSolverRunning] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isAutoPlayPaused, setIsAutoPlayPaused] = useState(false);
  const [displayTime, setDisplayTime] = useState(0);
  const [statusType, setStatusType] = useState('ok');
  const [statusMessage, setStatusMessage] = useState('Click cells to add numbers');

  // Handle cell click (add/remove waypoint)
  const handleCellClick = (row, col) => {
    if (solverRunning) return;

    const key = `${row},${col}`;
    let newWayPoints;

    if (wayPoints[key]) {
      // Remove waypoint
      newWayPoints = { ...wayPoints };
      delete newWayPoints[key];

      // Renumber remaining points
      const sortedByNumber = Object.entries(newWayPoints).sort(
        ([, a], [, b]) => a - b
      );
      const renumbered = {};
      sortedByNumber.forEach(([pos, _], idx) => {
        renumbered[pos] = idx + 1;
      });
      newWayPoints = renumbered;
    } else {
      // Add waypoint
      const nextNumber = Object.keys(wayPoints).length + 1;
      newWayPoints = { ...wayPoints, [key]: nextNumber };
    }

    setWayPoints(newWayPoints);
    setSolutions([]);
    updateStatus(Object.keys(newWayPoints).length);
  };

  // Handle wall click
  const handleWallClick = (type, row, col) => {
    if (solverRunning) return;

    const key = `${row},${col}`;
    setWalls((prev) => {
      const newWalls = { ...prev, [type]: { ...prev[type] } };
      if (newWalls[type][key]) {
        delete newWalls[type][key];
      } else {
        newWalls[type][key] = true;
      }
      return newWalls;
    });
    setSolutions([]);
  };

  // Update status based on waypoint count
  const updateStatus = (count) => {
    if (count === 0) {
      setStatusMessage('Click cells to add numbers');
      setStatusType('ok');
    } else if (count === 1) {
      setStatusMessage('Add at least 2 numbers');
      setStatusType('ok');
    } else {
      setStatusMessage('Ready to solve!');
      setStatusType('ok');
    }
  };

  // Handle solve
  const handleSolve = () => {
    const waypointCount = Object.keys(wayPoints).length;
    if (waypointCount < 2) {
      setStatusType('err');
      setStatusMessage('Add 2+ numbers first');
      return;
    }

    setSolverRunning(true);
    setCurrentStepIndex(0);
    setIsAutoPlayPaused(false);
    setDisplayTime(0);

    // Run solver
    const solver = new ZipSolver(gridSize, wayPoints, walls);
    const results = solver.solve();

    if (results.length > 0) {
      setSolutions(results);
      setCurrentSolutionIndex(0);
      setStatusType('done');
      const limitMsg = solver.hitIterationLimit ? ' (limit reached)' : '';
      setStatusMessage(
        `${results.length >= 50 ? '50+' : results.length} Solution${
          results.length === 1 ? '' : 's'
        } found!${limitMsg}`
      );
    } else {
      setSolverRunning(false);
      setStatusType('err');
      const limitMsg = solver.hitIterationLimit ? ' (iteration limit reached)' : '';
      setStatusMessage(`No solution found${limitMsg}`);
      setSolutions([]);
    }
  };

  // Handle reset
  const handleReset = () => {
    setWayPoints({});
    setWalls({ h: {}, v: {} });
    setSolutions([]);
    setCurrentSolutionIndex(0);
    setSolverRunning(false);
    setCurrentStepIndex(0);
    setIsAutoPlayPaused(false);
    setDisplayTime(0);
    setStatusType('ok');
    setStatusMessage('Click cells to add numbers');
  };

  // Handle export
  const handleExport = () => {
    if (solutions.length === 0) return;

    const jsonData = exportGridToJSON(gridSize, wayPoints, walls);
    const timestamp = new Date().toISOString().slice(0, 10);
    downloadJSON(jsonData, `zip_puzzle_${gridSize}x${gridSize}_${timestamp}.json`);

    setStatusType('done');
    setStatusMessage('JSON exported successfully!');
  };

  // Animation loop
  useEffect(() => {
    if (!solverRunning || solutions.length === 0 || isAutoPlayPaused) return;

    const currentSolution = solutions[currentSolutionIndex];
    const pathLength = currentSolution.path.length;
    const totalTime = parseFloat(currentSolution.time);

    const interval = setInterval(() => {
      setCurrentStepIndex((idx) => {
        if (idx >= pathLength - 1) {
          setSolverRunning(false);
          setDisplayTime(totalTime);
          clearInterval(interval);
          return idx;
        }

        const progress = (idx + 1) / pathLength;
        setDisplayTime(parseFloat((totalTime * progress).toFixed(2)));
        return idx + 1;
      });
    }, 25); // Smooth animation

    return () => clearInterval(interval);
  }, [solverRunning, solutions, currentSolutionIndex, isAutoPlayPaused]);

  // Handle grid size change
  const handleGridSizeChange = (size) => {
    setGridSize(size);
    setWayPoints({});
    setWalls({ h: {}, v: {} });
    setSolutions([]);
    setCurrentStepIndex(0);
    setIsAutoPlayPaused(false);
    setDisplayTime(0);
    setStatusType('ok');
    setStatusMessage('Click cells to add numbers');
  };

  // Handle solution navigation
  const handlePrevSolution = () => {
    setCurrentSolutionIndex((idx) =>
      idx === 0 ? solutions.length - 1 : idx - 1
    );
    setCurrentStepIndex(0);
    setIsAutoPlayPaused(false);
    setSolverRunning(true);
  };

  const handleNextSolution = () => {
    setCurrentSolutionIndex((idx) =>
      idx === solutions.length - 1 ? 0 : idx + 1
    );
    setCurrentStepIndex(0);
    setIsAutoPlayPaused(false);
    setSolverRunning(true);
  };

  // Handle step navigation
  const handlePreviousStep = () => {
    setCurrentStepIndex((idx) => Math.max(0, idx - 1));
    setIsAutoPlayPaused(true);
    setSolverRunning(false);
  };

  const handleNextStep = () => {
    if (solutions.length === 0) return;
    const currentSolution = solutions[currentSolutionIndex];
    const pathLength = currentSolution.path.length;
    setCurrentStepIndex((idx) => Math.min(pathLength - 1, idx + 1));
    setIsAutoPlayPaused(true);
    setSolverRunning(false);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (solutions.length === 0) return;
      
      if (e.key === 'ArrowLeft') {
        handlePreviousStep();
      } else if (e.key === 'ArrowRight') {
        handleNextStep();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [solutions, currentSolutionIndex]);

  return (
    <div className="max-w-7xl mx-auto px-6 py-4 w-full">
      {/* Responsive Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6">
        {/* Left Column: Grid */}
        <div className="min-w-0">
          <Grid
            gridSize={gridSize}
            wayPoints={wayPoints}
            walls={walls}
            solutions={solutions}
            currentSolutionIndex={currentSolutionIndex}
            isAnimating={solverRunning}
            currentStepIndex={currentStepIndex}
            editMode={editMode}
            onCellClick={handleCellClick}
            onWallClick={handleWallClick}
          />
          
          {/* Step Navigation Buttons */}
          {solutions.length > 0 && (
            <div className="mt-4 flex justify-center gap-4">
              <button
                onClick={handlePreviousStep}
                disabled={currentStepIndex === 0}
                className="px-4 py-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed bg-orange-600 hover:bg-orange-700 text-white dark:bg-orange-600 dark:hover:bg-orange-700 dark:text-white disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:text-gray-500 dark:disabled:text-gray-400"
              >
                ◄ Previous
              </button>
              <div className="flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg font-semibold text-gray-900 dark:text-gray-100 transition-colors duration-200">
                Step {currentStepIndex + 1} / {solutions[currentSolutionIndex]?.path.length || 0}
              </div>
              <button
                onClick={handleNextStep}
                disabled={currentStepIndex === (solutions[currentSolutionIndex]?.path.length - 1 || 0)}
                className="px-4 py-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed bg-orange-600 hover:bg-orange-700 text-white dark:bg-orange-600 dark:hover:bg-orange-700 dark:text-white disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:text-gray-500 dark:disabled:text-gray-400"
              >
                Next ►
              </button>
            </div>
          )}
        </div>

        {/* Right Column: Controls & Metrics */}
        <div className="space-y-4">
          <Controls
            gridSize={gridSize}
            onGridSizeChange={handleGridSizeChange}
            onSolve={handleSolve}
            onReset={handleReset}
            onExport={handleExport}
            statusType={statusType}
            statusMessage={statusMessage}
            solutions={solutions}
            currentSolutionIndex={currentSolutionIndex}
            onPrevSolution={handlePrevSolution}
            onNextSolution={handleNextSolution}
            editMode={editMode}
            onEditModeChange={setEditMode}
            solverRunning={solverRunning}
            displayTime={displayTime}
          />

          <MetricsPanel
            solutions={solutions}
            currentSolutionIndex={currentSolutionIndex}
          />
        </div>
      </div>
    </div>
  );
}
