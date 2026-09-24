/** One section rendered by the help modal. */
export interface HelpSection {
  id: string;
  title: string;
  icon: string;
  content: string[];
}

/** Static user guidance shown in the help modal. */
export const HELP_SECTIONS: readonly HelpSection[] = [
  {
    id: "what-is-zipsolver",
    title: "What is ZipSolver?",
    icon: "❓",
    content: [
      "ZipSolver helps you build, explore, and solve Zip puzzles on an interactive board.",
      "Create a puzzle by hand or start from an example, then switch to Play mode to follow the path yourself."
    ]
  },
  {
    id: "zip-rules",
    title: "Zip Puzzle Rules",
    icon: "🧩",
    content: [
      "Fill every cell exactly once, moving only to an orthogonally adjacent cell.",
      "Visit numbered waypoints in ascending order, starting with waypoint 1.",
      "Walls block movement between neighboring cells, so plan around them."
    ]
  },
  {
    id: "create-puzzle",
    title: "How do I create a puzzle?",
    icon: "🎮",
    content: [
      "Choose a grid size, then place at least two numbered waypoints in Build mode.",
      "Add walls between adjacent cells when you want to make the route more challenging.",
      "Click Show Solution to let ZipSolver search for a complete path.",
      "Switch to Play mode to try the puzzle with arrow keys, touch, or mouse clicks."
    ]
  },
  {
    id: "import-puzzle",
    title: "Import a Puzzle",
    icon: "🖼️",
    content: [
      "Use Import Screenshot to read a Zip board from an image.",
      "Choose the grid size that matches the screenshot, then check the detected waypoints and walls before solving.",
      "If a marker is unclear, ZipSolver will warn you so you can correct it in Build mode."
    ]
  },
  {
    id: "sharing",
    title: "Share a Puzzle",
    icon: "🔗",
    content: [
      "Click Share to copy a link containing your current board.",
      "Send the link to someone else or keep it as a quick way to return to the puzzle later.",
      "Opening a shared link restores the board automatically."
    ]
  },
  {
    id: "no-solution",
    title: "What does 'No solution exists' mean?",
    icon: "🔍",
    content: [
      "ZipSolver checked the current board but could not find a path that visits every cell and waypoint in order.",
      "Try moving a waypoint, removing a wall, or starting from one of the examples."
    ]
  }
];