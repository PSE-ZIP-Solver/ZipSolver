"""§8.2.2 Contract Validation Tests — pytest + Pydantic schema validation.

Pure DTO tests: no TestClient, no mocks, no I/O. These assert the wire contract that
§5.5 publishes to the frontend, and they are the most durable file in this suite —
they should survive every backend implementation change.

When a test here fails, either the DTO changed or the design document did. One of the
two needs updating before the change ships.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from backend.api.dtos.ErrorResponse import ErrorCode, ErrorResponse
from backend.api.dtos.HealthStatus import HealthStatus
from backend.api.dtos.PuzzleRequest import PuzzleRequest, WallDTO
from backend.api.dtos.SolverResponse import SolverResponse
from backend.api.dtos.ValidationResult import ValidationError, ValidationResult
from backend.api.solver_dtos.SolverMetrics import SolverMetrics
from backend.api.solver_dtos.SolverStatus import SolverStatus

pytestmark = pytest.mark.contract


# ──────────────────────────────────────────────────────────────────────────────
# PuzzleRequest — §5.5.1
# ──────────────────────────────────────────────────────────────────────────────


class TestPuzzleRequest:
    def test_accepts_camel_case_wire_format(self):
        """camelCase is the published wire format and what the frontend sends."""
        request = PuzzleRequest.model_validate(
            {"boardSize": 6, "waypoints": [[0, 0], [5, 5]], "walls": []}
        )
        assert request.board_size == 6

    def test_accepts_snake_case_via_populate_by_name(self):
        """``populate_by_name=True`` lets backend code construct DTOs with Python-native
        field names without going through aliases."""
        request = PuzzleRequest.model_validate({"board_size": 6, "waypoints": [(0, 0)], "walls": []})
        assert request.board_size == 6

    def test_coordinates_are_coerced_to_tuples(self):
        """JSON arrays arrive as lists; the DTO normalises them to hashable tuples."""
        request = PuzzleRequest.model_validate({"boardSize": 6, "waypoints": [[1, 2]], "walls": []})
        assert request.waypoints == [(1, 2)]
        assert isinstance(request.waypoints[0], tuple)

    def test_walls_defaults_to_empty_list_when_omitted(self):
        request = PuzzleRequest.model_validate({"boardSize": 6, "waypoints": [[0, 0]]})
        assert request.walls == []

    def test_waypoint_order_is_preserved(self):
        """§5.2: list index defines visit order. Reordering would silently change the
        puzzle, so sequence stability is part of the contract."""
        ordered = [[0, 0], [3, 1], [1, 4], [5, 5]]
        request = PuzzleRequest.model_validate({"boardSize": 6, "waypoints": ordered, "walls": []})
        assert request.waypoints == [tuple(pair) for pair in ordered]

    def test_ignores_unknown_fields(self):
        """The reference ``board_configuration.json`` (§5.4.2) carries ``solutionPath``,
        which ``PuzzleRequest`` deliberately does not model. It must be dropped, not
        rejected, so example files import unchanged."""
        request = PuzzleRequest.model_validate(
            {
                "boardSize": 6,
                "waypoints": [[0, 0]],
                "walls": [],
                "solutionPath": [[0, 0], [0, 1]],
            }
        )
        assert not hasattr(request, "solutionPath")
        assert not hasattr(request, "solution_path")

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param({"waypoints": [[0, 0]], "walls": []}, id="missing-boardSize"),
            pytest.param({"boardSize": 6, "walls": []}, id="missing-waypoints"),
            pytest.param({"boardSize": "six", "waypoints": [[0, 0]]}, id="boardSize-not-int"),
            pytest.param({"boardSize": 6, "waypoints": "nope"}, id="waypoints-not-list"),
            pytest.param({"boardSize": 6, "waypoints": [[0]]}, id="coordinate-too-short"),
            pytest.param({"boardSize": 6, "waypoints": [[0, 1, 2]]}, id="coordinate-too-long"),
            pytest.param({"boardSize": 6, "waypoints": [["a", "b"]]}, id="coordinate-not-int"),
            pytest.param({"boardSize": None, "waypoints": [[0, 0]]}, id="boardSize-null"),
            pytest.param({"boardSize": 6, "waypoints": None}, id="waypoints-null"),
        ],
    )
    def test_rejects_malformed_shapes(self, payload):
        with pytest.raises(PydanticValidationError):
            PuzzleRequest.model_validate(payload)

    def test_board_size_is_not_range_constrained_at_schema_level(self):
        """§5.5.1 lists 6|7|8, but the constraint is enforced by ``InputValidator``, not
        the schema — so an out-of-range size yields 422 UNSUPPORTED_BOARD_SIZE rather
        than 400 MALFORMED_REQUEST. This test pins that division of responsibility."""
        assert PuzzleRequest.model_validate({"boardSize": 99, "waypoints": [[0, 0]]}).board_size == 99

    def test_negative_coordinates_pass_shape_validation(self):
        """Bounds are semantic, not structural — same division as board size."""
        assert PuzzleRequest.model_validate({"boardSize": 6, "waypoints": [[-1, -1]]}).waypoints == [(-1, -1)]


class TestWallDTO:
    def test_accepts_neighbor_aliases(self):
        wall = WallDTO.model_validate({"neighborA": [0, 0], "neighborB": [1, 0]})
        assert wall.neighbor_a == (0, 0)
        assert wall.neighbor_b == (1, 0)

    def test_serialises_back_to_camel_case(self):
        wall = WallDTO.model_validate({"neighborA": [0, 0], "neighborB": [1, 0]})
        assert set(wall.model_dump(by_alias=True)) == {"neighborA", "neighborB"}

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param({"neighborA": [0, 0]}, id="missing-neighborB"),
            pytest.param({"neighborB": [0, 0]}, id="missing-neighborA"),
            pytest.param({"neighborA": [0, 0], "neighborB": "x"}, id="neighbor-not-coordinate"),
        ],
    )
    def test_rejects_malformed_walls(self, payload):
        with pytest.raises(PydanticValidationError):
            WallDTO.model_validate(payload)

    def test_adjacency_is_not_enforced_at_schema_level(self):
        """Diagonal / non-adjacent walls are semantic errors (422 INVALID_WALLS), not
        shape errors (400)."""
        assert WallDTO.model_validate({"neighborA": [0, 0], "neighborB": [5, 5]}).neighbor_b == (5, 5)


# ──────────────────────────────────────────────────────────────────────────────
# SolverResponse / SolverMetrics / SolverStatus — §5.5.2, §5.5.3
# ──────────────────────────────────────────────────────────────────────────────


class TestSolverResponse:
    def test_serialises_every_documented_field_in_camel_case(self):
        response = SolverResponse(
            status=SolverStatus.SOLVED,
            success=True,
            solutionPath=[(0, 0), (0, 1)],
            solverUsed="RL",
            message="Solved by RL agent.",
            metrics=SolverMetrics(runtimeMs=142, steps=36, attempts=1),
        )
        assert set(response.model_dump(by_alias=True)) == {
            "status",
            "success",
            "solutionPath",
            "solverUsed",
            "message",
            "metrics",
        }

    def test_status_serialises_as_bare_string(self):
        """``SolverStatus`` subclasses ``str`` so it emits ``"SOLVED"``, not
        ``{"value": "SOLVED"}`` — the frontend's ``SolverStatus`` union depends on it."""
        response = SolverResponse(
            status=SolverStatus.SOLVED, success=True, metrics=SolverMetrics(runtimeMs=0, steps=0, attempts=1)
        )
        assert response.model_dump(mode="json")["status"] == "SOLVED"

    def test_optional_fields_default_to_none_and_empty(self):
        response = SolverResponse(
            status=SolverStatus.FAILED,
            success=False,
            metrics=SolverMetrics(runtimeMs=0, steps=0, attempts=1),
        )
        assert response.solution_path is None
        assert response.solver_used is None
        assert response.message == ""

    def test_status_and_metrics_are_required(self):
        with pytest.raises(PydanticValidationError):
            SolverResponse.model_validate(
                {"success": True, "metrics": {"runtimeMs": 0, "steps": 0, "attempts": 1}}
            )
        with pytest.raises(PydanticValidationError):
            SolverResponse.model_validate({"status": "SOLVED", "success": True})

    def test_rejects_unknown_status_value(self):
        with pytest.raises(PydanticValidationError):
            SolverResponse.model_validate(
                {
                    "status": "PARTIALLY_SOLVED",
                    "success": False,
                    "metrics": {"runtimeMs": 0, "steps": 0, "attempts": 1},
                }
            )

    def test_round_trips_through_json(self):
        original = SolverResponse(
            status=SolverStatus.SOLVED,
            success=True,
            solutionPath=[(0, 0), (1, 1)],
            solverUsed="DFS",
            message="ok",
            metrics=SolverMetrics(runtimeMs=5, steps=2, attempts=1),
        )
        assert SolverResponse(**original.model_dump(by_alias=True)) == original

    def test_solver_used_permits_null(self):
        """Backend models ``solverUsed`` as nullable for the not-attempted case. The
        frontend currently types it as a non-nullable ``"RL" | "DFS"`` union — a known
        contract delta tracked against the frontend owner."""
        response = SolverResponse(
            status=SolverStatus.FAILED,
            success=False,
            solverUsed=None,
            metrics=SolverMetrics(runtimeMs=0, steps=0, attempts=1),
        )
        assert response.model_dump(by_alias=True)["solverUsed"] is None


class TestSolverMetrics:
    def test_serialises_runtime_in_camel_case(self):
        metrics = SolverMetrics(runtimeMs=142, steps=36, attempts=1)
        assert metrics.model_dump(by_alias=True) == {
            "runtimeMs": 142,
            "steps": 36,
            "attempts": 1,
        }

    def test_all_three_fields_are_required(self):
        """§5.5.3 defines exactly three fields. The frontend's ``SolverMetrics``
        interface requires all three, so none may become optional without a
        coordinated change."""
        for omitted in ("runtimeMs", "steps", "attempts"):
            payload = {"runtimeMs": 1, "steps": 1, "attempts": 1}
            payload.pop(omitted)
            with pytest.raises(PydanticValidationError):
                SolverMetrics(**payload)

    @pytest.mark.parametrize(
        ("field", "value"),
        [("runtimeMs", -1), ("steps", -1), ("attempts", 0), ("attempts", -1)],
    )
    def test_rejects_out_of_range_values(self, field, value):
        """``runtimeMs``/``steps`` are ``ge=0``; ``attempts`` is ``ge=1`` — a solve that
        ran at all made at least one attempt."""
        payload = {"runtimeMs": 0, "steps": 0, "attempts": 1, field: value}
        with pytest.raises(PydanticValidationError):
            SolverMetrics(**payload)

    def test_accepts_boundary_values(self):
        assert SolverMetrics(runtimeMs=0, steps=0, attempts=1).attempts == 1


class TestSolverStatus:
    def test_defines_exactly_the_four_documented_values(self):
        assert {member.value for member in SolverStatus} == {
            "SOLVED",
            "UNSOLVABLE",
            "TIMEOUT",
            "FAILED",
        }

    def test_compares_equal_to_plain_strings(self):
        """String inheritance keeps ``status == "SOLVED"`` working across the codebase."""
        assert SolverStatus.SOLVED == "SOLVED"


# ──────────────────────────────────────────────────────────────────────────────
# ValidationResult / ValidationError — §5.5.4
# ──────────────────────────────────────────────────────────────────────────────


class TestValidationResult:
    def test_valid_result_defaults_to_empty_errors(self):
        result = ValidationResult(valid=True)
        assert result.errors == []
        assert result.message == ""

    def test_valid_flag_is_required(self):
        with pytest.raises(PydanticValidationError):
            ValidationResult.model_validate({"message": "no flag"})

    def test_serialises_nested_errors_in_camel_case(self):
        result = ValidationResult(
            valid=False,
            message="Board configuration is invalid.",
            errors=[
                ValidationError(
                    errorCode="INVALID_WAYPOINTS",
                    affectedField="waypoints",
                    message="Duplicate waypoint at [0, 0].",
                )
            ],
        )
        assert result.model_dump(by_alias=True)["errors"][0] == {
            "errorCode": "INVALID_WAYPOINTS",
            "affectedField": "waypoints",
            "message": "Duplicate waypoint at [0, 0].",
        }

    def test_round_trips_through_json(self):
        original = ValidationResult(
            valid=False,
            message="bad",
            errors=[ValidationError(errorCode="INVALID_WALLS", message="non-adjacent")],
        )
        assert ValidationResult(**original.model_dump(by_alias=True)) == original


class TestValidationErrorModel:
    def test_affected_field_is_optional(self):
        """Board-level problems have no single offending field."""
        error = ValidationError(errorCode="UNSUPPORTED_BOARD_SIZE", message="size 99")
        assert error.affected_field is None

    def test_error_code_and_message_are_required(self):
        with pytest.raises(PydanticValidationError):
            ValidationError.model_validate({"message": "orphan message"})
        with pytest.raises(PydanticValidationError):
            ValidationError.model_validate({"errorCode": "INVALID_WALLS"})

    def test_error_code_is_a_free_string_not_an_enum(self):
        """``ValidationError.errorCode`` is intentionally open: ``InputValidator`` and
        ``SolutionValidator`` emit domain codes (``PATH_EMPTY``, ``RULE_VIOLATION``)
        beyond the HTTP-level ``ErrorCode`` taxonomy."""
        assert ValidationError(errorCode="RULE_VIOLATION", message="x").error_code == (
            "RULE_VIOLATION"
        )


# ──────────────────────────────────────────────────────────────────────────────
# ErrorResponse — §5.5.5
# ──────────────────────────────────────────────────────────────────────────────


class TestErrorResponse:
    def test_defines_exactly_the_five_taxonomy_codes(self):
        assert {member.value for member in ErrorCode} == {
            "MALFORMED_REQUEST",
            "UNSUPPORTED_BOARD_SIZE",
            "INVALID_WAYPOINTS",
            "INVALID_WALLS",
            "INTERNAL_ERROR",
        }

    def test_solver_statuses_are_absent_from_the_error_taxonomy(self):
        """§5.5.5 is explicit: UNSOLVABLE / TIMEOUT / FAILED are 200 outcomes and must
        never appear as error codes."""
        codes = {member.value for member in ErrorCode}
        assert codes.isdisjoint({"UNSOLVABLE", "TIMEOUT", "FAILED", "SOLVED"})

    def test_serialises_every_documented_field(self):
        response = ErrorResponse(
            status=422,
            code=ErrorCode.INVALID_WAYPOINTS,
            message="Duplicate waypoint.",
            details=None,
            timestamp="2026-06-07T10:15:30+00:00",
        )
        assert set(response.model_dump(by_alias=True)) == {
            "status",
            "code",
            "message",
            "details",
            "timestamp",
        }

    def test_code_serialises_as_bare_string(self):
        response = ErrorResponse(
            status=400,
            code=ErrorCode.MALFORMED_REQUEST,
            message="bad",
            timestamp="2026-06-07T10:15:30+00:00",
        )
        assert response.model_dump(mode="json")["code"] == "MALFORMED_REQUEST"

    def test_details_default_to_none(self):
        response = ErrorResponse(
            status=500,
            code=ErrorCode.INTERNAL_ERROR,
            message="boom",
            timestamp="2026-06-07T10:15:30+00:00",
        )
        assert response.details is None

    def test_timestamp_is_required(self):
        with pytest.raises(PydanticValidationError):
            ErrorResponse.model_validate(
                {"status": 400, "code": "MALFORMED_REQUEST", "message": "bad"}
            )

    def test_rejects_codes_outside_the_taxonomy(self):
        with pytest.raises(PydanticValidationError):
            ErrorResponse.model_validate(
                {
                    "status": 418,
                    "code": "TEAPOT",
                    "message": "nope",
                    "timestamp": "2026-06-07T10:15:30+00:00",
                }
            )


# ──────────────────────────────────────────────────────────────────────────────
# HealthStatus — §3.2.1
# ──────────────────────────────────────────────────────────────────────────────


class TestHealthStatus:
    def test_status_defaults_to_ok(self):
        assert HealthStatus(apiVersion="1.0.0").status == "ok"

    def test_model_loaded_is_optional(self):
        assert HealthStatus(apiVersion="1.0.0").model_loaded is None

    def test_serialises_in_camel_case(self):
        health = HealthStatus(apiVersion="1.0.0", modelLoaded=True)
        assert health.model_dump(by_alias=True) == {
            "status": "ok",
            "apiVersion": "1.0.0",
            "modelLoaded": True,
        }

    def test_api_version_is_required(self):
        with pytest.raises(PydanticValidationError):
            HealthStatus.model_validate({})


# ──────────────────────────────────────────────────────────────────────────────
# Cross-cutting: internal domain model ↔ API DTO consistency
# ──────────────────────────────────────────────────────────────────────────────


class TestInternalToApiConsistency:
    """§8.2.2: "ensuring consistency between internal domain models and API-level data
    structures". These guard the seams where the two representations meet."""

    def test_api_and_internal_solver_status_agree_on_values(self):
        """Two ``SolverStatus`` enums exist — the API DTO one and the internal
        ``solving_process`` one. Their value sets must stay identical or the adapter
        between them silently drops states."""
        from backend.solving_process.solver_status import SolverStatus as InternalStatus

        assert {m.value for m in SolverStatus} == {m.value for m in InternalStatus}

    def test_api_metrics_field_names_match_internal_metrics(self):
        """The internal ``SolverMetrics`` exposes ``getRuntimeMs`` / ``getSteps`` /
        ``getAttempts``; the DTO must offer a field for each."""
        from backend.solving_process.solver_metrics import SolverMetrics as InternalMetrics

        internal = InternalMetrics(runtimeMs=1, steps=2, attempts=3)
        dto = SolverMetrics(
            runtimeMs=internal.getRuntimeMs,
            steps=internal.getSteps,
            attempts=internal.getAttempts,
        )
        assert dto.model_dump(by_alias=True) == {"runtimeMs": 1, "steps": 2, "attempts": 3}

    def test_solution_path_positions_map_onto_coordinate_pairs(self):
        """The wire format is ``[x, y]``; the domain object is ``Position``. This is the
        exact conversion ``BackendAPI.solvePuzzle`` performs."""
        from backend.puzzle_logic import Position
        from backend.solution_path import SolutionPath

        path = SolutionPath()
        for x, y in [(0, 0), (1, 0), (1, 1)]:
            path.add(Position(x, y))

        assert [(p.getX, p.getY) for p in path.getPostions] == [(0, 0), (1, 0), (1, 1)]