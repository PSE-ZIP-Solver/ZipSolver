interface ActionPanelProps {
  canSolve: boolean;
  isSolving: boolean;

  onSolve: () => void;
  onReset: () => void;
  onImport: () => void;
  onExport: () => void;
}

export default function ActionPanel({
  canSolve,
  isSolving,
  onSolve,
  onReset,
  onImport,
  onExport,
}: ActionPanelProps) {
  return (
    <section
      className="
        rounded-xl
        border
        border-gray-300
        bg-white
        p-4
        shadow-sm
      "
    >
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={onImport}
          disabled={isSolving}
          className="
            rounded-lg
            border
            border-gray-300
            px-4
            py-2
            text-sm
            font-medium
            transition-colors

            hover:bg-gray-100
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          Import
        </button>

        <button
          type="button"
          onClick={onExport}
          disabled={isSolving}
          className="
            rounded-lg
            border
            border-gray-300
            px-4
            py-2
            text-sm
            font-medium
            transition-colors

            hover:bg-gray-100
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          Export
        </button>

        <button
          type="button"
          onClick={onReset}
          disabled={isSolving}
          className="
            rounded-lg
            border
            border-red-300
            px-4
            py-2
            text-sm
            font-medium
            text-red-600
            transition-colors

            hover:bg-red-50
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          Reset
        </button>

        <button
          type="button"
          onClick={onSolve}
          disabled={!canSolve || isSolving}
          className="
            rounded-lg
            bg-primary
            px-4
            py-2
            text-sm
            font-semibold
            text-white
            transition-colors

            hover:bg-primary-hover
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          {isSolving ? "Solving..." : "Solve"}
        </button>
      </div>
    </section>
  );
}