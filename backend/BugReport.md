# JsonInterpreter — Bug Report

`backend/input_validation/json_interpreter.py`

Five verified bugs. The file does not run in its current state — a syntactically
perfect board returns `False` from `verifySyntax` and `buildBoard` raises. The
validation *rules* are correct; the mechanics and the API contract are not.

Each item below was reproduced by running the code.

---

## Bug 1 — `@staticmethod` + `self` parameter (fatal)

Every method is decorated `@staticmethod` but still declares `self` as its first
parameter. A staticmethod receives no implicit `self`, so the first argument you pass
lands in the `self` slot.

```python
@staticmethod
def verifySyntax(self, file): ...
```

```
>>> ji.verifySyntax(board)
TypeError: verifySyntax() missing 1 required positional argument: 'file'
```

Fix: drop `@staticmethod` from every method that uses `self`. They are instance
methods.

## Bug 2 — internal `self.X()` calls collapse (fatal)

Because of Bug 1, every internal call like `self._load(file)` passes `file` into the
callee's `self` slot and leaves the real argument missing → `TypeError`, swallowed by
the bare `except` → `False`. A flawless board returns `False`.

```
>>> JsonInterpreter.verifySyntax(ji, {"boardSize":6,"waypoints":[[0,0],[1,1]],"walls":[],"solutionPath":[]})
False        # should be True
```

Fixed automatically once Bug 1 is fixed.

## Bug 3 — off-by-one board bounds (fatal for edge cells)

```python
return 0 <= x < board_size-1 and 0 <= y < board_size-1
```

`board_size-1` excludes the last row and column. On a 6x6 board, valid coordinates are
0..5, but this accepts only 0..4 — `[5,5]` is wrongly rejected.

```
>>> # size 6, corner waypoint [5,5]
0 <= 5 < 5   ->   False   # rejected, but [5,5] is a legal cell
```

Fix: `0 <= x < board_size and 0 <= y < board_size`.

## Bug 4 — wrong contract with the API

`BackendAPI` injects the interpreter through `JsonInterpreterProtocol`:

```python
def buildBoard(self, request: PuzzleRequest) -> Board
```

The file's `buildBoard(file: str|dict|filehandle)` expects raw JSON. A `PuzzleRequest`
is a Pydantic model, not a dict, so `_load` would `TypeError` on it. The interpreter
could not be wired into `/api/solve` or `/api/import` as written.

Fix: `buildBoard` accepts the DTO (reads `.board_size` / `.waypoints` / `.walls`) and
still supports raw JSON for the import-file workflow.

## Bug 5 — `solutionPath` handling rejects real inputs

`verifySyntax` requires a `solutionPath` key that must be an **empty list**. But:

- the API's `PuzzleRequest` has no `solutionPath` field at all, and
- the reference `board_configuration.json` ships with `solutionPath` fully populated
  (25 coordinates).

So the interpreter rejected the exact file it documents, and every request from the API.

Fix: the DTO path ignores `solutionPath` entirely (the API never sends it). The raw-JSON
`verifySyntax` path keeps the strict "present and empty" rule for the import-file format —
if that format should instead allow a populated `solutionPath`, relax the check.

---

## What was kept

The validation logic is sound and unchanged in intent: board size ∈ {6,7,8}, waypoint
count bounds and uniqueness, wall adjacency via `abs(dx)+abs(dy)==1`, unordered wall
dedup via `frozenset`. One small hardening added: `bool` is a subclass of `int`, so
`_validate_board_size` and `_is_valid_point` now reject `True`/`False` explicitly.

## Verification after fix

```
buildBoard(PuzzleRequest)         -> Board (size, waypoints, walls populated)
verifySyntax(perfect board)       -> True
corner cell [5,5] on size 6       -> accepted
/api/solve with real interpreter  -> 200 SOLVED
all 8 rejection rules             -> False as expected
```

Also added `backend/input_validation/__init__.py` (the package had none, so
`from backend.input_validation import JsonInterpreter` failed).