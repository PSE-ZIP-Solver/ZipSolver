export const dialogMessages = {
    welcome: "Welcome to ZipSolver! Build a puzzle or try some of our examples!",

    mode: {
        playEnabled: "Play mode: Arrows or tap to move, Ctrl+Z or button to undo, take a hint if you get stuck!",
        playEnabledWithoutGuarantee: "Play mode enabled, but we could not verify that this puzzle is solvable",
        buildEnabled: "Build mode: Continue editing your puzzle!",
    },

    play: {
        addWaypointFirst: "Add at least one waypoint before playing",
        alreadyOnCell: "You are already on this cell",
        waypointOrder: "Visit the waypoints in order",
        invalidMove: "That move is not valid",
        alreadyVisited: "You have already visited this cell",
        solved: "Puzzle solved! You visited every cell and all waypoints in order",
        lastWaypointOnly: "You reached the last waypoint, but you still need to visit every cell",
        switchToPlayFirst: "Switch to Play mode first",
        hintPathShown: "Hint path to the next waypoint has been highlighted",
        hintUnavailableForCurrentPath: "Hint is not available for your current path",
        unableToSolveForHint: "The system cannot solve this puzzle, so hints are unavailable",
    },

    solve: {
        addWaypointsFirst: "Add at least two waypoints first",
        requestFailed: "Solver request failed",
    },

    reset: "Puzzle reset",

    share: {
        nothingToShare: "Nothing to share",
        copied: "Share link copied to clipboard",
        clipboardDenied: "Clipboard access denied. Share link opened manually",
    },

    examples: {
        loaded: (name: string) => `Loaded example: ${name}`,
    },

    /*
     * Screenshot import. Extraction is probabilistic, so the copy distinguishes three
     * outcomes the user must respond to differently: a clean read, a read that needs
     * checking, and a read that produced an unusable board.
     */
    import: {
        started: "Reading your screenshot...",

        succeeded: (waypointCount: number, wallCount: number) =>
            `Imported ${waypointCount} waypoints and ${wallCount} walls from your screenshot`,

        succeededWithWarnings: (warningCount: number) =>
            `Board imported, but ${warningCount} ${warningCount === 1 ? "marker" : "markers"} `
            + "could not be read confidently. Check the numbers before solving",

        invalidBoard: (message: string) =>
            `Imported board needs fixing: ${message}`,

        noBoardDetected:
            "No Zip board found in that image. Upload a screenshot showing the full grid",

        failed: (message: string) => `Import failed: ${message}`,

        sizeHint: (size: number) =>
            `Reading the screenshot as a ${size}\u00d7${size} board. `
            + "Choose a different screenshot size if that is wrong",
    },
} as const;