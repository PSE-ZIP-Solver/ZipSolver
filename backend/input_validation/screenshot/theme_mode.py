import enum

class ThemeMode(enum.Enum):
    """
    Enumeration for the detected color palette of the board.
    Used to adjust downstream computer vision thresholds dynamically 
    (e.g., inverting OpenCV masks for walls and waypoints).
    """
    LIGHT = "LIGHT"
    DARK = "DARK"

    @property
    def isLight(self) -> bool:
        """
        Property getter to check if the current theme is LIGHT mode.
        Do NOT call with parentheses.
        """
        return self == ThemeMode.LIGHT

    @property
    def isDark(self) -> bool:
        """
        Property getter to check if the current theme is DARK mode.
        Do NOT call with parentheses.
        """
        return self == ThemeMode.DARK

    def _get_log_string(self) -> str:
        """
        Private helper method to safely format the theme for debugging or logging.
        """
        return f"[{self.__class__.__name__} :: {self.value}]"