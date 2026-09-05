import logo from "../assets/logoNoBg.png";

/** Navigation actions and current theme state supplied by the application shell. */
interface NavbarProps {
  onOpenHelp: () => void;

  isDarkTheme: boolean;
  onToggleTheme: () => void;
}

/** Renders the application identity and global help/theme actions. */
export default function Navbar({
  onOpenHelp,
  isDarkTheme,
  onToggleTheme,
}: NavbarProps) {

  return (
    <nav
      className="
                bg-chrome/90
                shadow-[0_12px_32px_rgba(23,14,9,0.18)]
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

          {/* Advanced toggle disabled by product decision.
          <button
            className="
                            px-3
                            py-2
                            rounded-lg
                            font-semibold
                            transition-colors
                            ui-transition
                            text-text
                            hover:bg-surface
                        "
            aria-label="Toggle advanced mode"
            disabled
          >
            ⚙️ Advanced
          </button>
          */}



          {/* Help */}

          <button
            type="button"
            onClick={onOpenHelp}
            className="
                            p-2
                            rounded-lg
                            text-footer-text
                            hover:bg-surface
                            transition-colors
                            ui-transition
                        "
            aria-label="Open help"
          >
            <span className="text-xl font-bold">
              ?
            </span>
          </button>

          <button
            type="button"
            onClick={onToggleTheme}
            className="
                            p-2
                            rounded-lg
                            text-footer-text
                            hover:bg-surface
                            transition-colors
                            ui-transition
                        "
            aria-label="Toggle theme"
            title={isDarkTheme ? "Switch to light theme" : "Switch to dark theme"}
          >
            <span className="text-xl">
              {isDarkTheme ? "☀️" : "🌙"}
            </span>
          </button>
        </div>

      </div>

    </nav>
  );
}