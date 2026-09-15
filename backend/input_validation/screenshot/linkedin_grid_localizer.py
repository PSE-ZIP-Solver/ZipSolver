"""Localize upright LinkedIn-style grids with black numbered discs.

No source-specific coordinates or screenshots are embedded here. The board is
selected from closed grid outlines containing circular marker candidates.
"""


def localize_linkedin_grid(image_data, board_size):
    """Return (cell bounds, marker centres), or None for another visual style.

    The caller validates the supplied board size. Separate horizontal/vertical
    fits accommodate screenshots that have been slightly stretched in transit.
    """
    import cv2
    import numpy as np

    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    dark = (gray < 95).astype(np.uint8) * 255
    contours, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        (cx, cy), radius = cv2.minEnclosingCircle(contour)
        if area >= 300 and area / (np.pi * radius * radius) > 0.82:
            circles.append((float(cx), float(cy), float(radius)))
    if len(circles) < 2:
        return None

    # Grid lines form a closed contour even though their colour is much lighter
    # than the walls. Unlike a white-background mask, this excludes page chrome.
    lines = (gray < 235).astype(np.uint8) * 255
    contours, _ = cv2.findContours(lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if not 0.8 < w / h < 1.25 or w * h < gray.size * 0.04:
            continue
        # A tight crop may remove part of the outer frame while leaving every
        # marker visible. Permit the resulting open contour only at an image edge.
        clipped = x == 0 or y == 0 or x + w == gray.shape[1] or y + h == gray.shape[0]
        min_fill = 0.65 if clipped else 0.75
        if cv2.contourArea(contour) / (w * h) < min_fill:
            continue
        inside = [c for c in circles if x < c[0] < x + w and y < c[1] < y + h]
        if len(inside) >= 2:
            candidates.append((len(inside), w * h, x, y, w, h, inside))
    if not candidates:
        return None
    _, _, x, y, w, h, inside = max(candidates, key=lambda c: c[:2])

    def fit_axis(values, origin, span):
        pitch = span / board_size
        indices = np.rint((values - origin) / pitch - 0.5)
        if len(np.unique(indices)) >= 2:
            design = np.column_stack((np.ones(len(values)), indices + 0.5))
            fitted_origin, fitted_pitch = np.linalg.lstsq(design, values, rcond=None)[0]
            if abs(fitted_pitch - pitch) <= pitch * 0.08:
                origin, pitch = float(fitted_origin), float(fitted_pitch)
        else:
            origin += float(np.median(values - (origin + (indices + 0.5) * pitch)))
        return origin, pitch

    ox, px = fit_axis(np.array([c[0] for c in inside]), x, w)
    oy, py = fit_axis(np.array([c[1] for c in inside]), y, h)
    discs = {}
    for cx, cy, radius in inside:
        col, row = int(round((cx - ox) / px - 0.5)), int(round((cy - oy) / py - 0.5))
        # Reject candidates not centred on cells (e.g. unrelated text/icons).
        if not (0 <= col < board_size and 0 <= row < board_size):
            return None
        if abs(cx - (ox + (col + 0.5) * px)) > px * 0.12:
            return None
        if abs(cy - (oy + (row + 0.5) * py)) > py * 0.12:
            return None
        if (col, row) in discs:
            return None
        discs[(col, row)] = (cx, cy, radius)
    bounds = {
        (col, row): (round(ox + col * px), round(oy + row * py), round(px), round(py))
        for row in range(board_size) for col in range(board_size)
    }
    return bounds, discs
