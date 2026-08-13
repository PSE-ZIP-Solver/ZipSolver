export const dialogMessages = {
    welcome: "Welcome to ZipSolver! Build a puzzle or try some of our examples!",

    mode: {
        playEnabled: "Play mode enabled. Give it a try!",
        buildEnabled: "Build mode enabled. Continue editing your puzzle",
    },

    play: {
        addWaypointFirst: "Add at least one waypoint before playing",
        alreadyOnCell: "You are already on this cell",
        lastMoveUndone: "Last move undone",
        waypointOrder: "Visit the waypoints in order",
        invalidMove: "That move is not valid",
        alreadyVisited: "You have already visited this cell",
        solved: "Puzzle solved! You visited every cell and all waypoints in order",
        lastWaypointOnly: "You reached the last waypoint, but you still need to visit every cell",
        movedTo: (position: [number, number]) => `Moved to (${position[0] + 1}, ${position[1] + 1})`,
        switchToPlayFirst: "Switch to Play mode first",
        hintLocked: "Solve the puzzle to unlock hints",
        hintAlreadyHere: "You are already on the suggested cell",
        hintBlocked: "The hinted move is blocked by a wall",
        hintApplied: (position: [number, number]) => `Hint applied to (${position[0] + 1}, ${position[1] + 1})`,
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
} as const;