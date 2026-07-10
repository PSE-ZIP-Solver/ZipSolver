export interface HelpSection {
  id: string;
  title: string;
  icon: string;
  content: string[];
}

export const HELP_SECTIONS: HelpSection[] = [
  {
    id: "what-is-zipsolver",
    title: "What is ZipSolver?",
    icon: "❓",
    content: [
      "ZipSolver is a Reinforcement Learning based tool for creating, editing, validating, and solving Zip puzzles.",
      "The application allows users to design their own puzzles, import and export configurations, and visualize solver results."
    ]
  },
  {
    id: "zip-rules",
    title: "Zip Puzzle Rules",
    icon: "🧩",
    content: [
      "Place numbered waypoints on the board.",
      "The solution path must visit all waypoints in ascending order.",
      "The path must respect all puzzle constraints and walls."
    ]
  },
  {
    id: "create-puzzle",
    title: "How do I create a puzzle?",
    icon: "🎮",
    content: [
      "Select a grid size.",
      "Place numbered waypoints on the board.",
      "Add walls between adjacent cells if necessary.",
      "Click Solve to search for a solution."
    ]
  },
  {
    id: "import-export",
    title: "Import and Export",
    icon: "📁",
    content: [
      "Import a puzzle from a JSON file.",
      "Export your current puzzle configuration for later use or sharing."
    ]
  },
  {
    id: "validation-failed",
    title: "What does 'Validation Failed' mean?",
    icon: "⚠️",
    content: [
      "The current puzzle configuration is not valid.",
      "Review the reported issue, correct it, and try again."
    ]
  },
  {
    id: "no-solution",
    title: "What does 'No Solution Found' mean?",
    icon: "🔍",
    content: [
      "The puzzle configuration is valid, but no valid solution could be found.",
      "Check the waypoint placement and wall configuration."
    ]
  }
];