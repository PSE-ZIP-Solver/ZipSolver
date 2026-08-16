import { useEffect } from "react";
import { createPortal } from "react-dom";

import type { GridSize } from "../types/board";

interface ImportSizeModalProps {
  isOpen: boolean;
  selectedSize: GridSize;
  onSelectSize: (size: GridSize) => void;
  onCancel: () => void;
  onConfirm: () => void;
}

export default function ImportSizeModal({
  isOpen,
  selectedSize,
  onSelectSize,
  onCancel,
  onConfirm,
}: ImportSizeModalProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onCancel();
      }
    };

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleEscape);

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onCancel]);

  if (!isOpen) {
    return null;
  }

  return createPortal(
    <div
      className="
        fixed inset-0 z-100
        flex items-center justify-center
        p-4
        bg-black/40
        backdrop-blur-sm
      "
      onClick={onCancel}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="import-size-modal-title"
        onClick={(event) => event.stopPropagation()}
        className="
          w-full
          max-w-sm

          rounded-2xl
          border
          panel-card-strong

          p-5
          sm:p-6
          space-y-5
        "
      >
        <div className="space-y-2">
          <h3
            id="import-size-modal-title"
            className="text-lg font-bold"
          >
            Screenshot grid size
          </h3>

          <p className="text-sm text-text/80">
            Select board size on the screenshot.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-2">
          {[6, 7, 8].map((size) => {
            const typedSize = size as GridSize;
            const selected = selectedSize === typedSize;

            return (
              <button
                key={size}
                type="button"
                onClick={() => onSelectSize(typedSize)}
                className={`
                  rounded-xl
                  border
                  px-3
                  py-3
                  text-sm
                  font-semibold
                  transition-colors
                  ${selected
                    ? "border-primary bg-primary text-white"
                    : "border-board-border bg-white/80 text-text hover:border-primary/40 hover:bg-primary/5"}
                `}
              >
                {size} x {size}
              </button>
            );
          })}
        </div>

        <div className="flex items-center justify-center gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="
              rounded-xl
              border
              border-board-border
              bg-white/80
              px-4
              py-2.5
              text-sm
              font-medium
              text-text
              transition-colors
              hover:bg-background
            "
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={onConfirm}
            className="
              rounded-xl
              bg-primary
              px-4
              py-2.5
              text-sm
              font-semibold
              text-white
              transition-colors
              hover:bg-primary-hover
            "
          >
            Continue import
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
