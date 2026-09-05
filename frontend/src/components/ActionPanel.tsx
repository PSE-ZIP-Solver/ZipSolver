import { useRef, useState } from "react";

import type { ViewMode } from "../types/grid";
import type { GridSize } from "../types/board";
import { IMAGE_ACCEPT_ATTRIBUTE } from "../utils/fileValidation";
import ImportSizeModal from "./ImportSizeModal";

/** Primary actions for solving, importing, sharing, resetting, and changing mode. */
interface ActionPanelProps {
  canSolve: boolean;
  canPlay: boolean;
  isSolving: boolean;
  isPlayCompleted: boolean;
  isImporting: boolean;
  viewMode: ViewMode;

  onSolve: () => void;
  onViewModeChange: (mode: ViewMode) => void | Promise<void>;
  onReset: () => void;
  onShare: () => void;
  onImport: (file: File, imageBoardSize: GridSize) => void;
}

/** Renders the primary puzzle workflow actions and import-size dialog. */
export default function ActionPanel({
  canSolve,
  canPlay,
  isSolving,
  isPlayCompleted,
  isImporting,
  viewMode,
  onSolve,
  onViewModeChange,
  onReset,
  onShare,
  onImport,
}: ActionPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [importSizeModalOpen, setImportSizeModalOpen] = useState(false);
  const [pendingImportFile, setPendingImportFile] = useState<File | null>(null);
  const [pendingBoardSize, setPendingBoardSize] = useState<GridSize>(6);

  const isBusy = isSolving || isImporting;

  function closeImportSizeModal() {
    setImportSizeModalOpen(false);
    setPendingImportFile(null);
    setPendingBoardSize(6);
  }

  function confirmImportSize() {
    if (!pendingImportFile) {
      closeImportSizeModal();
      return;
    }

    onImport(pendingImportFile, pendingBoardSize);
    closeImportSizeModal();
  }

  function handleFileSelected(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    event.target.value = "";

    if (file) {
      setPendingImportFile(file);
      setPendingBoardSize(6);
      setImportSizeModalOpen(true);
    }
  }

  return (
    <section className="panel-card rounded-2xl p-4">
      <div className="flex flex-col gap-3">
        <div className="flex rounded-xl border border-board-border bg-background/70 p-1">
          {(["BUILD", "PLAY"] as ViewMode[]).map((mode) => {
            const isActive = viewMode === mode;
            const isModeDisabled = isSolving || (mode === "PLAY" && !canPlay);

            return (
              <button
                key={mode}
                type="button"
                onClick={() => {
                  void onViewModeChange(mode);
                }}
                disabled={isModeDisabled}
                className={`flex-1 rounded-lg px-3 py-2 text-sm font-semibold transition-colors ui-transition ${
                  isActive
                    ? "bg-primary text-on-primary shadow-sm"
                    : "text-text hover:bg-primary/10"
                } disabled:cursor-not-allowed disabled:opacity-50`}
              >
                {mode === "BUILD" ? "Build" : "Play"}
              </button>
            );
          })}
        </div>

        <button
          type="button"
          onClick={onSolve}
          disabled={!canSolve || isSolving || (viewMode === "PLAY" && isPlayCompleted)}
          className="
            flex
            min-h-14
            w-full
            items-center
            justify-center
            gap-2
            rounded-xl
            bg-primary
            px-5
            py-4
            text-base
            font-semibold
            text-on-primary
            shadow-[0_10px_24px_var(--color-path-highlight-glow)]
            transition-colors
            ui-transition

            hover:bg-primary-hover
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          <SolveIcon />
          {isSolving ? "Solving..." : "Show Solution"}
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept={IMAGE_ACCEPT_ATTRIBUTE}
          onChange={handleFileSelected}
          className="sr-only"
          aria-label="Import a puzzle screenshot"
        />

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isBusy}
          className="
            flex
            min-h-12
            w-full
            items-center
            justify-center
            gap-2
            rounded-xl
            border
            border-dashed
            border-primary/40
            bg-primary/5
            px-4
            py-3
            text-sm
            font-semibold
            text-primary
            transition-colors

            hover:bg-primary/10
            hover:border-primary/60
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          <ImportIcon />
          {isImporting ? "Reading screenshot..." : "Import from screenshot"}
        </button>

        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={onReset}
            disabled={isBusy}
            className="
              flex
              w-full
              items-center
              justify-center
              gap-2
              rounded-xl
              border
              border-danger-border
              bg-danger-surface
              px-4
              py-3
              text-sm
              font-medium
              text-danger-text
              transition-colors
              ui-transition

              hover:bg-danger-surface-hover
              hover:border-danger-border-hover
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            <ResetIcon />
            Reset
          </button>

          <button
            type="button"
            onClick={onShare}
            disabled={isBusy}
            className="
              flex
              w-full
              items-center
              justify-center
              gap-2
              rounded-xl
              border
              border-board-border
              bg-surface-soft/80
              px-4
              py-3
              text-sm
              font-medium
              text-text
              transition-colors
              ui-transition

              hover:bg-background
              hover:border-primary/20
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            <ShareIcon />
            Share
          </button>
        </div>
      </div>

      <ImportSizeModal
        isOpen={importSizeModalOpen}
        selectedSize={pendingBoardSize}
        onSelectSize={setPendingBoardSize}
        onCancel={closeImportSizeModal}
        onConfirm={confirmImportSize}
      />
    </section>
  );
}

function ImportIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <path d="M21 15l-5-5L5 21" />
    </svg>
  );
}

function SolveIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M13 2L4 14h7l-1 8 10-12h-7l0-8z" />
    </svg>
  );
}

function ResetIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 12a9 9 0 1 0 3-6.7" />
      <path d="M3 4v5h5" />
    </svg>
  );
}

function ShareIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7" />
      <path d="M16 6l-4-4-4 4" />
      <path d="M12 2v14" />
    </svg>
  );
}
