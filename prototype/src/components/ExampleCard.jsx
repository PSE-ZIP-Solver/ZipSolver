import { useTheme } from '../context/ThemeContext';

export default function ExampleCard({ example, onSelect }) {
  const { theme } = useTheme();

  // Color scheme based on theme
  const colors = {
    light: {
      bg: '#ffffff',
      border: '#e5e7eb',
      grid: '#f3f4f6',
      waypoint: '#f97316',
      waypointBorder: '#ea580c',
      wall: '#374151',
      text: '#111827',
    },
    dark: {
      bg: '#1f2937',
      border: '#4b5563',
      grid: '#111827',
      waypoint: '#ea580c',
      waypointBorder: '#dc2626',
      wall: '#9ca3af',
      text: '#f3f4f6',
    },
  };

  const color = colors[theme];
  const cellSize = 20;
  const padding = 4;
  const wallThickness = 2;

  // Calculate SVG dimensions
  const svgSize = example.boardSize * cellSize + padding * 2;

  // Helper to check if wall exists between two cells
  const hasWall = (row1, col1, row2, col2) => {
    return example.walls.some(
      (wall) =>
        (wall.neighborA[0] === row1 &&
          wall.neighborA[1] === col1 &&
          wall.neighborB[0] === row2 &&
          wall.neighborB[1] === col2) ||
        (wall.neighborA[0] === row2 &&
          wall.neighborA[1] === col2 &&
          wall.neighborB[0] === row1 &&
          wall.neighborB[1] === col1)
    );
  };

  // Render grid cells
  const cells = [];
  for (let row = 0; row < example.boardSize; row++) {
    for (let col = 0; col < example.boardSize; col++) {
      const x = col * cellSize + padding;
      const y = row * cellSize + padding;

      cells.push(
        <rect
          key={`cell-${row}-${col}`}
          x={x}
          y={y}
          width={cellSize}
          height={cellSize}
          fill={color.grid}
          stroke={color.border}
          strokeWidth="0.5"
        />
      );
    }
  }

  // Render walls between cells
  const walls = [];
  for (let row = 0; row < example.boardSize; row++) {
    for (let col = 0; col < example.boardSize; col++) {
      const x = col * cellSize + padding;
      const y = row * cellSize + padding;

      // Check for wall to the right
      if (col < example.boardSize - 1 && hasWall(row, col, row, col + 1)) {
        walls.push(
          <line
            key={`wall-v-${row}-${col}`}
            x1={x + cellSize}
            y1={y}
            x2={x + cellSize}
            y2={y + cellSize}
            stroke={color.wall}
            strokeWidth={wallThickness}
          />
        );
      }

      // Check for wall below
      if (row < example.boardSize - 1 && hasWall(row, col, row + 1, col)) {
        walls.push(
          <line
            key={`wall-h-${row}-${col}`}
            x1={x}
            y1={y + cellSize}
            x2={x + cellSize}
            y2={y + cellSize}
            stroke={color.wall}
            strokeWidth={wallThickness}
          />
        );
      }
    }
  }

  // Render waypoints
  const waypoints = example.waypoints.map((waypoint, index) => {
    const [row, col] = waypoint;
    const x = col * cellSize + padding + cellSize / 2;
    const y = row * cellSize + padding + cellSize / 2;
    const radius = cellSize / 3;

    return (
      <g key={`waypoint-${index}`}>
        <circle
          cx={x}
          cy={y}
          r={radius}
          fill={color.waypoint}
          stroke={color.waypointBorder}
          strokeWidth="1"
        />
        <text
          x={x}
          y={y}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="10"
          fontWeight="bold"
          fill={color.bg}
        >
          {index + 1}
        </text>
      </g>
    );
  });

  return (
    <button
      onClick={() => onSelect(example)}
      className="flex flex-col items-center gap-2 p-3 rounded-lg border-2 border-gray-300 dark:border-gray-600 hover:border-orange-500 dark:hover:border-orange-400 hover:shadow-lg dark:hover:shadow-orange-900/30 transition-all duration-200 cursor-pointer bg-white dark:bg-gray-800 group"
      title={`Load ${example.name}`}
    >
      {/* SVG Miniature */}
      <div className="bg-gray-50 dark:bg-gray-900 rounded p-1">
        <svg
          width={svgSize}
          height={svgSize}
          viewBox={`0 0 ${svgSize} ${svgSize}`}
          className="group-hover:scale-110 transition-transform duration-200"
        >
          {cells}
          {walls}
          {waypoints}
        </svg>
      </div>

      {/* Label */}
      <div className="text-center">
        <p className="text-xs font-semibold text-gray-700 dark:text-gray-300">
          {example.name}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {example.boardSize}×{example.boardSize}
        </p>
      </div>
    </button>
  );
}
