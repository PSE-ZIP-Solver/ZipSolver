export default function Controls({
  gridSize,
  onGridSizeChange,
  onSolve,
  onReset,
  onExport,
  statusType,
  statusMessage,
  solutions,
  currentSolutionIndex,
  onPrevSolution,
  onNextSolution,
  editMode,
  onEditModeChange,
  solverRunning,
  displayTime,
}) {
  return (
    <div className="glass rounded-2xl p-4 w-full shadow-md">
      {/* Edit Mode Tabs */}
      <div className="flex gap-3 mb-4">
        <button
          className={`flex-1 btn-ghost py-2 px-2 rounded-2xl flex items-center justify-center gap-2 text-sm ${
            editMode === 'numbers' ? 'status-ok' : ''
          }`}
          onClick={() => onEditModeChange('numbers')}
        >
          <span>#</span>
          NUMBERS
        </button>
        <button
          className={`flex-1 btn-ghost py-2 px-2 rounded-2xl flex items-center justify-center gap-2 text-sm ${
            editMode === 'walls' ? 'status-ok' : ''
          }`}
          onClick={() => onEditModeChange('walls')}
        >
          <span>━</span>
          WALLS
        </button>
      </div>

      {/* Grid Size Slider */}
      <div className="mb-4">
        <div className="flex justify-between mb-2">
          <label className="text-xs font-bold text-gray-700 uppercase">
            Grid Size
          </label>
          <span className="text-xs font-bold text-orange-600">{gridSize}×{gridSize}</span>
        </div>
        <input
          type="range"
          min="3"
          max="9"
          value={gridSize}
          onChange={(e) => onGridSizeChange(parseInt(e.target.value))}
          className="w-full cursor-pointer"
          disabled={solverRunning}
        />
      </div>

      {/* Status Message */}
      <div className={`status-${statusType} rounded-3xl p-4 mb-4 border`}>
        <p className="text-xs font-bold">{statusMessage}</p>
        {solutions.length > 1 && (
          <div className="flex items-center justify-center gap-3 mt-3">
            <button
              className="btn-ghost w-9 h-9 rounded-xl flex items-center justify-center text-sm"
              onClick={onPrevSolution}
              disabled={solverRunning}
            >
              ←
            </button>
            <span className="text-xs font-bold">
              {currentSolutionIndex + 1} / {solutions.length}
            </span>
            <button
              className="btn-ghost w-9 h-9 rounded-xl flex items-center justify-center text-sm"
              onClick={onNextSolution}
              disabled={solverRunning}
            >
              →
            </button>
          </div>
        )}
      </div>

      {/* Time Display */}
      <div className="glass rounded-3xl px-3.5 py-3 mb-4 border flex justify-center items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-red-600"></div>
        <span className="text-sm font-bold text-red-600 tracking-wide">
          {displayTime}ms
        </span>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-2">
        <button
          className="btn-primary py-2.5 px-4 rounded-2xl font-bold text-xs flex items-center justify-center gap-2 w-full disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={onSolve}
          disabled={solverRunning}
        >
          <span>⚡</span>
          SOLVE ALL
        </button>
        
        {solutions.length > 0 && (
          <button
            className="btn-ghost py-2.5 px-4 rounded-2xl font-bold text-xs flex items-center justify-center gap-2 w-full hover:text-orange-600"
            onClick={onExport}
            disabled={solverRunning}
          >
            <span>📥</span>
            EXPORT JSON
          </button>
        )}

        <button
          className="btn-ghost py-2.5 px-4 rounded-2xl font-bold text-xs flex items-center justify-center gap-2 w-full hover:text-orange-600"
          onClick={onReset}
          disabled={solverRunning}
        >
          <span>🔄</span>
          RESET
        </button>
      </div>
    </div>
  );
}
