from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend.api.dtos.PuzzleRequest import PuzzleRequest
from backend.api.dtos.ValidationResult import ValidationError


class ImportWarning(BaseModel):
    """A non-fatal issue from screenshot extraction the user should review.

    Distinct from ``ValidationError``: an error means the board is unusable, a warning
    means it was imported but a cell was read with low confidence or a marker was skipped.
    Extraction is probabilistic in a way JSON parsing is not, so the two are kept separate.
    """

    model_config = ConfigDict(populate_by_name=True)

    code: str
    message: str
    cell: list[int] | None = None


class ImportResult(BaseModel):
    """Outcome of POST /api/import (screenshot import).

    ``board`` is the extracted configuration in the same shape the editor already loads
    (a ``PuzzleRequest``), so the frontend can drop it straight into the grid. It is
    populated whenever extraction produced a board — even one that then failed semantic
    validation — so the user can see and correct it rather than starting over. ``valid``
    reflects ``InputValidator``; ``errors`` carries the semantic problems; ``warnings``
    carries recoverable extraction uncertainty.
    """

    model_config = ConfigDict(populate_by_name=True)

    board: PuzzleRequest | None = None
    valid: bool = False
    message: str = ""
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ImportWarning] = Field(default_factory=list)
