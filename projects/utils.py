def calculate_position(before, after):
    """
    Calculate a float position between two neighbors.
    - before: previous item's position (or None)
    - after: next item's position (or None)
    """
    if before is None and after is None:
        return 1.0

    if before is None:
        return after - 1.0

    if after is None:
        return before + 1.0

    return (before + after) / 2.0
