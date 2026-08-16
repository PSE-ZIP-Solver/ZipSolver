import { useEffect } from "react";
import { HELP_SECTIONS } from "../data/helpContent";

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function HelpModal({
  isOpen,
  onClose,
}: HelpModalProps) {
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.body.style.overflow = "hidden";

    window.addEventListener("keydown", handleEscape);

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="
        fixed inset-0 z-50
        flex items-center justify-center
        p-4
        bg-overlay
        backdrop-blur-sm
      "
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="help-modal-title"
        onClick={(event) => event.stopPropagation()}
        className="
          w-full
          max-w-3xl
          max-h-[90vh]
          overflow-hidden

          rounded-2xl
          border
          panel-card-strong

          flex
          flex-col
        "
      >
        <div
          className="
            flex items-center justify-between
            p-4 sm:p-6
            border-b
            border-footer-border
          "
        >
          <h2
            id="help-modal-title"
            className="
              text-lg
              sm:text-xl
              md:text-2xl
              font-bold
            "
          >
            Help & Guide
          </h2>

          <button
            onClick={onClose}
            aria-label="Close help modal"
            className="
              h-10 w-10
              rounded-lg

              flex items-center justify-center

              text-xl
              hover:bg-primary/10
              transition-colors
              ui-transition
            "
          >
            ✕
          </button>
        </div>

        <div
          className="
            flex-1
            overflow-y-auto
            p-4 sm:p-6
            space-y-6
          "
        >
          {HELP_SECTIONS.map((section) => (
            <section key={section.id}>
              <h3
                className="
                  flex items-center gap-2
                  mb-3

                  text-lg
                  font-semibold
                "
              >
                <span>{section.icon}</span>
                {section.title}
              </h3>

              <div className="space-y-2 text-sm sm:text-base">
                {section.content.map((paragraph) => (
                  <p key={paragraph}>{paragraph}</p>
                ))}
              </div>
            </section>
          ))}
        </div>

        <div
          className="
            border-t
            border-footer-border
            p-4
            sm:p-6

            flex justify-end
          "
        >
          <button
            onClick={onClose}
            className="btn-primary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}