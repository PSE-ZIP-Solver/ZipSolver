/**
 * JSON Exporter using unified board representation format
 * Format: boardSize, waypoints (array of [row, col]), walls (array of {neighborA, neighborB})
 */

export function exportGridToJSON(boardSize, wayPoints, walls, solutionPath = null) {
  // Convert wayPoints object to array format sorted by number
  const sortedWaypoints = [];
  const entries = Object.entries(wayPoints).map(([pos, number]) => ({
    pos,
    number,
  }));
  entries.sort((a, b) => a.number - b.number);
  
  for (const { pos } of entries) {
    const [r, c] = pos.split(',').map(Number);
    sortedWaypoints.push([r, c]);
  }

  // Convert walls from h/v format to neighborA/neighborB format
  const wallsArray = [];

  if (walls && walls.h) {
    for (const pos of Object.keys(walls.h)) {
      const [r, c] = pos.split(',').map(Number);
      // Horizontal wall: between [r, c] and [r+1, c]
      wallsArray.push({
        neighborA: [r, c],
        neighborB: [r + 1, c],
      });
    }
  }

  if (walls && walls.v) {
    for (const pos of Object.keys(walls.v)) {
      const [r, c] = pos.split(',').map(Number);
      // Vertical wall: between [r, c] and [r, c+1]
      wallsArray.push({
        neighborA: [r, c],
        neighborB: [r, c + 1],
      });
    }
  }

  const exportData = {
    boardSize,
    waypoints: sortedWaypoints,
    walls: wallsArray,
  };

  // Add solution path if provided
  if (solutionPath && solutionPath.length > 0) {
    exportData.solutionPath = solutionPath;
  }

  return exportData;
}

export function downloadJSON(data, filename = 'zip_puzzle.json') {
  const json = JSON.stringify(data, null, 1);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
