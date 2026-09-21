from __future__ import annotations

import os


def max_rl_board_size() -> int:
    """Return the largest board size for which RL inference is enabled.

    Local development keeps all trained sizes available. Render can set
    ``ZIPSOLVER_RL_MAX_BOARD_SIZE=6`` (or relies on its ``RENDER=true`` marker)
    to avoid loading the larger 7x7 and 8x8 artifacts under the 512 MB limit.
    """
    configured = os.getenv("ZIPSOLVER_RL_MAX_BOARD_SIZE")
    if configured:
        try:
            return max(0, int(configured))
        except ValueError:
            pass

    return 6 if os.getenv("RENDER", "").lower() == "true" else 8


def rl_board_size_allowed(board_size: int) -> bool:
    return board_size <= max_rl_board_size()