export interface ActionPanelProps {
	isSolving: boolean;
	onSolve: () => void;
	onReset: () => void;
	onImport: () => void;
	onExport: () => void;
}

export default function ActionPanel({
	isSolving,
	onSolve,
	onReset,
	onImport,
	onExport,
}: ActionPanelProps) {

	return (
		<div className="rounded-xl border border-slate-200 p-4 text-sm">
			<div className="font-semibold text-slate-900">Actions placeholder</div>
			<div>Solving: {isSolving ? "yes" : "no"}</div>
			<div className="mt-3 flex gap-2">
				<button type="button" onClick={onSolve}>Solve</button>
				<button type="button" onClick={onReset}>Reset</button>
				<button type="button" onClick={onImport}>Import</button>
				<button type="button" onClick={onExport}>Export</button>
			</div>
		</div>
	);
}
