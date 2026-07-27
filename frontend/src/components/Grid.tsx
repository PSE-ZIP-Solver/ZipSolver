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
	onCellClick: (position: Position) => void;
	onWallClick: (wall: Wall) => void;
}

const MAX_GRID_PIXELS = 600;
const MIN_GRID_PIXELS = 300;
const GRID_GAP_PX = 1;
const WALL_THICKNESS_PX = 6;

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
	onCellClick,
	onWallClick
}: GridProps) {

	const canvasRef = useRef<HTMLCanvasElement | null>(null);
	const containerRef = useRef<HTMLDivElement | null>(null);

	const [containerWidth, setContainerWidth] = useState(0);
	const [hoveredCell, setHoveredCell] = useState<number | null>(null);

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

		if (!solution || solution.length < 2) {
			return;
		}

		const duration = 650;
		let raf = 0;
		const startedAt = performance.now();

		const draw = (now: number) => {
			const animationProgress = Math.min(1, (now - startedAt) / duration);
			const visibleSegments = animationProgress * (solution.length - 1);

			ctx.clearRect(0, 0, gridPixels, gridPixels);

			ctx.lineWidth = Math.max(2, cellSize * 0.16);
			ctx.lineCap = "round";
			ctx.lineJoin = "round";
			ctx.shadowColor = "rgba(249, 115, 22, 0.28)";
			ctx.shadowBlur = Math.max(4, cellSize * 0.12);

			for (let i = 1; i < solution.length; i += 1) {
				if (i > Math.ceil(visibleSegments)) break;

				const previous = solution[i - 1];
				const current = solution[i];
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

				const tintProgress = i / solution.length;
				const hue = 48 - tintProgress * 36;
				const lightness = 66 - tintProgress * 12;

				ctx.beginPath();
				ctx.moveTo(prevX, prevY);
				ctx.lineTo(currentX, currentY);
				ctx.strokeStyle = `hsl(${hue}, 100%, ${lightness}%)`;
				ctx.stroke();
			}

			if (animationProgress < 1) {
				raf = requestAnimationFrame(draw);
			}
		};

		raf = requestAnimationFrame(draw);

		return () => cancelAnimationFrame(raf);
	}, [cellSize, gridPixels, solution, stride]);

	return (
		<div
			ref={containerRef}
			className="flex w-full justify-center select-none"
		>
			<div
				className="grid-board relative overflow-hidden rounded-2xl border transition-colors duration-200"
				style={{
					width: gridPixels,
					height: gridPixels,
				}}
			>
				<canvas
					ref={canvasRef}
					className="pointer-events-none absolute inset-0 z-20"
				/>

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
						const waypointIndex = waypointIndexByCell.get(key);
						const isWaypoint = waypointIndex !== undefined;
						const isHovered = hoveredCell === index;

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
									"transition-colors duration-150",
									editMode === "WALLS"
										? "cursor-default"
										: "cursor-pointer"
									,
									editMode === "NUMBERS" && isHovered
										? "grid-cell--hovered"
										: ""
								].join(" ")}
								onMouseEnter={() => setHoveredCell(index)}
								onMouseLeave={() => setHoveredCell(null)}
								onClick={() => {
									if (editMode === "NUMBERS") {
										onCellClick([row, col]);
									}
								}}
							>
								{isWaypoint && (
									<div
										className="grid-waypoint flex items-center justify-center rounded-full text-white"
										style={{
											width: Math.round(cellSize * 0.58),
											height: Math.round(cellSize * 0.58),
											fontSize: Math.round(cellSize * 0.28),
											animation: `zip-pop 220ms ease-out ${waypointIndex * 30}ms both`
										}}
									>
										{waypointIndex + 1}
									</div>
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
												shadow-[0_0_12px_rgba(249,115,22,0.18)]
												transition-opacity duration-200
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
												shadow-[0_0_12px_rgba(249,115,22,0.18)]
												transition-opacity duration-200
												animate-pulse hover:bg-primary/35
											"
										/>
									</button>
								)}
							</div>
						);
					})}
				</div>

				<div className="pointer-events-none absolute inset-0 z-30">
					{board.walls.map((wall, index) => {
						const [aRow, aCol] = wall.neighborA;
						const [bRow, bCol] = wall.neighborB;
						const isVertical = aRow === bRow;
						const renderKey = `${getWallKey(wall.neighborA, wall.neighborB)}-${index}`;

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
									className="grid-wall absolute rounded-full"
									style={{
										left: x,
										top: y,
										width: WALL_THICKNESS_PX,
										height: cellSize * 0.76,
										animation: `zip-wall-in 180ms ease-out ${index * 18}ms both`
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
								className="grid-wall absolute rounded-full"
								style={{
									left: x,
									top: y,
									width: cellSize * 0.76,
									height: WALL_THICKNESS_PX,
									animation: `zip-wall-in 180ms ease-out ${index * 18}ms both`
								}}
							/>
						);
					})}
				</div>
			</div>
		</div>
	);
}