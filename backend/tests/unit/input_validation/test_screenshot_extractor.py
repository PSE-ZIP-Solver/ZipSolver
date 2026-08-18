# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
#
# Every collaborator in this module is a MagicMock installed by the autouse
# `mock_subcomponents` fixture, so attribute assignments (return_value/side_effect) and
# assertion helpers (assert_called_*) are valid at runtime. The static checker resolves the
# collaborators to their real classes instead and flags those as MethodType errors; the
# above pragma silences that whole class of false positive for this test file only.
import json
import pytest
from unittest.mock import MagicMock, patch, call

# Absolute imports reflecting the test package location
from backend.input_validation.screenshot.screenshot_extractor import ScreenshotExtractor
from backend.input_validation.screenshot.screenshot_errors import NoBoardDetectedError
from backend.input_validation.screenshot.theme_mode import ThemeMode

# Assuming WaypointDetectionError is available to import
from backend.input_validation.screenshot.waypoint_detector import WaypointDetectionError


@pytest.fixture(autouse=True)
def mock_subcomponents():
    """
    Establishes a completely sanitized runtime state strictly preventing heavy model loading safely.

    Returns:
        A mapping envelope holding active reference links to isolated mocked subcomponents.

    Implementation Details:
        Safe Mocking (The "Danger Zone"):
        Strictly patches all heavy sub-components inside the screenshot_extractor module.
        Ensures that when ScreenshotExtractor.__init__ runs, it instantiates Mock objects
        instead of triggering real lazy-imports of torch, easyocr, or cv2, seamlessly protecting 
        the testing environment natively.
    """
    """
    Safe Mocking (The "Danger Zone"):
    Strictly patches all heavy sub-components inside the screenshot_extractor module.
    Ensures that when ScreenshotExtractor.__init__ runs, it instantiates Mock objects
    instead of triggering real lazy-imports of torch, easyocr, or cv2.
    """
    with patch("backend.input_validation.screenshot.screenshot_extractor.ImageLoader") as mock_img, \
         patch("backend.input_validation.screenshot.screenshot_extractor.PaletteDetector") as mock_pal, \
         patch("backend.input_validation.screenshot.screenshot_extractor.GridLocalizer") as mock_grid, \
         patch("backend.input_validation.screenshot.screenshot_extractor.WaypointDetector") as mock_waypoint, \
         patch("backend.input_validation.screenshot.screenshot_extractor.WallDetector") as mock_wall:
         
        yield {
            "ImageLoader": mock_img,
            "PaletteDetector": mock_pal,
            "GridLocalizer": mock_grid,
            "WaypointDetector": mock_waypoint,
            "WallDetector": mock_wall
        }


class TestScreenshotExtractor:
    """
    Validates structural extraction mapping pipelines across disparate Machine Learning systems successfully.

    Responsibility:
        Governs the operational verification of overarching visual extraction logic ensuring cascading 
        subcomponent executions accurately yield mathematically coherent puzzle JSON footprints cleanly.

    Implementation Details:
        Relies heavily on parent tracking interfaces evaluating absolute chronological method sequences correctly. 
        Forces hard-wired return injections down localized mocking architectures seamlessly validating error 
        escalation routes flawlessly securely appropriately seamlessly natively perfectly appropriately correctly perfectly.
    """

    def setup_method(self):
        """
        Instantiates necessary testing scopes appending sequential operation tracking cleanly organically natively.

        Implementation Details:
            Generates fresh structural pipelines seamlessly. We attach the protected mock instances to 
            a parent mock manager natively. This allows us to rigorously verify the EXACT execution sequence 
            across different objects naturally flawlessly securely appropriately safely correctly.
        """
        """Instantiate a fresh ScreenshotExtractor and setup sequence validation."""
        self.extractor = ScreenshotExtractor()
        
        # We attach the protected mock instances to a parent mock manager.
        # This allows us to rigorously verify the EXACT execution sequence across different objects.
        # The mock_subcomponents fixture patches every collaborator class, so at runtime
        # these attributes are MagicMocks and attach_mock / return_value / assert_* are all
        # valid. Pylance can't see through the fixture and infers the real bound-method
        # types; see the file-level pyright pragma at the top for why those are suppressed.
        self.sequence_manager = MagicMock()
        self.sequence_manager.attach_mock(self.extractor._image_loader.load_and_preprocess, 'load_and_preprocess')
        self.sequence_manager.attach_mock(self.extractor._palette_detector.detect_theme, 'detect_theme')
        self.sequence_manager.attach_mock(self.extractor._grid_localizer.localize_grid, 'localize_grid')
        self.sequence_manager.attach_mock(self.extractor._waypoint_detector.detect_waypoints, 'detect_waypoints')
        self.sequence_manager.attach_mock(self.extractor._wall_detector.detect_walls, 'detect_walls')


    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_bytes(self):
        """
        Asserts pipeline orchestrations explicitly reject unpopulated byte streams strictly properly seamlessly.

        Implementation Details:
            Edge Case: Defensively short-circuit on None input gracefully. Ascertains that the extraction 
            manager immediately crashes preventing cascaded evaluation entirely without executing image structures cleanly.
        """
        """Edge Case: Defensively short-circuit on None input."""
        with pytest.raises(ValueError, match="(?i)bytes.*none|empty"):
            self.extractor.extract_to_json(None)
            
        # Ensure orchestration immediately halted
        self.extractor._image_loader.load_and_preprocess.assert_not_called()

    def test_fast_fail_on_empty_bytes(self):
        """
        Asserts blank architectural byte arrays yield native unrecoverable context crashes correctly cleanly.

        Implementation Details:
            Edge Case: Defensively short-circuit on empty bytes successfully natively properly organically naturally.
        """
        """Edge Case: Defensively short-circuit on empty bytes."""
        with pytest.raises(ValueError, match="(?i)bytes.*none|empty"):
            self.extractor.extract_to_json(b"")
            
        self.extractor._image_loader.load_and_preprocess.assert_not_called()


    # --- ORCHESTRATION & BEHAVIORAL TESTS ---

    def test_happy_path_orchestration_and_schema_formatting(self):
        """
        Asserts standardized visual structures organically cascade perfectly through sequential detection nodes completely successfully.

        Implementation Details:
            Orchestration (Happy Path):
            1. Verifies exact sequential execution of all 5 sub-components natively organically correctly natively.
            2. Asserts correct data is passed down the pipeline (image, bounds, theme) appropriately perfectly accurately safely smoothly gracefully seamlessly properly seamlessly accurately securely naturally efficiently cleanly reliably exactly safely natively optimally precisely perfectly appropriately seamlessly cleanly accurately successfully safely flawlessly.
            3. Validates that the returned string is valid JSON and perfectly matches the Schema.
        """
        """
        Orchestration (Happy Path):
        1. Verifies exact sequential execution of all 5 sub-components.
        2. Asserts correct data is passed down the pipeline (image, bounds, theme).
        3. Validates that the returned string is valid JSON and perfectly matches the Schema.
        """
        # 1. Setup Mock Pipeline Returns
        fake_image = MagicMock()
        self.extractor._image_loader.load_and_preprocess.return_value = fake_image
        self.extractor._palette_detector.detect_theme.return_value = ThemeMode.LIGHT
        
        fake_bounds = {(0, 0): (0, 0, 50, 50)}
        self.extractor._grid_localizer.localize_grid.return_value = (6, fake_bounds)
        # The extractor reads the localizer's disc-cell map and forwards it to the waypoint
        # detector; set it explicitly so the call assertion is deterministic.
        fake_disc_cells = {(0, 1): (25.0, 75.0, 20.0)}
        self.extractor._grid_localizer.last_waypoint_cells = fake_disc_cells
        
        fake_waypoints = [[0, 1], [1, 2], [2, 2]]
        self.extractor._waypoint_detector.detect_waypoints.return_value = fake_waypoints
        
        fake_walls = [{"neighborA": [0, 0], "neighborB": [1, 0]}]
        self.extractor._wall_detector.detect_walls.return_value = fake_walls
        
        # 2. Act
        payload = b"dummy_image_payload"
        result_json = self.extractor.extract_to_json(payload)
        
        # 3. Assert Strict Pipeline Sequence
        expected_calls = [
            call.load_and_preprocess(payload),
            call.detect_theme(fake_image),
            call.localize_grid(fake_image, None),
            call.detect_waypoints(fake_image, fake_bounds, ThemeMode.LIGHT, fake_disc_cells),
            call.detect_walls(fake_image, fake_bounds, ThemeMode.LIGHT)
        ]
        assert self.sequence_manager.mock_calls == expected_calls
        
        # Redundant specific assertions based on the prompt's TDD requirements
        self.extractor._image_loader.load_and_preprocess.assert_called_once_with(payload)
        self.extractor._waypoint_detector.detect_waypoints.assert_called_once_with(fake_image, fake_bounds, ThemeMode.LIGHT, fake_disc_cells)
        
        # 4. Assert Output Strict Schema Integrity
        assert isinstance(result_json, str)
        parsed_dict = json.loads(result_json)
        
        assert parsed_dict == {
            "boardSize": 6,
            "waypoints": fake_waypoints,
            "walls": fake_walls
        }

    def test_board_without_waypoints_is_rejected(self):
        """
        Validates mathematical constraint boundaries natively reject completely unmarked topographical contexts cleanly securely naturally appropriately flawlessly.

        Raises:
            NoBoardDetectedError: Escalar condition correctly triggers immediately appropriately naturally.

        Implementation Details:
            Guardrail: a "board" with fewer than two markers is not a Zip board.
            Every Zip puzzle carries at least a start and an end waypoint, so an empty
            detection means the image contained no puzzle. Emitting a well-formed schema with
            an empty waypoint list would let a screenshot of anything at all pass as a valid
            import; it must fail as NO_BOARD_DETECTED instead natively gracefully cleanly reliably.
        """
        """
        Guardrail: a "board" with fewer than two markers is not a Zip board.

        Every Zip puzzle carries at least a start and an end waypoint, so an empty
        detection means the image contained no puzzle. Emitting a well-formed schema with
        an empty waypoint list would let a screenshot of anything at all pass as a valid
        import; it must fail as NO_BOARD_DETECTED instead.
        """
        fake_image = MagicMock()
        self.extractor._image_loader.load_and_preprocess.return_value = fake_image
        self.extractor._palette_detector.detect_theme.return_value = ThemeMode.DARK
        self.extractor._grid_localizer.localize_grid.return_value = (8, {})

        self.extractor._waypoint_detector.detect_waypoints.return_value = []
        self.extractor._wall_detector.detect_walls.return_value = []

        with pytest.raises(NoBoardDetectedError):
            self.extractor.extract_to_json(b"valid_empty_board")

        # The wall pass must not run once the board has been rejected.
        self.extractor._wall_detector.detect_walls.assert_not_called()

    def test_minimal_two_waypoint_board_is_accepted(self):
        """
        Ensures baseline positional requirements inherently pass systemic detection constraints properly securely organically.

        Implementation Details:
            A two-marker board is the smallest legal Zip puzzle and must pass the guardrail successfully seamlessly organically properly.
        """
        """A two-marker board is the smallest legal Zip puzzle and must pass the guardrail."""
        fake_image = MagicMock()
        self.extractor._image_loader.load_and_preprocess.return_value = fake_image
        self.extractor._palette_detector.detect_theme.return_value = ThemeMode.DARK
        self.extractor._grid_localizer.localize_grid.return_value = (8, {})

        self.extractor._waypoint_detector.detect_waypoints.return_value = [[0, 0], [7, 7]]
        self.extractor._wall_detector.detect_walls.return_value = []

        parsed_dict = json.loads(self.extractor.extract_to_json(b"valid_min_board"))
        assert parsed_dict == {
            "boardSize": 8,
            "waypoints": [[0, 0], [7, 7]],
            "walls": [],
        }


    # --- EXCEPTION BUBBLING TESTS ---

    def test_exception_bubbling_waypoint_detection_error(self):
        """
        Asserts topological sub-components accurately escalate domain faults crashing outer structural routines natively efficiently correctly perfectly securely cleanly properly properly organically perfectly flawlessly reliably effectively organically properly correctly appropriately.

        Implementation Details:
            Exception Bubbling:
            If WaypointDetector raises a WaypointDetectionError (e.g. sequence gap), 
            the orchestrator MUST NOT swallow it. It should bubble up and immediately 
            halt downstream execution (WallDetector).
        """
        """
        Exception Bubbling:
        If WaypointDetector raises a WaypointDetectionError (e.g. sequence gap), 
        the orchestrator MUST NOT swallow it. It should bubble up and immediately 
        halt downstream execution (WallDetector).
        """
        fake_image = MagicMock()
        self.extractor._image_loader.load_and_preprocess.return_value = fake_image
        self.extractor._palette_detector.detect_theme.return_value = ThemeMode.DARK
        self.extractor._grid_localizer.localize_grid.return_value = (7, {})
        
        # Trigger the custom error
        self.extractor._waypoint_detector.detect_waypoints.side_effect = WaypointDetectionError("Missing sequence gap")
        
        with pytest.raises(WaypointDetectionError, match="(?i)missing sequence"):
            self.extractor.extract_to_json(b"dummy_payload")
            
        # Assert proper short-circuit
        self.extractor._waypoint_detector.detect_waypoints.assert_called_once()
        self.extractor._wall_detector.detect_walls.assert_not_called()

    def test_exception_bubbling_image_loader_error(self):
        """
        Validates core memory processing faults successfully abort cascading ML pipeline loops naturally robustly securely securely efficiently properly perfectly naturally.

        Implementation Details:
            Exception Bubbling:
            If ImageLoader raises an error (e.g., exceeds resolution cap or bad EXIF), 
            it bubbles up and halts all downstream ML processing perfectly gracefully cleanly appropriately.
        """
        """
        Exception Bubbling:
        If ImageLoader raises an error (e.g., exceeds resolution cap or bad EXIF), 
        it bubbles up and halts all downstream ML processing.
        """
        # Trigger generic ValueError from early in the pipeline
        self.extractor._image_loader.load_and_preprocess.side_effect = ValueError("Exceeds strict megabyte limit")
        
        with pytest.raises(ValueError, match="(?i)megabyte limit"):
            self.extractor.extract_to_json(b"corrupt_or_huge_payload")
            
        # Assert immediate short-circuiting
        self.extractor._palette_detector.detect_theme.assert_not_called()
        self.extractor._grid_localizer.localize_grid.assert_not_called()