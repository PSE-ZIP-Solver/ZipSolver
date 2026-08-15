import { useRef } from "react";

import type { ViewMode } from "../types/grid";
import { IMAGE_ACCEPT_ATTRIBUTE } from "../utils/fileValidation";

interface ActionPanelProps {
  canSolve: boolean;
  isSolving: boolean;
  isImporting: boolean;
  viewMode: ViewMode;

  onSolve: () => void;
  onViewModeChange: (mode: ViewMode) => void;
  onReset: () => void;
  onShare: () => void;
  onImport: (file: File) => void;
}

export default function ActionPanel({
  canSolve,
  isSolving,
  isImporting,
  viewMode,
  onSolve,
  onViewModeChange,
  onReset,
  onShare,
  onImport,
}: ActionPanelProps) {
  /*
   * The native file input cannot be styled to match the rest of the panel, so it is kept
   * off-screen and driven by a real button. `sr-only` rather than `display: none` so the
   * input stays reachable by assistive technology and keyboard users.
   */
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isBusy = isSolving || isImporting;

  function handleFileSelected(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    /*
     * Reset the input value after every selection. Without it, picking the same file
     * twice in a row fires no change event, so a user who fixes their screenshot and
     * re-selects it silently gets nothing.
     */
    event.target.value = "";

    if (file) {
      onImport(file);
    }
  }

  return (
    <section
      className="panel-card rounded-2xl p-4"
    >
      <div className="flex flex-col gap-3">

        <button
          type="button"
          onClick={onSolve}
          disabled={!canSolve || isSolving}
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
            text-white
            shadow-sm
            shadow-orange-500/20
            transition-colors

            hover:bg-primary-hover
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          <SolveIcon />
          {isSolving ? "Solving..." : "Solve"}
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

        <div className="flex rounded-xl border border-board-border bg-background/70 p-1">
          {(["BUILD", "PLAY"] as ViewMode[]).map((mode) => {
            const isActive = viewMode === mode;

            return (
              <button
                key={mode}
                type="button"
                onClick={() => onViewModeChange(mode)}
                className={`flex-1 rounded-lg px-3 py-2 text-sm font-semibold transition-colors ${
                  isActive
                    ? "bg-primary text-white shadow-sm"
                    : "text-text hover:bg-primary/10"
                }`}
              >
                {mode === "BUILD" ? "Build" : "Play"}
              </button>
            );
          })}
        </div>

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
              border-rose-200
              bg-white/80
              px-4
              py-3
              text-sm
              font-medium
              text-red-600
              transition-colors

              hover:bg-rose-50
              hover:border-rose-300
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
              bg-white/75
              px-4
              py-3
              text-sm
              font-medium
              text-text
              transition-colors

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