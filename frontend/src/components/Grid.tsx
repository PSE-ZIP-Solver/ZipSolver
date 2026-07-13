import {
	type BoardConfig,
	type Position,
	type SolutionPath,
	type Wall,
} from "../types/board";

export type GridEditMode =
	| "NUMBERS"
	| "WALLS";

export interface GridProps {
	board: BoardConfig;
	solution: SolutionPath | null;
	editMode: GridEditMode;
	onCellClick: (position: Position) => void;
	onWallClick: (wall: Wall) => void;
}

export default function Grid({
	board,
	solution,
	editMode,
	onCellClick,
	onWallClick,
}: GridProps) {

	void onCellClick;
	void onWallClick;

	return (
		<div className="rounded-xl border border-dashed border-slate-300 p-4 text-sm text-slate-600">
			<div className="font-medium text-slate-900">Grid placeholder</div>
			<div>Board size: {board.boardSize}x{board.boardSize}</div>
			<div>Waypoints: {board.waypoints.length}</div>
			<div>Walls: {board.walls.length}</div>
			<div>Edit mode: {editMode}</div>
			<div>Solution points: {solution?.length ?? 0}</div>
		</div>
	);
}
