import {
	useEffect,
	useMemo,
	useRef,
	useState
} from "react";

import {
	type BoardConfig,
	type Position,
	type Wall
} from "../types/board";

import {
	type SolutionPath
} from "../types/solver";

import {
	type EditMode
} from "../types/grid";

interface GridProps {
	board: BoardConfig;
	solution: SolutionPath | null;
	editMode: EditMode;
	playerPath: Position[];
	activePosition: Position | null;
	hintPosition: Position | null;
	hintPath: SolutionPath | null;
	hintPathVersion?: number;
	isPlayMode: boolean;
	onCellClick: (position: Position) => void;
	onWallClick: (wall: Wall) => void;
	pathShakeVersion?: number;
}

const MAX_GRID_PIXELS = 600;
const MIN_GRID_PIXELS = 300;
const GRID_GAP_PX = 1;
const WALL_THICKNESS_PX = 6;

function readThemeColor(variableName: string, fallback: string) {
	if (typeof window === "undefined") {
		return fallback;
	}

	const value = getComputedStyle(document.documentElement)
		.getPropertyValue(variableName)
		.trim();

	return value || fallback;
}

function isDarkThemeActive() {
	if (typeof document === "undefined") {
		return false;
	}

	return document.documentElement.classList.contains("dark");
}

function isBefore(a: Position, b: Position) {
	if (a[0] !== b[0]) return a[0] < b[0];
	return a[1] < b[1];
}

function getWallKey(a: Position, b: Position) {
	const [first, second] = isBefore(a, b) ? [a, b] : [b, a];
	return `${first[0]},${first[1]}|${second[0]},${second[1]}`;
}

function createWall(a: Position, b: Position): Wall {
	return {
		neighborA: a,
		neighborB: b
	};
}

export default function Grid({
	board,
	solution,
	editMode,
	playerPath,
	activePosition,
	hintPosition,
	hintPath,
	hintPathVersion = 0,
	isPlayMode,
	onCellClick,
	onWallClick,
	pathShakeVersion = 0
}: GridProps) {

	const canvasRef = useRef<HTMLCanvasElement | null>(null);
	const containerRef = useRef<HTMLDivElement | null>(null);
	const hintPathCanvasRef = useRef<HTMLCanvasElement | null>(null);
	const playerPathCanvasRef = useRef<HTMLCanvasElement | null>(null);

	const [containerWidth, setContainerWidth] = useState(0);
	const [hoveredCell, setHoveredCell] = useState<number | null>(null);
	const [isPointerDown, setIsPointerDown] = useState(false);

	useEffect(() => {
		const element = containerRef.current;
		if (!element) return;

		const measure = () => {
			const width = element.offsetWidth;
			setContainerWidth(
				Math.max(MIN_GRID_PIXELS, width - 48)
			);
		};

		measure();

		if (typeof ResizeObserver !== "undefined") {
			const observer = new ResizeObserver(measure);
			observer.observe(element);
			return () => observer.disconnect();
		}

		window.addEventListener("resize", measure);
		return () => window.removeEventListener("resize", measure);
	}, []);

	const gridPixels = Math.min(containerWidth, MAX_GRID_PIXELS);
	const cellSize = useMemo(() => {
		if (gridPixels <= 0) return 0;
		return (gridPixels - GRID_GAP_PX * (board.boardSize - 1)) / board.boardSize;
	}, [board.boardSize, gridPixels]);

	const stride = cellSize + GRID_GAP_PX;

	const waypointIndexByCell = useMemo(() => {
		const map = new Map<string, number>();
		board.waypoints.forEach((position, index) => {
			map.set(`${position[0]},${position[1]}`, index);
		});
		return map;
	}, [board.waypoints]);

	const activeCellKey = activePosition ? `${activePosition[0]},${activePosition[1]}` : null;
	const hintCellKey = hintPosition ? `${hintPosition[0]},${hintPosition[1]}` : null;
	const startPosition = board.waypoints[0] ?? null;
	const pathToRender = startPosition && playerPath.length > 0
		? (playerPath[0] && playerPath[0][0] === startPosition[0] && playerPath[0][1] === startPosition[1]
			? playerPath
			: [startPosition, ...playerPath])
		: playerPath;
	const solutionPathToRender = useMemo(() => {
		if (!solution || solution.length === 0) {
			return [];
		}

		if (!startPosition) {
			return solution;
		}

		const [firstPosition] = solution;
		if (firstPosition && firstPosition[0] === startPosition[0] && firstPosition[1] === startPosition[1]) {
			return solution;
		}

		return [startPosition, ...solution];
	}, [solution, startPosition]);

	const wallSet = useMemo(() => {
		const set = new Set<string>();
		board.walls.forEach((wall) => {
			set.add(getWallKey(wall.neighborA, wall.neighborB));
		});
		return set;
	}, [board.walls]);

	useEffect(() => {
		const canvas = canvasRef.current;
		if (!canvas || !gridPixels) return;

		const ctx = canvas.getContext("2d");
		if (!ctx) return;

		const dpr = window.devicePixelRatio || 1;
		canvas.width = Math.round(gridPixels * dpr);
		canvas.height = Math.round(gridPixels * dpr);
		canvas.style.width = `${gridPixels}px`;
		canvas.style.height = `${gridPixels}px`;
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
		ctx.clearRect(0, 0, gridPixels, gridPixels);

		if (!solution || solutionPathToRender.length < 2) {
			return;
		}

		const duration = 650;
		let raf = 0;
		const startedAt = performance.now();
		const solutionGlow = readThemeColor("--color-path-highlight-glow", "rgba(249, 115, 22, 0.28)");

		const draw = (now: number) => {
			const animationProgress = Math.min(1, (now - startedAt) / duration);
			const visibleSegments = animationProgress * (solutionPathToRender.length - 1);
			const darkTheme = isDarkThemeActive();

			ctx.clearRect(0, 0, gridPixels, gridPixels);

			ctx.lineWidth = Math.max(2, cellSize * 0.16);
			ctx.lineCap = "round";
			ctx.lineJoin = "round";
			ctx.shadowColor = solutionGlow;
			ctx.shadowBlur = Math.max(4, cellSize * 0.12);

			for (let i = 1; i < solutionPathToRender.length; i += 1) {
				if (i > Math.ceil(visibleSegments)) break;

				const previous = solutionPathToRender[i - 1];
				const current = solutionPathToRender[i];
				const segmentProgress = Math.max(
					0,
					Math.min(1, visibleSegments - (i - 1))
				);

				const prevX = previous[1] * stride + cellSize / 2;
				const prevY = previous[0] * stride + cellSize / 2;
				const currX = current[1] * stride + cellSize / 2;
				const currY = current[0] * stride + cellSize / 2;

				const currentX = prevX + (currX - prevX) * segmentProgress;
				const currentY = prevY + (currY - prevY) * segmentProgress;

				const tintProgress = i / solutionPathToRender.length;
				const hue = darkTheme
					? 34 - tintProgress * 10
					: 48 - tintProgress * 36;
				const saturation = darkTheme ? 64 : 100;
				const lightness = darkTheme
					? 62 - tintProgress * 8
					: 66 - tintProgress * 12;

				ctx.beginPath();
				ctx.moveTo(prevX, prevY);
				ctx.lineTo(currentX, currentY);
				ctx.strokeStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
				ctx.stroke();
			}

			if (animationProgress < 1) {
				raf = requestAnimationFrame(draw);
			}
		};

		raf = requestAnimationFrame(draw);

		return () => cancelAnimationFrame(raf);
	}, [cellSize, gridPixels, solutionPathToRender, stride]);

	useEffect(() => {
		const canvas = hintPathCanvasRef.current;
		if (!canvas || !gridPixels) return;

		const ctx = canvas.getContext("2d");
		if (!ctx) return;

		const dpr = window.devicePixelRatio || 1;
		canvas.width = Math.round(gridPixels * dpr);
		canvas.height = Math.round(gridPixels * dpr);
		canvas.style.width = `${gridPixels}px`;
		canvas.style.height = `${gridPixels}px`;
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
		ctx.clearRect(0, 0, gridPixels, gridPixels);

		if (!hintPath || hintPath.length < 2) {
			return;
		}

		const duration = 650;
		let raf = 0;
		const startedAt = performance.now();
		const hintGlow = readThemeColor("--color-hint-border", "rgba(52, 211, 153, 0.30)");

		const draw = (now: number) => {
			const animationProgress = Math.min(1, (now - startedAt) / duration);
			const visibleSegments = animationProgress * (hintPath.length - 1);
			const darkTheme = isDarkThemeActive();

			ctx.clearRect(0, 0, gridPixels, gridPixels);

			ctx.lineWidth = Math.max(2, cellSize * 0.15);
			ctx.lineCap = "round";
			ctx.lineJoin = "round";
			ctx.shadowColor = hintGlow;
			ctx.shadowBlur = Math.max(4, cellSize * 0.12);

			for (let i = 1; i < hintPath.length; i += 1) {
				if (i > Math.ceil(visibleSegments)) break;

				const previous = hintPath[i - 1];
				const current = hintPath[i];
				const segmentProgress = Math.max(
					0,
					Math.min(1, visibleSegments - (i - 1))
				);

				const prevX = previous[1] * stride + cellSize / 2;
				const prevY = previous[0] * stride + cellSize / 2;
				const currX = current[1] * stride + cellSize / 2;
				const currY = current[0] * stride + cellSize / 2;

				const currentX = prevX + (currX - prevX) * segmentProgress;
				const currentY = prevY + (currY - prevY) * segmentProgress;

				const tintProgress = i / hintPath.length;
				const hue = darkTheme
					? 154 - tintProgress * 12
					: 156 - tintProgress * 16;
				const saturation = darkTheme ? 48 : 78;
				const lightness = darkTheme
					? 56 - tintProgress * 8
					: 58 - tintProgress * 8;

				ctx.beginPath();
				ctx.moveTo(prevX, prevY);
				ctx.lineTo(currentX, currentY);
				ctx.strokeStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
				ctx.stroke();
			}

			if (animationProgress < 1) {
				raf = requestAnimationFrame(draw);
			}
		};

		raf = requestAnimationFrame(draw);

		return () => cancelAnimationFrame(raf);
	}, [cellSize, gridPixels, hintPath, hintPathVersion, stride]);

	useEffect(() => {
		const canvas = playerPathCanvasRef.current;
		if (!canvas || !gridPixels) return;

		const ctx = canvas.getContext("2d");
		if (!ctx) return;

		const dpr = window.devicePixelRatio || 1;
		canvas.width = Math.round(gridPixels * dpr);
		canvas.height = Math.round(gridPixels * dpr);
		canvas.style.width = `${gridPixels}px`;
		canvas.style.height = `${gridPixels}px`;
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
		ctx.clearRect(0, 0, gridPixels, gridPixels);

		if (pathToRender.length < 2) return;

		const playerPathColor = readThemeColor("--color-path-player", "rgba(234, 106, 26, 0.95)");
		const playerPathGlow = readThemeColor("--color-path-player-glow", "rgba(234, 106, 26, 0.25)");

		ctx.lineWidth = Math.max(2.5, cellSize * 0.18);
		ctx.lineCap = "round";
		ctx.lineJoin = "round";
		ctx.strokeStyle = playerPathColor;
		ctx.shadowColor = playerPathGlow;
		ctx.shadowBlur = Math.max(6, cellSize * 0.12);

		ctx.beginPath();
		pathToRender.forEach((position, index) => {
			const x = position[1] * stride + cellSize / 2;
			const y = position[0] * stride + cellSize / 2;
			if (index === 0) {
				ctx.moveTo(x, y);
			} else {
				ctx.lineTo(x, y);
			}
		});
		ctx.stroke();
	}, [cellSize, gridPixels, pathToRender, pathShakeVersion, stride]);

	return (
		<div
			ref={containerRef}
			className="flex w-full justify-center select-none"
		>
			<div
				className="grid-board relative overflow-hidden rounded-2xl border transition-colors ui-transition"
				style={{
					width: gridPixels,
					height: gridPixels,
				}}
			>
				<canvas
					ref={canvasRef}
					className="pointer-events-none absolute inset-0 z-20"
				/>
				<canvas
					ref={hintPathCanvasRef}
					className="pointer-events-none absolute inset-0 z-30"
				/>
				<div
					key={pathShakeVersion}
					className="pointer-events-none absolute inset-0 z-40"
					style={{ animation: pathShakeVersion > 0 ? "zip-path-shake 220ms ease-in-out" : undefined }}
				>
					<canvas
						ref={playerPathCanvasRef}
						className="absolute inset-0"
					/>
				</div>

				<div
					className="grid-lines absolute inset-0 z-10 grid"
					style={{
						gap: `${GRID_GAP_PX}px`,
						gridTemplateColumns: `repeat(${board.boardSize}, minmax(0, 1fr))`,
						gridTemplateRows: `repeat(${board.boardSize}, minmax(0, 1fr))`
					}}
				>
					{Array.from({ length: board.boardSize * board.boardSize }).map((_, index) => {
						const row = Math.floor(index / board.boardSize);
						const col = index % board.boardSize;
						const key = `${row},${col}`;
						const isHovered = hoveredCell === index;

						const isActive = activeCellKey === key;
						const isHint = hintCellKey === key;
						const rightWallExists =
							col < board.boardSize - 1
								? wallSet.has(getWallKey([row, col], [row, col + 1]))
								: false;
						const bottomWallExists =
							row < board.boardSize - 1
								? wallSet.has(getWallKey([row, col], [row + 1, col]))
								: false;
						return (
							<div
								key={index}
								className={[
									"grid-cell relative flex items-center justify-center",
									"transition-colors ui-transition",
									editMode === "WALLS"
										? "cursor-default"
										: "cursor-pointer",
									(editMode === "NUMBERS" && isHovered)
										? "grid-cell--hovered"
										: ""
								].join(" ")}
								onMouseEnter={() => {
									if (isPlayMode && isPointerDown) {
										onCellClick([row, col]);
										return;
									}

									if (editMode === "NUMBERS" && !isPlayMode) {
										setHoveredCell(index);
									}
								}}
								onMouseLeave={() => {
									if (!isPlayMode) {
										setHoveredCell(null);
									}
								}}
								onPointerDown={() => {
									if (isPlayMode) {
										setIsPointerDown(true);
										onCellClick([row, col]);
										return;
									}

									if (editMode === "NUMBERS") {
										onCellClick([row, col]);
									}
								}}
								onPointerUp={() => {
									setIsPointerDown(false);
								}}
								onPointerCancel={() => {
									setIsPointerDown(false);
								}}
							>
								{isActive && (
									<div className="absolute inset-0 rounded-xl border-2 border-primary shadow-[0_0_0_4px_var(--color-path-highlight-glow)]" />
								)}

								{isHint && !isActive && (
									<div className="absolute inset-0 rounded-xl border border-dashed border-hint-border bg-hint-bg" />
								)}

								{editMode === "WALLS" && col < board.boardSize - 1 && !rightWallExists && (
									<button
										type="button"
										aria-label={`Add a wall to the right of cell ${row + 1}, ${col + 1}`}
										className="absolute right-0 top-0 h-full w-4 cursor-pointer appearance-none border-0 bg-transparent p-0"
										onClick={(event) => {
											event.stopPropagation();
											onWallClick(createWall([row, col], [row, col + 1]));
										}}
									>
										<span
											className="
												absolute right-0 top-1/2 h-[52%] w-1.5
												-translate-y-1/2 translate-x-1/2 rounded-full
												bg-primary/20 opacity-70
												shadow-[0_0_12px_var(--color-path-highlight-glow)]
												transition-opacity ui-transition
												animate-pulse hover:bg-primary/35
											"
										/>
									</button>
								)}

								{editMode === "WALLS" && row < board.boardSize - 1 && !bottomWallExists && (
									<button
										type="button"
										aria-label={`Add a wall below cell ${row + 1}, ${col + 1}`}
										className="absolute bottom-0 left-0 h-4 w-full cursor-pointer appearance-none border-0 bg-transparent p-0"
										onClick={(event) => {
											event.stopPropagation();
											onWallClick(createWall([row, col], [row + 1, col]));
										}}
									>
										<span
											className="
												absolute bottom-0 left-1/2 h-1.5 w-[52%]
												-translate-x-1/2 translate-y-1/2 rounded-full
												bg-primary/20 opacity-70
												shadow-[0_0_12px_var(--color-path-highlight-glow)]
												transition-opacity ui-transition
												animate-pulse hover:bg-primary/35
											"
										/>
									</button>
								)}
							</div>
						);
					})}
				</div>

				<div className="pointer-events-none absolute inset-0 z-50">
					{Array.from({ length: board.boardSize * board.boardSize }).map((_, index) => {
						const row = Math.floor(index / board.boardSize);
						const col = index % board.boardSize;
						const key = `${row},${col}`;
						const waypointIndex = waypointIndexByCell.get(key);
						const isWaypoint = waypointIndex !== undefined;

						if (!isWaypoint) {
							return null;
						}

						const markerSize = Math.round(cellSize * 0.58);
						const left = col * stride + (cellSize - markerSize) / 2;
						const top = row * stride + (cellSize - markerSize) / 2;

						return (
							<div
								key={key}
								className="grid-waypoint absolute flex items-center justify-center rounded-full text-on-primary"
								style={{
									width: markerSize,
									height: markerSize,
									fontSize: Math.round(cellSize * 0.28),
									left,
									top,
									animation: `zip-pop 220ms ease-out ${waypointIndex * 30}ms both`
								}}
							>
								{waypointIndex + 1}
							</div>
						);
					})}
				</div>

				<div className="pointer-events-none absolute inset-0 z-40">
					{board.walls.map((wall, index) => {
						const [aRow, aCol] = wall.neighborA;
						const [bRow, bCol] = wall.neighborB;
						const isVertical = aRow === bRow;
						const renderKey = getWallKey(
							wall.neighborA,
							wall.neighborB
						);
						const wallLabel = isVertical
							? `Remove the wall between cells ${aRow + 1}, ${Math.min(aCol, bCol) + 1} and ${aRow + 1}, ${Math.max(aCol, bCol) + 1}`
							: `Remove the wall between cells ${Math.min(aRow, bRow) + 1}, ${aCol + 1} and ${Math.max(aRow, bRow) + 1}, ${aCol + 1}`;

						if (isVertical) {
							const row = aRow;
							const leftCell = Math.min(aCol, bCol);
							const x =
								leftCell * stride +
								cellSize -
								WALL_THICKNESS_PX / 2 +
								GRID_GAP_PX / 2;

							const y = row * stride + cellSize * 0.12;

							return (
								<div
									key={renderKey}
									role="button"
									aria-label={wallLabel}
									className="grid-wall absolute rounded-full cursor-pointer hover:opacity-80 transition-opacity ui-transition"
									style={{
										left: x,
										top: y,
										width: WALL_THICKNESS_PX,
										height: cellSize * 0.76,
										animation: `zip-wall-in 180ms ease-out ${index * 18}ms both`,
										pointerEvents: editMode === "WALLS" ? "auto" : "none"
									}}
									onClick={() => {
										if (editMode === "WALLS") {
											onWallClick(wall);
										}
									}}
								/>
							);
						}

						const topCell = Math.min(aRow, bRow);
						const col = aCol;
						const x = col * stride + cellSize * 0.12;
						const y =
							topCell * stride +
							cellSize -
							WALL_THICKNESS_PX / 2 +
							GRID_GAP_PX / 2;

						return (
							<div
								key={renderKey}
								role="button"
								aria-label={wallLabel}
								className="grid-wall absolute rounded-full cursor-pointer hover:opacity-80 transition-opacity ui-transition"
								style={{
									left: x,
									top: y,
									width: cellSize * 0.76,
									height: WALL_THICKNESS_PX,
									animation: `zip-wall-in 180ms ease-out ${index * 18}ms both`,
									pointerEvents: editMode === "WALLS" ? "auto" : "none"
								}}
								onClick={() => {
									if (editMode === "WALLS") {
										onWallClick(wall);
									}
								}}
							/>
						);
					})}
				</div>
			</div>
		</div>
	);
}
