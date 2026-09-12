import enum


class ThemeMode(enum.Enum):
    """
    Categorical enumeration managing overarching structural color baselines.

    Responsibility:
        Determines targeted thresholds utilized by underlying computer vision frameworks,
        ensuring mask evaluations, morphological ops, and extraction targets dynamically
        adapt depending on the application's underlying visual theme.

    Implementation Details:
        Derives from a native enumeration strictly limiting comparative logic maps. Integrates
        convenience properties exposing safe equality assessments without demanding external
        module injections.
    """

    LIGHT = "LIGHT"
    DARK = "DARK"

    @property
    def isLight(self) -> bool:
        """
        Evaluates active state equality against the designated illuminated aesthetic.

        Returns:
            A boolean reporting direct equivalence to the corresponding state.

        Implementation Details:
            Exposed via property wrappers preventing unsafe external mutations while providing
            direct read-only confirmation logic. Must be evaluated natively without invocation parameters.
        """
        return self == ThemeMode.LIGHT

    @property
    def isDark(self) -> bool:
        """
        Evaluates active state equality against the designated shaded aesthetic.

        Returns:
            A boolean reporting direct equivalence to the corresponding state.

        Implementation Details:
            Exposed via property wrappers preventing unsafe external mutations while providing
            direct read-only confirmation logic. Must be evaluated natively without invocation parameters.
        """
        return self == ThemeMode.DARK

    def _get_log_string(self) -> str:
        """
        Translates structural enumeration types into cohesive diagnostic messages.

        Returns:
            The uniformly constructed debug format string safely identifying active states.

        Implementation Details:
            Uses protected namespace definitions targeting absolute internal properties natively
            to prevent formatting leaks during runtime reporting.
        """
        return f"[{self.__class__.__name__} :: {self.value}]"
