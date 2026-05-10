/**
 * ZipSolver Engine - DFS-based puzzle solver
 * Supports any grid size, walls, and numbered waypoints
 */
class ZipSolver {
  constructor(gridSize, numbers, walls) {
    this.gridSize = gridSize;
    this.totalCells = gridSize * gridSize;
    this.numbers = numbers; // { "r,c": number }
    this.walls = walls; // { h: {...}, v: {...} }
    this.numberPositions = {};
    this.allSolutions = [];
    this.visited = new Set();

    // Build number positions map
    for (const [pos, num] of Object.entries(numbers)) {
      const [r, c] = pos.split(',').map(Number);
      this.numberPositions[num] = [r, c];
    }
  }

  isValid(r, c) {
    return r >= 0 && r < this.gridSize && c >= 0 && c < this.gridSize;
  }

  hasWallBetween(r1, c1, r2, c2) {
    if (!this.walls) return false;

    if (r1 === r2) {
      // Horizontal move
      const cmin = Math.min(c1, c2);
      if (this.walls.v[`${r1},${cmin}`]) return true;
    } else {
      // Vertical move
      const rmin = Math.min(r1, r2);
      if (this.walls.h[`${rmin},${c1}`]) return true;
    }
    return false;
  }

  getValidNeighbors(r, c) {
    const neighbors = [];
    const directions = [
      [0, 1],   // right
      [0, -1],  // left
      [1, 0],   // down
      [-1, 0],  // up
    ];

    for (const [dr, dc] of directions) {
      const nr = r + dr;
      const nc = c + dc;
      const key = `${nr},${nc}`;

      if (this.isValid(nr, nc) && !this.visited.has(key)) {
        if (!this.hasWallBetween(r, c, nr, nc)) {
          neighbors.push([nr, nc]);
        }
      }
    }
    return neighbors;
  }

  detectIsolated(testVisited) {
    const unvisited = [];
    for (let r = 0; r < this.gridSize; r++) {
      for (let c = 0; c < this.gridSize; c++) {
        if (!testVisited.has(`${r},${c}`)) {
          unvisited.push([r, c]);
        }
      }
    }

    if (!unvisited.length) return false;

    const start = unvisited[0];
    const q = [start];
    const seen = new Set([`${start[0]},${start[1]}`]);

    while (q.length > 0) {
      const [r, c] = q.shift();
      for (const [dr, dc] of [[0, 1], [0, -1], [1, 0], [-1, 0]]) {
        const nr = r + dr;
        const nc = c + dc;
        const key = `${nr},${nc}`;

        if (
          this.isValid(nr, nc) &&
          !testVisited.has(key) &&
          !seen.has(key)
        ) {
          if (!this.hasWallBetween(r, c, nr, nc)) {
            seen.add(key);
            q.push([nr, nc]);
          }
        }
      }
    }

    return seen.size < unvisited.length;
  }

  dfs(r, c, nextNum, path, startTime) {
    if (this.allSolutions.length >= 50) return;

    const key = `${r},${c}`;
    this.visited.add(key);
    path.push([r, c]);

    const maxNum = Math.max(...Object.values(this.numbers));

    if (path.length === this.totalCells) {
      if (this.numbers[key] === maxNum) {
        const now = performance.now();
        const timeFound = (now - this.lastTime).toFixed(2);
        this.lastTime = now;
        this.allSolutions.push({
          path: [...path],
          time: timeFound,
        });
      }
      this.visited.delete(key);
      path.pop();
      return;
    }

    let neighbors = this.getValidNeighbors(r, c);

    // Heuristic: sort by distance to next number
    const targetPos = this.numberPositions[nextNum];
    if (targetPos) {
      neighbors.sort(
        (a, b) =>
          Math.abs(a[0] - targetPos[0]) +
          Math.abs(a[1] - targetPos[1]) -
          (Math.abs(b[0] - targetPos[0]) + Math.abs(b[1] - targetPos[1]))
      );
    }

    for (const [nr, nc] of neighbors) {
      let next = nextNum;
      const nNum = this.numbers[`${nr},${nc}`];

      if (nNum) {
        if (nNum === nextNum) {
          if (nNum === maxNum && path.length !== this.totalCells - 1) {
            continue;
          }
          next++;
        } else if (nNum > nextNum) {
          continue;
        }
      }

      // Prune isolated cells
      if (this.detectIsolated(new Set([...this.visited, `${nr},${nc}`]))) {
        continue;
      }

      this.dfs(nr, nc, next, path, startTime);
    }

    this.visited.delete(key);
    path.pop();
  }

  solve() {
    const startPos = this.numberPositions[1];
    if (!startPos) return [];

    const t0 = performance.now();
    this.allSolutions = [];
    this.visited = new Set();
    this.lastTime = t0;

    this.dfs(startPos[0], startPos[1], 2, [], t0);

    return this.allSolutions;
  }
}

export default ZipSolver;
