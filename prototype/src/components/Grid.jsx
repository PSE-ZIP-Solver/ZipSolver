import { useRef, useEffect, useState } from 'react';
import { useTheme } from '../context/ThemeContext';

export default function Grid({
  gridSize,
  wayPoints,
  walls,
  solutions,
  currentSolutionIndex,
  isAnimating,
  currentStepIndex,
  editMode,
  onCellClick,
  onWallClick,
}) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [containerWidth, setContainerWidth] = useState(0);
  const { theme } = useTheme();

  // Measure container width on mount and resize
  useEffect(() => {
    const measureContainer = () => {
      if (containerRef.current) {
        const width = containerRef.current.offsetWidth;
        setContainerWidth(Math.max(300, width - 48)); // 48px for padding
      }
    };

    measureContainer();
    window.addEventListener('resize', measureContainer);
    return () => window.removeEventListener('resize', measureContainer);
  }, []);

  const gridPixels = Math.min(containerWidth, 600); // Max 600px
  const cellSize = gridPixels / gridSize;
  const [hoveredCell, setHoveredCell] = useState(null);

  // Draw solution path on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || gridPixels === 0) return;

    const ctx = canvas.getContext('2d');
    canvas.width = gridPixels;
    canvas.height = gridPixels;

    ctx.clearRect(0, 0, gridPixels, gridPixels);

    // Draw solution path if exists
    if (solutions.length > 0 && currentSolutionIndex < solutions.length) {
      const solution = solutions[currentSolutionIndex];
      const path = solution.path;
      const drawLimit = currentStepIndex + 1;

      ctx.lineWidth = Math.max(2, cellSize * 0.15);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      for (let i = 1; i < drawLimit; i++) {
        const [prevRow, prevCol] = path[i - 1];
        const [currRow, currCol] = path[i];

        ctx.beginPath();
        ctx.moveTo(
          prevCol * cellSize + cellSize / 2,
          prevRow * cellSize + cellSize / 2
        );
        ctx.lineTo(
          currCol * cellSize + cellSize / 2,
          currRow * cellSize + cellSize / 2
        );

        // Dynamic color gradient from orange to red
        const progress = i / path.length;
        const hue = 50 - progress * 40;
        const lightness = 65 - progress * 20;
        ctx.strokeStyle = `hsl(${hue}, 100%, ${lightness}%)`;
        ctx.stroke();
      }
    }
  }, [solutions, currentSolutionIndex, isAnimating, currentStepIndex, gridPixels, cellSize]);

  return (
    <div ref={containerRef} className="flex justify-center">
      <div
        className="relative rounded-xl overflow-hidden shadow-lg transition-colors duration-200"
        style={{
          width: gridPixels,
          height: gridPixels,
          backgroundColor: theme === 'dark' ? '#1a1a1a' : '#ffffff',
          border: `2px solid ${theme === 'dark' ? '#404040' : '#e5e5e5'}`,
        }}
      >
        {/* Canvas for drawing solution path */}
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            inset: 0,
            zIndex: 5,
            pointerEvents: 'none',
          }}
        />

        {/* Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
            gridTemplateRows: `repeat(${gridSize}, 1fr)`,
            width: '100%',
            height: '100%',
          }}
        >
          {Array.from({ length: gridSize * gridSize }).map((_, idx) => {
            const row = Math.floor(idx / gridSize);
            const col = idx % gridSize;
            const posKey = `${row},${col}`;
            const number = wayPoints[posKey];
            const hasRightWall = walls.v[posKey];
            const hasBottomWall = walls.h[posKey];
            const isHovered = hoveredCell === idx && editMode !== 'walls';

            return (
              <div
                key={idx}
                className="relative cursor-pointer transition-colors duration-150 flex items-center justify-center border"
                onClick={() => {
                  if (editMode === 'numbers') {
                    onCellClick(row, col);
                  }
                }}
                onMouseEnter={() => setHoveredCell(idx)}
                onMouseLeave={() => setHoveredCell(null)}
                style={{
                  position: 'relative',
                  width: cellSize,
                  height: cellSize,
                  borderColor: theme === 'dark' ? '#404040' : '#d1d5db',
                  borderWidth: '1px',
                  backgroundColor: isHovered
                    ? (theme === 'dark' ? '#92400e' : '#fef5f0')
                    : (theme === 'dark' ? '#111827' : '#ffffff'),
                  transition: 'background-color 0.15s ease-in-out',
                }}
              >
                {/* Number Ball */}
                {number !== undefined && (
                  <div
                    className="num-ball"
                    style={{
                      width: Math.round(cellSize * 0.58),
                      height: Math.round(cellSize * 0.58),
                      fontSize: Math.round(cellSize * 0.28),
                    }}
                  >
                    {number}
                  </div>
                )}

                {/* Wall Click Zones */}
                {editMode === 'walls' && col < gridSize - 1 && (
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      onWallClick('v', row, col);
                    }}
                    style={{
                      position: 'absolute',
                      right: -8,
                      top: 0,
                      bottom: 0,
                      width: 16,
                      zIndex: 100,
                      cursor: 'pointer',
                      background: 'linear-gradient(to right, transparent, rgba(249, 115, 22, 0.35), transparent)',
                      transition: 'background 0.2s',
                    }}
                  />
                )}
                {editMode === 'walls' && row < gridSize - 1 && (
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      onWallClick('h', row, col);
                    }}
                    style={{
                      position: 'absolute',
                      bottom: -8,
                      left: 0,
                      right: 0,
                      height: 16,
                      zIndex: 100,
                      cursor: 'pointer',
                      background: 'linear-gradient(to bottom, transparent, rgba(249, 115, 22, 0.35), transparent)',
                      transition: 'background 0.2s',
                    }}
                  />
                )}

                {/* Wall Visuals */}
                {hasRightWall && (
                  <div
                    className="absolute top-0 bottom-0 w-1 bg-gray-950 dark:bg-gray-100 z-50 -right-0.5"
                    style={{ boxShadow: '0 0 10px rgba(249, 115, 22, 0.4)' }}
                  />
                )}
                {hasBottomWall && (
                  <div
                    className="absolute left-0 right-0 h-1 bg-gray-950 dark:bg-gray-100 z-50 -bottom-0.5"
                    style={{ boxShadow: '0 0 10px rgba(249, 115, 22, 0.4)' }}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
