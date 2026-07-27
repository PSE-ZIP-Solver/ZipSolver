import logo from "../assets/logoNoBg.png";

interface NavbarProps {
  onOpenHelp: () => void;

  advancedMode: boolean;
  onToggleAdvanced: () => void;
}

export default function Navbar({
  onOpenHelp,
  advancedMode,
  onToggleAdvanced,
}: NavbarProps) {

  return (
    <nav
      className="
                bg-chrome/90
                shadow-[0_12px_32px_rgba(102,63,24,0.08)]
                border-b
                border-footer-border
                backdrop-blur-md
            "
    >

      <div
        className="
                    max-w-7xl
                    mx-auto
                    px-6
                    py-2
                    flex
                    items-center
                    justify-between
                "
      >

        {/* Logo */}

        <div
          className="
                        flex
                        items-center
                        gap-3
                    "
        >

          <img
            src={logo}
            alt="ZipSolver Logo"
            className="
                            h-14
                            w-14
                            object-contain
                        "
          />

          <h1
            className="
                            text-3xl
                            font-bold
                            text-text
                        "
          >
            Zip <span className="text-primary">
              Solver
            </span>
          </h1>

        </div>



        {/* Actions */}

        <div
          className="
                        flex
                        items-center
                        gap-3
                    "
        >

          {/* Advanced */}

          <button
            onClick={onToggleAdvanced}
            className={`
                            px-3
                            py-2
                            rounded-lg
                            font-semibold
                            transition-colors

                            ${advancedMode
                ? `
                                        bg-primary
                                        text-white
                                    `
                : `
                                        text-text
                                        hover:bg-surface
                                    `
              }
                        `}
            aria-label="Toggle advanced mode"
          >
            ⚙️ Advanced
          </button>



          {/* Help */}

          <button
            onClick={onOpenHelp}
            className="
                            p-2
                            rounded-lg
                            text-footer-text
                            hover:bg-surface
                            transition-colors
                        "
            aria-label="Open help"
          >
            <span className="text-xl font-bold">
              ?
            </span>
          </button>

          {/* Theme placeholder for future theme switching logic */}
          <button
            className="
                            p-2
                            rounded-lg
                            text-footer-text
                            hover:bg-surface
                            transition-colors
                        "
            aria-label="Toggle theme"
          >
            <span className="text-xl">
              🌙
            </span>
          </button>
        </div>

      </div>

    </nav>
  );
}