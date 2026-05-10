/**
 * JSON Exporter for backend integration
 */

export function exportGridToJSON(gridSize, wayPoints, walls) {
  // Convert wayPoints object to array format
  const waypointsArray = [];
  for (const [pos, number] of Object.entries(wayPoints)) {
    const [r, c] = pos.split(',').map(Number);
    waypointsArray.push({
      position: [r, c],
      number: number,
    });
  }

  // Convert walls to array format
  const horizontalWalls = [];
  const verticalWalls = [];

  if (walls && walls.h) {
    for (const pos of Object.keys(walls.h)) {
      const [r, c] = pos.split(',').map(Number);
      horizontalWalls.push({ position: [r, c] });
    }
  }

  if (walls && walls.v) {
    for (const pos of Object.keys(walls.v)) {
      const [r, c] = pos.split(',').map(Number);
      verticalWalls.push({ position: [r, c] });
    }
  }

  return {
    grid_size: gridSize,
    waypoints: waypointsArray,
    walls: {
      horizontal: horizontalWalls,
      vertical: verticalWalls,
    },
    metadata: {
      created_at: new Date().toISOString(),
      has_solution: true,
      solvable: true,
    },
  };
}

export function downloadJSON(data, filename = 'zip_puzzle.json') {
  const json = JSON.stringify(data, null, 2);
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
