import sys
import time
import pickle
import traceback
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, List, Optional, Tuple

# Solver and data model imports
from backend.solving_process.algorithmic_solver import AlgorithmicSolver
from backend.solving_process.solver_status import SolverStatus
from backend.solving_process.solver_result import SolverResult

from backend.solution_path import SolutionPath
from backend.puzzle_logic.board import Board
from backend.puzzle_logic.data_models import Position, Waypoint


RELATIVE_FILE_PATH = "offline_training/evaluation_boards/7x7(final_sets)/7x7-final-eval-set3-dense-25to36walls-32to47wp-10000boards.pkl"


# ----------------------------------------------------------------------
# 0. Robust Attribute Extractor & Status Matcher
# ----------------------------------------------------------------------
def extract_field(obj: Any, *field_names: str, default: Any = None) -> Any:
    """Safely retrieves fields, properties, getter methods, or private attributes."""
    if obj is None:
        return default

    if isinstance(obj, dict):
        for name in field_names:
            if name in obj:
                return obj[name]

    candidates = []
    for name in field_names:
        cap = name[0].upper() + name[1:] if name else ""
        candidates.extend([
            name,
            f"get{cap}",
            f"get_{name}",
            f"_{name}",
            f"_{cap}",
        ])

    for attr in candidates:
        if hasattr(obj, attr):
            try:
                val = getattr(obj, attr)
                if callable(val) and not isinstance(val, type):
                    return val()
                return val
            except Exception:
                continue

    return default


def match_status(status_obj: Any, target_enum: SolverStatus) -> bool:
    """
    Robustly compares status regardless of whether it is an Enum,
    a string, or an integer representation.
    """
    if status_obj is None:
        return False
    if status_obj == target_enum:
        return True

    target_name = getattr(target_enum, "name", str(target_enum)).upper()

    # Enum or object with .name / .value
    obj_name = getattr(status_obj, "name", None)
    if obj_name and str(obj_name).upper() == target_name:
        return True

    obj_val = getattr(status_obj, "value", None)
    if obj_val and str(obj_val).upper() == target_name:
        return True

    # Raw string comparison
    if str(status_obj).upper() in (target_name, f"SOLVERSTATUS.{target_name}"):
        return True

    return False


# ----------------------------------------------------------------------
# 1. Independent Path Validator
# ----------------------------------------------------------------------
def extract_positions(path: Optional[SolutionPath]) -> List[Position]:
    if path is None:
        return []
    if isinstance(path, (list, tuple)):
        return list(path)

    for attr in ["getPositions", "get_positions", "positions", "_positions", "getPath", "get_path", "path", "_path"]:
        if hasattr(path, attr):
            val = getattr(path, attr)
            res = val() if callable(val) and not isinstance(val, type) else val
            if isinstance(res, (list, tuple)):
                return list(res)
    try:
        return list(path)
    except TypeError:
        pass
    raise AttributeError("Could not extract positions from SolutionPath instance.")


def _pos_coord(pos: Position) -> Tuple[int, int]:
    x = extract_field(pos, "x", "getX", default=0)
    y = extract_field(pos, "y", "getY", default=0)
    return (x, y)


def _wp_order(wp: Waypoint) -> int:
    return extract_field(wp, "order", "getOrder", default=0)


def _wp_pos(wp: Waypoint) -> Position:
    return extract_field(wp, "position", "getPosition")


def is_valid_solution(board: Board, path: Optional[SolutionPath]) -> Tuple[bool, str]:
    if path is None:
        return False, "Path is None"

    positions = extract_positions(path)
    expected_cells = board.getCellCount() if callable(board.getCellCount) else board.getCellCount

    if len(positions) != expected_cells:
        return False, f"Path length ({len(positions)}) != total cells ({expected_cells})"

    seen = set()
    for pos in positions:
        coord = _pos_coord(pos)
        if coord in seen:
            return False, f"Duplicate cell visited: {coord}"
        seen.add(coord)

    for i in range(len(positions) - 1):
        p1, p2 = positions[i], positions[i + 1]
        c1, c2 = _pos_coord(p1), _pos_coord(p2)
        dist = abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])
        if dist != 1:
            return False, f"Non-adjacent step between {c1} and {c2}"
        if not board.isInside(p2):
            return False, f"Position {c2} is outside board boundaries"
        if board.hasWallBetween(p1, p2):
            return False, f"Wall collision between {c1} and {c2}"

    raw_wps = board.getWaypoints() if callable(board.getWaypoints) else board.getWaypoints
    waypoints = sorted(raw_wps, key=_wp_order)
    wp_pos_to_order = {_pos_coord(_wp_pos(wp)): _wp_order(wp) for wp in waypoints}

    visited_orders = []
    for pos in positions:
        coord = _pos_coord(pos)
        if coord in wp_pos_to_order:
            visited_orders.append(wp_pos_to_order[coord])

    expected_orders = [_wp_order(wp) for wp in waypoints]
    if visited_orders != expected_orders:
        return False, f"Waypoints visited in wrong order: {visited_orders} != {expected_orders}"

    return True, "Valid"


# ----------------------------------------------------------------------
# 2. Worker Execution
# ----------------------------------------------------------------------
@dataclass
class BoardEvaluationResult:
    index: int
    raw_status: Any
    is_solved: bool
    is_timeout: bool
    is_unsolvable: bool
    is_valid: bool
    has_exception: bool
    runtime_ms: int
    steps: int
    error_reason: str = ""


def _evaluate_single_board(args: Tuple[int, Board, int]) -> BoardEvaluationResult:
    index, board, timeout_ms = args
    solver = AlgorithmicSolver(timeout=timeout_ms)

    try:
        result: SolverResult = solver.solve(board)
    except Exception as e:
        tb = traceback.format_exc()
        return BoardEvaluationResult(
            index=index,
            raw_status="EXCEPTION",
            is_solved=False,
            is_timeout=False,
            is_unsolvable=False,
            is_valid=False,
            has_exception=True,
            runtime_ms=0,
            steps=0,
            error_reason=f"Exception during solve: {e}\n{tb}",
        )

    status = extract_field(result, "status")
    path = extract_field(result, "path")
    message = extract_field(result, "message", default="")
    metrics = extract_field(result, "metrics")

    runtime_ms = extract_field(metrics, "runtimeMs", "runtime_ms", default=0) or 0
    steps = extract_field(metrics, "steps", default=0) or 0

    is_solved = match_status(status, SolverStatus.SOLVED)
    is_timeout = match_status(status, SolverStatus.TIMEOUT)
    is_unsolvable = match_status(status, SolverStatus.UNSOLVABLE)

    if is_solved:
        valid, reason = is_valid_solution(board, path)
        return BoardEvaluationResult(
            index=index,
            raw_status=status,
            is_solved=True,
            is_timeout=False,
            is_unsolvable=False,
            is_valid=valid,
            has_exception=False,
            runtime_ms=runtime_ms,
            steps=steps,
            error_reason=reason if not valid else "",
        )

    return BoardEvaluationResult(
        index=index,
        raw_status=status,
        is_solved=False,
        is_timeout=is_timeout,
        is_unsolvable=is_unsolvable,
        is_valid=False,
        has_exception=False,
        runtime_ms=runtime_ms,
        steps=steps,
        error_reason=message or f"Status received: {status}",
    )


# ----------------------------------------------------------------------
# 3. Evaluation Runner
# ----------------------------------------------------------------------
class EvaluationHarness:
    def __init__(self, evaluation_boards_path: Path, timeout_ms: int = 10000, milestone_interval: int = 1000):
        self.evaluation_boards_path = evaluation_boards_path
        self.timeout_ms = timeout_ms
        self.milestone_interval = milestone_interval

    def load_boards(self) -> List[Board]:
        with self.evaluation_boards_path.open("rb") as file:
            boards = pickle.load(file)

        if not isinstance(boards, list) or not boards:
            raise ValueError("The saved evaluation board file is empty or invalid.")

        print(f"Loaded {len(boards):,} evaluation boards from {self.evaluation_boards_path}")
        return boards  # Testing first 50 boards; change to `return boards` for all 10,000

    def _format_time(self, seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:d}h {m:02d}m {s:02d}s"
        return f"{m:02d}m {s:02d}s"

    def run_preflight_diagnostic(self, board: Board):
        """Runs a direct, synchronous single-board solve to verify the solver pipeline."""
        print("\n" + "=" * 65)
        print("🔍 RUNNING PRE-FLIGHT DIAGNOSTIC ON BOARD #0 (Single Process)")
        print("=" * 65)
        try:
            size = extract_field(board, "size", "getSize")
            cells = board.getCellCount() if callable(board.getCellCount) else board.getCellCount
            wps = board.getWaypoints() if callable(board.getWaypoints) else board.getWaypoints
            print(f"• Board Dimensions : {size}x{size} ({cells} cells)")
            print(f"• Waypoint Count   : {len(wps)}")

            solver = AlgorithmicSolver(timeout=self.timeout_ms)
            start = time.perf_counter()
            result: SolverResult = solver.solve(board)
            elapsed = (time.perf_counter() - start) * 1000

            print(f"• Raw Result Type  : {type(result)}")
            print(f"• Raw Result Dirs  : {[a for a in dir(result) if not a.startswith('__')]}")
            
            status = extract_field(result, "status")
            print(f"• Extracted Status : {status} (type: {type(status)})")

            path = extract_field(result, "path")
            print(f"• Extracted Path   : {'Present' if path is not None else 'None'}")

            if match_status(status, SolverStatus.SOLVED):
                valid, reason = is_valid_solution(board, path)
                print(f"• Solution Check   : {'✅ VALID' if valid else f'❌ INVALID ({reason})'}")
            elif match_status(status, SolverStatus.TIMEOUT):
                print(f"• Solver Result    : ⏱️ TIMEOUT ({elapsed:.1f}ms)")
            else:
                print(f"• Solver Result    : ❌ UNSOLVABLE ({elapsed:.1f}ms)")

        except Exception as e:
            print(f"❌ Pre-flight check crashed with exception:\n{traceback.format_exc()}")

        print("=" * 65 + "\n")

    def run(self, max_workers: Optional[int] = None):
        boards = self.load_boards()
        total_boards = len(boards)

        # Run pre-flight test on board 0
        if total_boards > 0:
            self.run_preflight_diagnostic(boards[0])

        effective_interval = min(self.milestone_interval, max(10, total_boards // 5)) if total_boards > 0 else 1

        print(f"Starting batch evaluation across CPU cores...")
        print(f"Timeout: {self.timeout_ms}ms per board | Total: {total_boards:,} boards")
        print(f"Reporting progress milestone every {effective_interval:,} boards.\n")

        tasks = [(i, board, self.timeout_ms) for i, board in enumerate(boards)]
        results: List[BoardEvaluationResult] = []

        start_time = time.perf_counter()
        solved_count = 0
        timeout_count = 0
        unsolvable_count = 0
        exception_count = 0

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_board = {executor.submit(_evaluate_single_board, task): task[0] for task in tasks}

            for count, future in enumerate(as_completed(future_to_board), 1):
                res = future.result()
                results.append(res)

                if res.is_solved and res.is_valid:
                    solved_count += 1
                elif res.is_timeout:
                    timeout_count += 1
                elif res.is_unsolvable:
                    unsolvable_count += 1
                elif res.has_exception:
                    exception_count += 1

                elapsed = time.perf_counter() - start_time
                rate = count / elapsed if elapsed > 0 else 0
                eta = (total_boards - count) / rate if rate > 0 else 0

                if count % effective_interval == 0:
                    sys.stdout.write("\r" + " " * 95 + "\r")
                    pct_solved_so_far = (solved_count / count) * 100
                    print(
                        f"📌 [Milestone {count:>6,}/{total_boards:,} ({(count/total_boards)*100:5.1f}%)] "
                        f"Solved: {solved_count:,} ({pct_solved_so_far:5.1f}%) | "
                        f"Timeouts: {timeout_count} | "
                        f"Unsolvable: {unsolvable_count} | "
                        f"Rate: {rate:5.1f} b/s | "
                        f"Elapsed: {self._format_time(elapsed)}"
                    )
                else:
                    bar_len = 25
                    filled = int(bar_len * count // total_boards)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    sys.stdout.write(
                        f"\r[{bar}] {count:,}/{total_boards:,} ({(count/total_boards)*100:5.1f}%) "
                        f"| {rate:.1f} b/s | ETA: {self._format_time(eta)}"
                    )
                    sys.stdout.flush()

        print("\n")
        self._print_report(results, time.perf_counter() - start_time)

    def _print_report(self, results: List[BoardEvaluationResult], total_time_sec: float):
        total = len(results)
        if total == 0:
            print("No results to display.")
            return

        solved_correct = sum(1 for r in results if r.is_solved and r.is_valid)
        solved_invalid = sum(1 for r in results if r.is_solved and not r.is_valid)
        timed_out = sum(1 for r in results if r.is_timeout)
        unsolvable = sum(1 for r in results if r.is_unsolvable)
        crashes = sum(1 for r in results if r.has_exception)
        unknown = total - (solved_correct + solved_invalid + timed_out + unsolvable + crashes)

        avg_runtime = sum(r.runtime_ms for r in results) / total
        avg_steps = sum(r.steps for r in results) / total

        print("=" * 65)
        print("                        FINAL REPORT                        ")
        print("=" * 65)
        print(f"Total Boards Tested   : {total:,}")
        print(f"Total Evaluation Time : {self._format_time(total_time_sec)} ({total / total_time_sec:.1f} boards/s)")
        print("-" * 65)
        print(f"✅ Solved & Verified   : {solved_correct:,} ({(solved_correct / total) * 100:.2f}%)")
        print(f"⏱️  Timed Out          : {timed_out:,} ({(timed_out / total) * 100:.2f}%)")
        print(f"❌ Declared Unsolvable: {unsolvable:,} ({(unsolvable / total) * 100:.2f}%)")
        if crashes > 0:
            print(f"💥 Crashes / Exceptions: {crashes:,} ({(crashes / total) * 100:.2f}%)")
        if unknown > 0:
            print(f"⚠️  Status Parse Failed : {unknown:,} ({(unknown / total) * 100:.2f}%)")
        if solved_invalid > 0:
            print(f"⚠️  Solved but INVALID  : {solved_invalid:,} ({(solved_invalid / total) * 100:.2f}%)")
        print("-" * 65)
        print(f"Average Runtime       : {avg_runtime:.2f} ms/board")
        print(f"Average Search Steps  : {avg_steps:.1f} steps/board")
        print("=" * 65)

        # Print failures and exceptions
        if crashes > 0:
            print("\nFirst Crash Traceback:")
            first_crash = next(r for r in results if r.has_exception)
            print(f"Board #{first_crash.index}: {first_crash.error_reason}")

        if unsolvable > 0:
            print("\nSample Unsolvable Boards:")
            for r in [res for res in results if res.is_unsolvable][:5]:
                print(f" - Board #{r.index}: Steps={r.steps}, Time={r.runtime_ms}ms, Reason='{r.error_reason}'")


# ----------------------------------------------------------------------
# 4. Entrypoint
# ----------------------------------------------------------------------
if __name__ == "__main__":
    pickle_path = Path(RELATIVE_FILE_PATH)

    
    # Increased timeout to 5000ms (5 seconds) to allow 8x8 boards sufficient search budget
    harness = EvaluationHarness(evaluation_boards_path=pickle_path, timeout_ms=5000, milestone_interval=1000)
    harness.run()