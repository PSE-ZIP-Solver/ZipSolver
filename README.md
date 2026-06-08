# ZipSolver - Interactive Puzzle Solver

ZipSolver is an interactive web application for solving grid-based puzzles using a depth-first search (DFS) algorithm. Users can create custom puzzles with numbered waypoints and walls, visualize the solving process step-by-step, and explore multiple solutions. The application features a modern UI with dark mode support and both simple and advanced modes for different user skill levels.

## Overview

### Project Purpose

ZipSolver enables users to:
- **Design custom puzzles** by placing numbered waypoints and walls on a configurable grid
- **Solve puzzles** using an optimized DFS algorithm
- **Visualize solutions** with step-by-step animations
- **Explore alternatives** by browsing multiple valid solutions
- **Track performance** with real-time metrics and iteration counters
- **Export configurations** to JSON for sharing and reuse

### How It Works

1. **Puzzle Setup**: Create a grid (3x3 to 9x9), place numbered waypoints sequentially, and add walls as barriers
2. **Solving**: The ZipSolver engine uses depth-first search to find all valid paths connecting waypoints in order
3. **Visualization**: Solutions are displayed as step-by-step paths on the grid, with optional animation
4. **Exploration**: Browse through multiple solutions and compare their paths

## Technology Stack

### Frontend Framework
- **React 19.2.5** - Modern UI library with hooks
- **Vite 8.0.11** - Fast build tool and dev server with HMR support

### Styling
- **Tailwind CSS 4.3.0** - Utility-first CSS framework for responsive design
- **PostCSS 8.5.14** - CSS transformation and processing

### UI Components & Icons
- **Lucide React 1.14.0** - Beautiful, consistent icon library

### Development Tools
- **ESLint 10.2.1** - Code quality and style checking
- **ESLint Plugins**:
  - `eslint-plugin-react-refresh` - Fast Refresh compliance
  - `eslint-plugin-react-hooks` - React hooks best practices

### Build Configuration
- **Vite plugins**:
  - `@vitejs/plugin-react` - React Fast Refresh support
- **TypeScript support** (dev dependencies included)

## Project Structure

```
prototype/
├── public/                 # Static assets
├── src/
│   ├── components/        # React components
│   ├── context/           # React Context API (Theme management)
│   ├── data/              # Static data (example configurations)
│   ├── utils/             # Utility functions (solver engine, exporters)
│   ├── assets/            # Images and static resources
│   ├── App.jsx            # Root component
│   ├── main.jsx           # React entry point
│   └── index.css          # Global styles
├── package.json           # Project dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── eslint.config.js       # ESLint rules configuration
```

## Component Documentation

### Core Components

#### **Navbar** (`Navbar.jsx`)
Navigation header with application branding and controls.

**Features:**
- Application logo and title
- Theme toggle (light/dark mode)
- Advanced mode toggle switch
- Help modal trigger button
- Responsive layout that adapts to screen size

**Props:**
- None (uses `useTheme` context hook)

**State Management:**
- Help modal open/close state
- Accesses theme and advanced mode from context

---

#### **GridBuilder** (`GridBuilder.jsx`)
Main container component that orchestrates the entire puzzle creation and solving workflow.

**Features:**
- Manages grid size (3x3 to 9x9)
- Handles waypoint placement and renumbering
- Manages wall creation and deletion
- Coordinates solver execution
- Tracks solution browsing state
- Calculates and displays performance metrics

**Key State Variables:**
- `gridSize` - Dimensions of the puzzle grid
- `wayPoints` - Dictionary of placed numbered waypoints
- `walls` - Wall barrier definitions (horizontal and vertical)
- `editMode` - Current editing mode ('numbers' or 'walls')
- `solutions` - Array of all found solutions
- `currentSolutionIndex` - Currently viewed solution
- `solverRunning` - Solver execution status
- `statusMessage` - UI feedback messages

**Main Functions:**
- `handleCellClick()` - Add/remove waypoints with auto-renumbering
- `handleWallClick()` - Toggle wall barriers
- `handleSolve()` - Execute the solver algorithm
- `handleReset()` - Clear the entire grid
- `handleExport()` - Export configuration to JSON

---

#### **Grid** (`Grid.jsx`)
Canvas-based visualization component that renders the puzzle grid, waypoints, walls, and solution paths.

**Features:**
- Responsive canvas rendering (scales to container width)
- Visual rendering of:
  - Grid cells with coordinates
  - Numbered waypoints (with distinct colors)
  - Wall barriers (horizontal and vertical)
  - Solution paths with step-by-step highlighting
  - Current position indicator during animation
- Handles click events for cell and wall interactions
- Automatic re-rendering on state changes

**Props:**
- `gridSize` - Grid dimensions
- `wayPoints` - Waypoint locations and numbers
- `walls` - Wall configurations
- `solutions` - Found solutions array
- `currentSolutionIndex` - Active solution index
- `isAnimating` - Animation state
- `currentStepIndex` - Animation step position
- `editMode` - Current editing mode
- `onCellClick` - Waypoint click handler
- `onWallClick` - Wall click handler

**Technical Details:**
- Uses Canvas API for efficient rendering
- Implements responsive sizing with ResizeObserver
- Optimized redraw cycle for smooth animations
- Color scheme adapts to light/dark theme

---

#### **Controls** (`Controls.jsx`)
Control panel for puzzle editing modes, solver actions, and navigation through solutions.

**Features:**
- Edit mode tabs:
  - **Numbers** - Add/edit waypoints
  - **Walls** - Add/remove barriers
- Grid size selector (3-9)
- Solver actions:
  - Solve button (initiates solver)
  - Reset button (clear grid)
  - Export button (save to JSON)
- Solution navigation:
  - Previous/Next solution buttons
  - Solution counter
- Status indicator with message feedback
- Solver execution time display

**Props:**
- All states from GridBuilder (grid size, mode, solutions, etc.)
- Event handlers for user actions
- Status information for UI feedback

---

#### **MetricsPanel** (`MetricsPanel.jsx`)
Displays reinforcement learning-style metrics for solver performance analysis.

**Features:**
- Shows metrics only when solutions are found
- Displays:
  - **Average Reward** - Quality metric for current solution
  - **Episode Steps** - Number of steps in solution
  - **Training Progress** - Solver progress indicator
  - **Convergence Rate** - Algorithm convergence metric
- Generates realistic metrics based on solution data
- Responsive card layout

**Props:**
- `solutions` - Array of found solutions
- `currentSolutionIndex` - Current solution index

**Note:** Metrics are calculated procedurally for UI demonstration; they provide realistic-looking feedback about solver performance.

---

#### **ExamplesSection** (`ExamplesSection.jsx`)
Displays preset puzzle examples for users to learn from or use as templates.

**Features:**
- Shows examples only for available grid sizes
- Displays example puzzles as interactive cards
- One-click loading of example configurations
- Conditionally rendered (hidden when no examples exist)

**Props:**
- `gridSize` - Current grid size (filters displayed examples)
- `onExampleSelect` - Callback when example is selected

**Data Source:**
- Loads examples from `examplesData.js`
- Pre-configured for common grid sizes

---

#### **ExampleCard** (`ExampleCard.jsx`)
Individual example puzzle card component displayed in ExamplesSection.

**Features:**
- Displays example name and difficulty
- Shows preview of puzzle configuration
- Click handler to load example
- Styled to match application theme

**Props:**
- `example` - Example configuration object
- `onSelect` - Selection callback

---

#### **Footer** (`Footer.jsx`)
Application footer with metadata and links.

**Features:**
- Application version and copyright information
- Links to documentation or external resources
- Responsive layout

---

#### **HelpModal** (`HelpModal.jsx`)
Modal dialog providing user guidance and help documentation.

**Features:**
- Help content with keyboard shortcuts
- Editing mode explanations
- Solver usage instructions
- Modal overlay with close button
- Responsive design

**Props:**
- `isOpen` - Modal visibility state
- `onClose` - Close handler

---

### Context & State Management

#### **ThemeContext** (`context/ThemeContext.jsx`)
Centralized theme and advanced mode management using React Context API.

**Provided Values:**
- `theme` - Current theme ('light' or 'dark')
- `toggleTheme()` - Switch theme
- `advancedMode` - Advanced mode state
- `toggleAdvancedMode()` - Toggle advanced features

**Features:**
- Persistent storage using localStorage
- Respects system color scheme preferences
- Provides context hook: `useTheme()`

---

## Utility Functions

### **ZipSolver Engine** (`utils/zipSolver.js`)

The core puzzle-solving algorithm using Depth-First Search (DFS).

**Class: `ZipSolver`**

**Constructor Parameters:**
- `gridSize` - Dimension of the square grid
- `numbers` - Dictionary of waypoint positions and their numbers
- `walls` - Walls configuration with horizontal and vertical barriers

**Key Methods:**
- `isValid(r, c)` - Check if cell is within grid bounds
- `hasWallBetween(r1, c1, r2, c2)` - Detect wall barriers between cells
- `solve()` - Main solver method (returns all valid solutions)
- `dfs()` - Recursive depth-first search implementation

**Algorithm Details:**
- Finds all valid paths connecting numbered waypoints in sequential order
- Supports wall barriers and grid boundaries
- Iteration limit (15M) prevents infinite loops on unsolvable puzzles
- Returns empty array if no solutions exist

**Features:**
- Tracks iteration count for performance metrics
- Detects when iteration limit is reached
- Efficient waypoint sequencing validation

### **JSON Exporter** (`utils/jsonExporter.js`)

Utilities for exporting and importing puzzle configurations.

**Functions:**
- `exportGridToJSON(gridSize, wayPoints, walls)` - Serialize puzzle to JSON
- `downloadJSON(data, filename)` - Trigger browser download

**Export Format:**
```json
{
  "gridSize": 6,
  "wayPoints": {
    "0,0": 1,
    "3,3": 2,
    ...
  },
  "walls": {
    "h": { /* horizontal walls */ },
    "v": { /* vertical walls */ }
  }
}
```

---

## Data

### **Examples Data** (`data/examplesData.js`)

Pre-configured puzzle examples for different grid sizes.

**Structure:**
- Organized by grid size (4x4, 6x6, 8x8, etc.)
- Each example includes:
  - Name/title
  - Difficulty level
  - Waypoint configuration
  - Wall configuration

**Usage:**
- Loaded dynamically by ExamplesSection
- Provides learning references for users

---

## Getting Started

### Installation

```bash
cd prototype
npm install
```

### Development

```bash
npm run dev
```
Starts Vite development server with hot module replacement (HMR) on `http://localhost:5173`

### Building

```bash
npm run build
```
Creates optimized production build in `dist/` directory

### Linting

```bash
npm run lint
```
Checks code quality using ESLint

### Preview

```bash
npm run preview
```
Preview production build locally

---

## Features Overview

### Editing Modes
- **Numbers Mode**: Place numbered waypoints sequentially on the grid
- **Walls Mode**: Add horizontal and vertical walls as puzzle constraints

### Solving
- Find all valid solutions connecting waypoints in order
- Real-time solver execution with status feedback
- Iteration count tracking to monitor algorithm performance

### Visualization
- Step-by-step solution animation
- Path highlighting for current solution
- Support for browsing multiple solutions

### User Experience
- Dark/Light theme toggle
- Responsive design (works on desktop and tablet)
- Advanced mode for experienced users
- Help modal with instructions
- Export functionality for sharing puzzles

### Performance
- Canvas-based rendering for efficiency
- Responsive grid scaling
- Optimized re-render cycle
- Solver iteration limits prevent UI freezing

---

## Advanced Mode

When enabled, users gain access to:
- Additional metrics and statistics
- Solver performance details
- Advanced configuration options
- Detailed iteration tracking

---

## Accessibility & Responsive Design

- Tailwind CSS ensures responsive layouts across devices
- Dark mode for reduced eye strain
- Clear visual feedback for all interactions
- Keyboard accessible controls (via theme toggle, buttons)
- Semantic HTML structure

---

## Future Enhancements

Potential improvements mentioned in UML documentation:
- **Reinforcement Learning Integration** - Machine learning-based puzzle solving
- **Backend API** - REST endpoints for puzzle validation
- **Database** - Persistent storage of user puzzles
- **Collaborative Features** - Sharing and puzzle voting
- **Advanced Input Validation** - Enhanced error handling

---

## Project Layout

See `UML-Diagramms/` folder for architectural diagrams:
- `ComponentArchtecturdDiagram.puml` - High-level architecture
- `sequence.puml` - Interaction sequences
- `backend/` - Backend design diagrams
- `frontend/` - Frontend component hierarchy

---

## Notes

- The application is a **prototype** focused on core solver functionality
- Examples data is pre-populated for demonstration
- Metrics generation is procedural for UI showcase purposes
- The DFS algorithm is optimized for grids up to 9x9

---

**Version**: 0.0.0  
**License**: As specified in project documentation
