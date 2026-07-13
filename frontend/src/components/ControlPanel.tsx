import {
	type EditMode,
} from "./GridBuilder";

export interface ControlPanelProps {
	boardSize: 6 | 7 | 8;
	editMode: EditMode;
	isSolving: boolean;
	onGridSizeChange: (size: 6 | 7 | 8) => void;
	onEditModeChange: (mode: EditMode) => void;
}

export default function ControlPanel({
	boardSize,
	editMode,
	isSolving,
	onGridSizeChange,
	onEditModeChange,
}: ControlPanelProps) {

	return (
		<div className="rounded-xl border border-slate-200 p-4 text-sm">
			<div className="font-semibold text-slate-900">Control panel placeholder</div>
			<div>Board size: {boardSize}x{boardSize}</div>
			<div>Edit mode: {editMode}</div>
			<div>Solving: {isSolving ? "yes" : "no"}</div>
			<div className="mt-3 flex gap-2">
				<button type="button" onClick={() => onGridSizeChange(6)}>6x6</button>
				<button type="button" onClick={() => onGridSizeChange(7)}>7x7</button>
				<button type="button" onClick={() => onGridSizeChange(8)}>8x8</button>
				<button type="button" onClick={() => onEditModeChange("NUMBERS")}>Numbers</button>
				<button type="button" onClick={() => onEditModeChange("WALLS")}>Walls</button>
			</div>
		</div>
	);
}
