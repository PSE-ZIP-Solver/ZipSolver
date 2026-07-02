# 🧩 Queens Puzzle Platform – Frontend

This is the frontend package for our university project: a one-page web application that allows users to create, play, and upload custom puzzle configurations (via JSON) for LinkedIn's **Queens** (Zip) game. 

The backend powering this application is written in **Python**.

## 🚀 Tech Stack

* **Framework:** React (TypeScript)
* **Build Tool:** Vite
* **Linter:** Oxlint + `oxlint-tsgolint` (Type-aware)

---

## 🛠️ Getting Started

### 1. Installation
Navigate to this directory and install the dependencies:
Bash
npm install
### 2. Development Server
Start the local Vite development server:

Bash
npm run dev
### 3. Linting & Code Quality
We use Oxlint for lightning-fast code analysis. To manually scan the project for errors:

Bash
npx oxlint
💡 Tip: For live, real-time error highlighting in your editor, install the official Oxc extension in VS Code.

📂 Core Features & Scope
One-Page Architecture: Everything happens seamlessly in a single dashboard view.

Puzzle Creator: An interactive grid UI to design custom grid boundaries.

JSON Import/Export: Load or save puzzle designs instantly using a structured JSON schema.

(For full details on project architecture, algorithm design, and Python backend setup, please refer to the main repository README at the root level.)