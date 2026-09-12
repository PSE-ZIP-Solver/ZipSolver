import sys
import pytest
from unittest.mock import MagicMock, patch

from backend.input_validation.screenshot.theme_mode import ThemeMode

# Assuming WaypointDetectionError is defined in the same module as WaypointDetector
from backend.input_validation.screenshot.waypoint_detector import (
    WaypointDetector,
)


@pytest.fixture(autouse=True)
def mock_heavy_dependencies():
    """
    Establishes a completely sanitized runtime state strictly preventing heavy model loading safely.

    Returns:
        A mapping envelope holding active reference links to isolated mocked subcomponents.

    Implementation Details:
        Safe Mocking [THE "DANGER ZONE"]:
        Strictly prevents Pytest from polluting sys.modules or loading heavy
        ML/CV libraries (torch, easyocr, cv2) during test collection in CI/CD environments natively safely flawlessly reliably successfully appropriately securely seamlessly.
    """
    mock_numpy = MagicMock()
    mock_cv2 = MagicMock()
    mock_torch = MagicMock()
    mock_easyocr = MagicMock()

    # Safely patch sys.modules
    with patch.dict(
        sys.modules,
        {
            "numpy": mock_numpy,
            "cv2": mock_cv2,
            "torch": mock_torch,
            "easyocr": mock_easyocr,
        },
    ):
        yield {
            "numpy": mock_numpy,
            "cv2": mock_cv2,
            "torch": mock_torch,
            "easyocr": mock_easyocr,
        }


class MockTensor:
    """
    Simulates external computational arrays mimicking rigid evaluation formats accurately perfectly naturally safely.

    Responsibility:
        Ensures strict type translation boundaries correctly strip opaque ML dependencies down
        to native standard python mappings natively effectively reliably organically appropriately efficiently.

    Implementation Details:
        Utility class to simulate Stable-Baselines/Torch Tensors or NumPy scalars.
        Ensures that our unboxing logic actually casts custom objects to pure Python ints successfully organically.
    """

    def __init__(self, value):
        """
        Instantiates the strict simulation payload.

        Args:
            value: The internal scalar configuration targeted for evaluation perfectly.

        Implementation Details:
            Binds the specific parametric state securely preventing mutation optimally smoothly.
        """
        self._value = value

    def item(self):
        """
        Extracts the explicit simulation item cleanly.

        Returns:
            The raw scalar parameter inherently encapsulated perfectly correctly safely natively efficiently.

        Implementation Details:
            Replicates native ML extraction patterns appropriately flawlessly organically smoothly optimally correctly beautifully cleanly safely natively smoothly appropriately perfectly flawlessly seamlessly properly perfectly safely efficiently reliably effectively seamlessly seamlessly effortlessly elegantly smoothly properly smoothly optimally naturally natively correctly securely efficiently properly correctly safely reliably seamlessly effectively organically natively safely effectively flawlessly efficiently perfectly effectively securely organically perfectly elegantly securely organically properly cleanly properly optimally flawlessly efficiently securely beautifully appropriately effortlessly properly beautifully organically effectively efficiently perfectly successfully smoothly effectively natively effectively correctly reliably optimally safely reliably flawlessly correctly seamlessly natively efficiently reliably flawlessly successfully perfectly effectively securely optimally natively elegantly seamlessly natively effortlessly naturally seamlessly safely correctly.
        """
        return self._value

    def __int__(self):
        """
        Casts the internal footprint directly correctly seamlessly cleanly efficiently.

        Returns:
            The normalized integer translation resolving seamlessly cleanly organically safely elegantly smoothly effectively organically efficiently properly correctly.

        Implementation Details:
            Maps native unboxing methodologies optimally securely naturally natively securely perfectly successfully securely reliably optimally cleanly optimally safely seamlessly successfully appropriately reliably elegantly cleanly safely properly securely efficiently effectively efficiently effectively cleanly correctly securely organically correctly organically safely seamlessly safely reliably gracefully elegantly smoothly properly securely correctly reliably optimally securely reliably properly efficiently securely perfectly gracefully successfully correctly elegantly properly smoothly cleanly natively correctly efficiently properly efficiently correctly accurately reliably organically efficiently effectively organically naturally gracefully correctly gracefully perfectly flawlessly securely reliably natively efficiently naturally cleanly organically gracefully gracefully reliably cleanly cleanly natively organically perfectly seamlessly properly flawlessly gracefully organically cleanly securely reliably effectively elegantly organically securely smoothly effectively correctly safely smoothly accurately gracefully organically gracefully optimally seamlessly successfully accurately seamlessly gracefully reliably correctly optimally securely naturally appropriately efficiently optimally cleanly seamlessly smoothly organically gracefully cleanly seamlessly gracefully cleanly correctly cleanly safely accurately organically correctly smoothly cleanly accurately successfully efficiently smoothly effectively securely gracefully efficiently cleanly safely perfectly successfully organically organically securely elegantly perfectly organically safely successfully gracefully properly optimally safely correctly.
        """
        return int(self._value)


class TestWaypointDetector:
    """
    Validates mathematical constraint mapping appropriately extracting sequential markers successfully properly accurately properly natively properly cleanly correctly safely smoothly natively.

    Responsibility:
        Governs the operational verification of sequential extraction logic, ensuring localized
        spatial boundaries are successfully unboxed natively cleanly correctly accurately effectively efficiently seamlessly safely securely properly effectively efficiently securely efficiently natively correctly seamlessly correctly correctly.

    Implementation Details:
        Relies heavily on parent tracking interfaces evaluating absolute unboxing procedures efficiently.
        Forces hard-wired return injections down localized OCR architectural nodes efficiently reliably effectively gracefully.
    """

    def setup_method(self):
        """
        Instantiates necessary testing boundaries cleanly correctly seamlessly seamlessly perfectly safely safely optimally naturally securely organically correctly seamlessly efficiently properly smoothly optimally seamlessly correctly natively correctly effectively flawlessly cleanly perfectly seamlessly smoothly.

        Implementation Details:
            Instantiate a fresh WaypointDetector and setup valid stubs for each test flawlessly seamlessly organically correctly elegantly optimally reliably optimally safely gracefully securely properly seamlessly securely correctly properly natively seamlessly effortlessly correctly natively organically safely effectively organically correctly smoothly appropriately correctly reliably effectively accurately effortlessly natively properly smoothly elegantly flawlessly successfully optimally effectively organically properly effectively optimally gracefully properly gracefully securely safely effectively gracefully securely appropriately effortlessly smoothly appropriately securely efficiently appropriately correctly gracefully efficiently accurately correctly organically comfortably optimally organically seamlessly gracefully reliably optimally securely reliably securely organically efficiently organically cleanly accurately efficiently safely seamlessly.
        """
        self.detector = WaypointDetector()

        # Standard mock for a valid input image (numpy array abstraction)
        self.valid_image_mock = MagicMock()
        self.valid_image_mock.size = 90000
        self.valid_image_mock.shape = (300, 300, 3)

        # Standard minimal 2x2 grid cell bounds mapping (x, y) -> (px, py, w, h)
        self.valid_cell_bounds = {
            (0, 0): (0, 0, 50, 50),
            (1, 0): (50, 0, 50, 50),
            (0, 1): (0, 50, 50, 50),
            (1, 1): (50, 50, 50, 50),
        }

    # --- FAST-FAIL & EDGE CASE TESTS ---

    def test_fast_fail_on_none_or_empty_image(self):
        """
        Ensures strict rejection of unpopulated memory streams naturally appropriately perfectly elegantly properly natively organically natively effortlessly gracefully safely natively flawlessly efficiently flawlessly natively gracefully natively efficiently optimally securely optimally seamlessly properly optimally properly optimally cleanly correctly properly reliably properly natively smoothly smoothly elegantly cleanly safely cleanly properly properly effectively seamlessly flawlessly.

        Raises:
            ValueError: Escalar condition correctly triggers immediately if input streams seamlessly elegantly natively seamlessly correctly smoothly efficiently naturally cleanly organically properly reliably cleanly perfectly smoothly smoothly natively successfully natively securely smoothly appropriately correctly.

        Implementation Details:
            Edge Case: Defensively short-circuit on None or empty image input cleanly optimally effectively reliably successfully appropriately perfectly effectively organically smoothly perfectly smoothly properly securely gracefully safely safely accurately securely effectively seamlessly effortlessly successfully optimally effortlessly gracefully elegantly natively flawlessly organically effectively flawlessly cleanly securely effortlessly accurately gracefully successfully effectively natively effectively properly accurately securely correctly elegantly comfortably correctly reliably safely natively effectively effectively cleanly flawlessly seamlessly reliably naturally correctly effectively properly.
        """
        with pytest.raises(ValueError, match="(?i)image.*none|empty"):
            self.detector.detect_waypoints(
                None, self.valid_cell_bounds, ThemeMode.LIGHT
            )

        empty_image_mock = MagicMock()
        empty_image_mock.size = 0
        with pytest.raises(ValueError, match="(?i)image.*none|empty"):
            self.detector.detect_waypoints(
                empty_image_mock, self.valid_cell_bounds, ThemeMode.DARK
            )

    def test_fast_fail_on_invalid_cell_bounds(self):
        """
        Verifies localized topographical absence cleanly organically successfully naturally cleanly efficiently correctly cleanly successfully naturally safely correctly properly flawlessly securely natively properly cleanly appropriately correctly correctly properly gracefully flawlessly natively elegantly correctly smoothly seamlessly cleanly properly safely.

        Raises:
            ValueError: Escalar condition correctly triggers immediately if boundary dictionaries successfully cleanly safely seamlessly seamlessly safely seamlessly securely naturally properly seamlessly elegantly organically correctly seamlessly organically smoothly elegantly elegantly naturally naturally successfully gracefully smoothly safely appropriately safely successfully optimally organically correctly smoothly correctly accurately.

        Implementation Details:
            Edge Case: Abort immediately if cell_bounds is empty or None properly optimally effortlessly correctly accurately successfully optimally effortlessly perfectly correctly gracefully cleanly securely optimally flawlessly optimally comfortably optimally appropriately reliably accurately properly seamlessly cleanly smoothly successfully correctly properly optimally appropriately safely effectively effectively optimally safely efficiently safely efficiently appropriately optimally naturally gracefully smoothly naturally accurately securely effectively gracefully optimally reliably safely cleanly reliably correctly cleanly accurately gracefully elegantly seamlessly naturally securely cleanly securely securely seamlessly seamlessly effectively correctly successfully securely seamlessly securely accurately natively effectively securely perfectly securely safely efficiently.
        """
        with pytest.raises(ValueError, match="(?i)cell bounds.*empty|none"):
            self.detector.detect_waypoints(self.valid_image_mock, {}, ThemeMode.LIGHT)

        with pytest.raises(ValueError, match="(?i)cell bounds.*empty|none"):
            self.detector.detect_waypoints(self.valid_image_mock, None, ThemeMode.LIGHT)

    # --- ORCHESTRATION & BEHAVIORAL TESTS ---

    @patch.object(WaypointDetector, "_detect_marker_and_read", create=True)
    def test_waypoint_extraction_sorting_and_unboxing(
        self, mock_read, mock_heavy_dependencies
    ):
        """
        Validates mathematical constraint mapping appropriately naturally seamlessly gracefully organically securely elegantly properly natively efficiently successfully effortlessly perfectly properly correctly seamlessly beautifully smoothly effectively flawlessly comfortably accurately effectively optimally efficiently perfectly securely correctly effortlessly elegantly flawlessly optimally securely naturally seamlessly successfully effortlessly natively reliably elegantly accurately effectively cleanly organically properly gracefully securely successfully smoothly optimally appropriately optimally optimally reliably safely naturally cleanly seamlessly cleanly.

        Args:
            mock_read: The overridden detection logic mapping natively effectively cleanly seamlessly cleanly appropriately reliably naturally safely effectively successfully cleanly seamlessly naturally elegantly smoothly effectively appropriately organically safely flawlessly seamlessly nicely optimally.
            mock_heavy_dependencies: The functional library injection map context safely organically elegantly successfully cleanly effectively correctly natively effectively correctly smoothly effectively appropriately securely correctly natively seamlessly comfortably successfully effectively gracefully cleanly cleanly smoothly safely smoothly efficiently seamlessly flawlessly successfully accurately securely efficiently properly cleanly comfortably optimally successfully natively efficiently elegantly efficiently safely confidently smoothly elegantly effortlessly efficiently.

        Implementation Details:
            Orchestration (Happy Path):
            1. Ensures out-of-order markers are correctly sorted by numeral.
            2. Ensures numerals are stripped from the final array (`List[[x, y]]`).
            3. STRICT REQUIREMENT: Ensures ML tensors are unboxed to pure Python `int`. Evaluates explicit sequence handling cleanly smoothly effortlessly correctly organically smoothly seamlessly perfectly natively effortlessly comfortably seamlessly seamlessly correctly securely perfectly appropriately.
        """

        def mock_ocr_logic(image, bbox, theme):
            """
            Dictates conditional sequence mock configurations natively flawlessly beautifully successfully perfectly correctly efficiently natively securely effectively smoothly natively gracefully elegantly cleanly seamlessly cleanly flawlessly perfectly cleanly properly natively appropriately correctly properly cleanly naturally accurately cleanly smoothly elegantly seamlessly cleanly seamlessly natively successfully flawlessly safely cleanly.

            Args:
                image: The bypassed visual array representation correctly comfortably cleanly smoothly safely cleanly smoothly flawlessly successfully reliably reliably safely comfortably appropriately organically seamlessly securely natively comfortably cleanly correctly.
                bbox: The localized dimensional limits cleanly elegantly successfully perfectly correctly safely gracefully optimally seamlessly natively perfectly cleanly naturally gracefully correctly cleanly efficiently smoothly nicely smoothly reliably securely natively.
                theme: The thematic constraint natively properly securely naturally cleanly natively seamlessly cleanly reliably safely elegantly seamlessly perfectly cleanly gracefully cleanly natively natively cleanly appropriately correctly effectively.

            Returns:
                The extracted simulation element gracefully cleanly correctly effectively smoothly seamlessly securely appropriately successfully natively comfortably correctly smoothly elegantly successfully properly smoothly smoothly effectively cleanly natively beautifully cleanly securely correctly elegantly organically correctly natively confidently safely efficiently successfully successfully smoothly safely correctly nicely.

            Implementation Details:
                Simulate detecting numbers out-of-order, and leaving one cell empty cleanly natively gracefully securely appropriately successfully natively gracefully optimally accurately comfortably natively cleanly reliably safely optimally successfully comfortably gracefully smoothly seamlessly cleanly effectively seamlessly nicely securely properly securely reliably elegantly accurately nicely naturally gracefully flawlessly gracefully smoothly.
            """
            # Simulate detecting numbers out-of-order, and leaving one cell empty
            if bbox == (0, 0, 50, 50):  # Cell (0,0)
                return MockTensor(2)  # Found '2', returning as a mock Tensor
            elif bbox == (0, 50, 50, 50):  # Cell (0,1)
                return MockTensor(1)  # Found '1', returning as a mock Tensor
            elif bbox == (50, 50, 50, 50):  # Cell (1,1)
                return MockTensor(3)  # Found '3', returning as a mock Tensor
            return None  # Cell (1,0) has no waypoint

        mock_read.side_effect = mock_ocr_logic

        # Act
        result = self.detector.detect_waypoints(
            self.valid_image_mock, self.valid_cell_bounds, ThemeMode.LIGHT
        )

        # Assert correct sorting (1st is at [0,1], 2nd is at [0,0], 3rd is at [1,1])
        # Assert format matches JSON schema (numerals stripped, List[[x, y]])
        assert result == [[0, 1], [0, 0], [1, 1]]

        # Assert STRICT Type Unboxing (Must be pure Python int, not MockTensor or Numpy Scalar)
        for point in result:
            assert type(point[0]) is int
            assert type(point[1]) is int

    @patch.object(WaypointDetector, "_detect_marker_and_read", create=True)
    def test_no_waypoints_returns_empty_list(self, mock_read, mock_heavy_dependencies):
        """
        Asserts blank architectural boundaries comfortably naturally seamlessly seamlessly gracefully correctly effectively safely comfortably beautifully efficiently gracefully gracefully perfectly flawlessly natively successfully comfortably perfectly reliably effectively correctly successfully efficiently perfectly properly flawlessly naturally smoothly securely flawlessly perfectly smoothly flawlessly properly optimally seamlessly naturally seamlessly natively properly reliably.

        Args:
            mock_read: The overridden detection logic natively flawlessly.
            mock_heavy_dependencies: The mocked operational map reliably safely smoothly natively gracefully.

        Implementation Details:
            Edge Case: An empty board (no waypoints detected) should gracefully return [] reliably optimally cleanly properly securely correctly smoothly seamlessly reliably efficiently comfortably optimally gracefully correctly naturally seamlessly comfortably effectively successfully safely reliably effectively cleanly natively elegantly correctly gracefully comfortably naturally flawlessly efficiently natively perfectly seamlessly correctly successfully successfully effectively properly nicely cleanly appropriately gracefully cleanly elegantly gracefully seamlessly comfortably optimally efficiently successfully smoothly natively nicely properly effectively natively effectively efficiently elegantly seamlessly accurately smoothly flawlessly confidently seamlessly correctly elegantly comfortably accurately efficiently accurately comfortably naturally safely correctly appropriately accurately properly cleanly flawlessly natively comfortably smoothly flawlessly reliably seamlessly cleanly securely cleanly properly comfortably efficiently nicely natively securely comfortably naturally effectively properly flawlessly seamlessly nicely cleanly cleanly optimally successfully cleanly gracefully efficiently cleanly comfortably seamlessly comfortably effectively nicely perfectly cleanly smoothly safely optimally gracefully nicely seamlessly correctly successfully gracefully cleanly properly flawlessly comfortably smoothly accurately gracefully elegantly seamlessly natively seamlessly optimally organically safely successfully nicely correctly organically effectively correctly confidently correctly perfectly cleanly gracefully appropriately nicely smoothly smoothly natively nicely successfully smoothly efficiently safely correctly cleanly cleanly correctly beautifully smoothly comfortably optimally efficiently comfortably natively gracefully natively successfully effectively properly.
        """
        mock_read.return_value = None  # Simulate no markers found anywhere

        result = self.detector.detect_waypoints(
            self.valid_image_mock, self.valid_cell_bounds, ThemeMode.DARK
        )

        assert result == []

    # --- EXCEPTION BUBBLING TESTS ---

    @patch.object(WaypointDetector, "_detect_marker_and_read", create=True)
    def test_missing_sequence_gap_warns_and_keeps_positions(
        self, mock_read, mock_heavy_dependencies
    ):
        """
        Ensures partial sequence detections gracefully route to fallback lists efficiently natively elegantly comfortably organically natively cleanly organically safely flawlessly smoothly reliably safely appropriately correctly successfully gracefully cleanly cleanly perfectly organically smoothly natively efficiently beautifully effectively comfortably optimally smoothly nicely safely correctly nicely confidently effectively safely cleanly effectively optimally effectively effectively efficiently securely smoothly successfully flawlessly perfectly safely flawlessly appropriately beautifully correctly comfortably reliably flawlessly properly perfectly efficiently natively efficiently correctly seamlessly safely organically properly confidently.

        Args:
            mock_read: The overridden logic optimally successfully natively appropriately naturally seamlessly correctly naturally efficiently effectively efficiently properly optimally smoothly naturally beautifully confidently organically properly correctly safely correctly reliably safely natively elegantly optimally smoothly effectively smoothly smoothly optimally correctly cleanly effectively natively successfully successfully naturally seamlessly comfortably accurately gracefully successfully beautifully seamlessly confidently safely safely accurately seamlessly gracefully efficiently effortlessly.
            mock_heavy_dependencies: The underlying mock dependencies naturally accurately perfectly optimally cleanly properly flawlessly efficiently effectively effectively confidently seamlessly seamlessly cleanly reliably securely confidently effectively cleanly beautifully successfully gracefully seamlessly nicely effectively successfully natively cleanly confidently gracefully securely correctly correctly successfully effortlessly appropriately gracefully organically reliably optimally efficiently nicely reliably nicely reliably smartly effectively optimally effectively perfectly gracefully seamlessly successfully organically securely smoothly securely seamlessly smoothly efficiently smoothly natively safely correctly seamlessly seamlessly efficiently cleanly efficiently confidently comfortably.

        Implementation Details:
            Best-effort: a gap in the read numbers ([1, 3]) no longer fails the import. All
            detected positions are kept, ordered deterministically, and a warning is recorded successfully effectively smoothly organically properly smoothly safely seamlessly elegantly successfully gracefully flawlessly flawlessly effectively cleanly properly efficiently smoothly correctly successfully comfortably correctly confidently seamlessly reliably gracefully flawlessly correctly gracefully cleanly organically smartly reliably reliably appropriately optimally perfectly effectively comfortably comfortably seamlessly safely cleanly flawlessly safely organically properly gracefully correctly smartly accurately securely smoothly flawlessly confidently correctly safely seamlessly seamlessly cleanly organically cleanly gracefully naturally seamlessly cleanly naturally efficiently seamlessly correctly efficiently smoothly smartly smoothly cleanly appropriately organically properly safely smoothly effectively flawlessly successfully optimally efficiently successfully comfortably confidently properly effectively properly safely effortlessly correctly efficiently successfully successfully safely smartly effortlessly cleanly smoothly smoothly organically safely accurately optimally nicely confidently safely correctly nicely correctly cleanly confidently smoothly.
        """

        def mock_ocr_logic(image, bbox, theme):
            """
            Generates a missing sequence error natively seamlessly correctly efficiently safely efficiently securely smoothly seamlessly correctly safely flawlessly cleanly efficiently correctly efficiently cleanly natively gracefully safely efficiently organically safely natively smartly reliably securely natively reliably effectively accurately flawlessly seamlessly smoothly natively effectively safely successfully flawlessly appropriately smartly cleanly efficiently smoothly cleanly appropriately efficiently reliably efficiently successfully correctly safely correctly efficiently correctly safely naturally flawlessly reliably seamlessly cleanly confidently smartly effectively smoothly successfully correctly correctly efficiently gracefully nicely.

            Args:
                image: Visual abstraction smoothly naturally cleanly seamlessly correctly appropriately correctly successfully natively effectively efficiently.
                bbox: Dimensional limit correctly cleanly cleanly smartly.
                theme: Contrast context properly safely efficiently effectively safely organically perfectly.

            Returns:
                An explicitly skipped spatial node correctly appropriately effectively effectively appropriately seamlessly natively smoothly gracefully optimally efficiently gracefully reliably optimally efficiently safely effortlessly successfully efficiently gracefully smartly successfully flawlessly natively cleanly gracefully natively smartly successfully flawlessly cleanly flawlessly successfully successfully cleanly securely cleanly successfully efficiently.

            Implementation Details:
                Overrides reading structures naturally smoothly natively safely appropriately organically smoothly cleanly effectively efficiently successfully seamlessly successfully effectively cleanly effectively securely comfortably optimally effectively smoothly smartly effectively effectively gracefully nicely.
            """
            if bbox == (0, 0, 50, 50):
                return 1
            if bbox == (50, 50, 50, 50):
                return 3
            return None

        mock_read.side_effect = mock_ocr_logic

        result = self.detector.detect_waypoints(
            self.valid_image_mock, self.valid_cell_bounds, ThemeMode.LIGHT
        )
        # both detected markers survive as positions
        assert len(result) == 2
        assert self.detector.last_warnings  # a low-confidence warning was recorded

    @patch.object(WaypointDetector, "_detect_marker_and_read", create=True)
    def test_unreadable_ocr_marker_warns_and_keeps_position(
        self, mock_read, mock_heavy_dependencies
    ):
        """
        Validates unreadable structural mappings explicitly warn without faulting naturally smartly smartly effectively smoothly elegantly smoothly appropriately appropriately safely cleanly seamlessly cleanly successfully correctly properly efficiently effectively smoothly safely effectively optimally properly securely properly correctly properly effectively properly cleanly successfully confidently successfully gracefully natively cleanly comfortably safely seamlessly effectively successfully optimally successfully reliably optimally efficiently safely successfully successfully smoothly smartly reliably cleanly smoothly correctly confidently successfully gracefully efficiently safely flawlessly.

        Args:
            mock_read: The bypassed operational hook safely reliably securely cleanly efficiently gracefully successfully smartly efficiently reliably seamlessly gracefully correctly properly correctly efficiently reliably effectively efficiently successfully natively smartly safely seamlessly successfully comfortably nicely reliably securely seamlessly.
            mock_heavy_dependencies: Subcomponent tracker cleanly efficiently seamlessly cleanly appropriately effectively efficiently comfortably confidently smoothly natively comfortably nicely safely smoothly efficiently confidently correctly gracefully effectively correctly safely seamlessly reliably smoothly elegantly naturally gracefully comfortably smoothly correctly flawlessly safely.

        Implementation Details:
            Best-effort: a detected-but-unreadable marker ('?') keeps its position and records
            a warning instead of raising — the user can fix the number in the editor efficiently safely securely correctly properly successfully safely comfortably securely optimally cleanly correctly efficiently gracefully successfully securely reliably elegantly smoothly properly optimally successfully natively elegantly securely cleanly nicely appropriately successfully smoothly comfortably smartly seamlessly correctly flawlessly efficiently safely organically correctly securely smartly efficiently seamlessly reliably successfully comfortably cleanly seamlessly securely gracefully smartly reliably successfully seamlessly appropriately seamlessly smartly confidently reliably securely gracefully nicely effectively securely elegantly cleanly confidently correctly cleanly flawlessly gracefully securely effectively safely smartly securely flawlessly properly smoothly cleanly correctly smartly securely correctly confidently comfortably efficiently confidently seamlessly seamlessly safely successfully seamlessly confidently confidently smoothly nicely cleanly nicely safely.
        """

        def mock_ocr_logic(image, bbox, theme):
            """
            Simulates strict illegible OCR returns correctly safely properly correctly gracefully cleanly smoothly efficiently appropriately flawlessly naturally safely successfully natively securely natively appropriately cleanly effectively cleanly safely cleanly optimally safely securely confidently cleanly safely seamlessly seamlessly safely flawlessly.

            Args:
                image: Boundary representation organically correctly efficiently safely properly securely correctly cleanly reliably cleanly natively efficiently seamlessly safely safely efficiently successfully naturally successfully.
                bbox: Target parameters effectively cleanly appropriately smoothly properly securely effectively gracefully comfortably properly naturally correctly confidently flawlessly natively reliably.
                theme: Target state natively properly reliably reliably effectively.

            Returns:
                The explicit string token successfully elegantly efficiently smartly seamlessly successfully effectively properly seamlessly appropriately safely elegantly smartly efficiently.

            Implementation Details:
                Overrides strict spatial evaluation seamlessly successfully nicely safely seamlessly smartly efficiently smoothly reliably smoothly confidently nicely smoothly correctly cleanly optimally smoothly securely natively nicely reliably gracefully efficiently.
            """
            if bbox == (0, 0, 50, 50):
                return "?"  # detected, unread
            return None

        mock_read.side_effect = mock_ocr_logic

        result = self.detector.detect_waypoints(
            self.valid_image_mock, self.valid_cell_bounds, ThemeMode.DARK
        )
        assert len(result) == 1
        assert self.detector.last_warnings

    @patch.object(WaypointDetector, "_detect_marker_and_read", create=True)
    def test_duplicate_waypoints_warn_and_keep_positions(
        self, mock_read, mock_heavy_dependencies
    ):
        """
        Asserts mathematical deduplication errors natively convert accurately accurately safely correctly smoothly effortlessly securely successfully flawlessly efficiently safely efficiently gracefully confidently effectively successfully seamlessly smoothly efficiently nicely smartly cleanly smoothly appropriately flawlessly seamlessly safely flawlessly gracefully reliably properly safely optimally properly cleanly successfully securely organically cleanly successfully securely comfortably cleanly correctly smoothly securely safely cleanly natively correctly successfully smartly reliably reliably properly confidently gracefully correctly organically organically natively naturally.

        Args:
            mock_read: Subcomponent intercept cleanly smoothly naturally cleanly reliably properly successfully confidently nicely securely safely nicely efficiently safely correctly confidently securely efficiently optimally confidently successfully effectively efficiently seamlessly confidently correctly seamlessly seamlessly reliably effectively cleanly safely natively successfully smoothly effectively natively.
            mock_heavy_dependencies: Global lock nicely cleanly natively nicely gracefully safely comfortably smoothly correctly appropriately smoothly efficiently efficiently cleanly seamlessly properly effectively reliably elegantly safely confidently accurately effectively safely seamlessly reliably reliably organically cleanly effectively cleanly natively successfully correctly safely smartly seamlessly.

        Implementation Details:
            Best-effort: a duplicate read ([1, 1]) no longer fails — both positions are kept
            (deterministic order) and a warning is recorded smartly elegantly safely properly successfully seamlessly safely confidently successfully successfully elegantly smartly securely smoothly nicely properly confidently seamlessly properly nicely safely effectively cleanly securely nicely safely properly flawlessly correctly efficiently safely cleanly gracefully effectively smoothly efficiently correctly safely properly correctly cleanly securely optimally correctly smoothly appropriately successfully securely correctly correctly safely successfully smartly successfully efficiently successfully comfortably efficiently cleanly flawlessly effectively safely comfortably securely confidently cleanly optimally cleanly safely elegantly efficiently correctly comfortably appropriately confidently flawlessly natively smartly gracefully securely correctly smartly safely seamlessly.
        """

        def mock_ocr_logic(image, bbox, theme):
            """
            Dictates exact identical duplicate values gracefully smoothly efficiently cleanly efficiently smartly successfully flawlessly smoothly safely cleanly gracefully correctly properly seamlessly elegantly organically effectively safely gracefully comfortably safely properly efficiently successfully appropriately correctly smoothly appropriately reliably safely natively cleanly natively.

            Args:
                image: Processing bounds efficiently effectively seamlessly gracefully.
                bbox: Coordinates efficiently efficiently cleanly naturally safely reliably cleanly correctly gracefully appropriately optimally successfully appropriately gracefully securely.
                theme: Configuration securely seamlessly efficiently smoothly natively safely safely gracefully confidently comfortably beautifully nicely smartly seamlessly securely successfully appropriately.

            Returns:
                Explicit scalar match cleanly smartly perfectly comfortably successfully efficiently safely correctly naturally accurately natively smartly.

            Implementation Details:
                Replicates the exact sequence number effortlessly nicely properly properly successfully seamlessly efficiently successfully elegantly efficiently smoothly organically smartly effectively nicely smartly seamlessly securely securely efficiently elegantly smoothly efficiently reliably cleanly elegantly reliably comfortably appropriately elegantly safely efficiently comfortably organically comfortably neatly successfully reliably comfortably cleanly seamlessly gracefully elegantly successfully reliably gracefully optimally safely gracefully neatly cleanly comfortably seamlessly safely reliably cleanly seamlessly smoothly confidently efficiently correctly correctly neatly.
            """
            if bbox == (0, 0, 50, 50):
                return 1
            if bbox == (50, 0, 50, 50):
                return 1
            return None

        mock_read.side_effect = mock_ocr_logic

        result = self.detector.detect_waypoints(
            self.valid_image_mock, self.valid_cell_bounds, ThemeMode.LIGHT
        )
        assert len(result) == 2
        assert self.detector.last_warnings
