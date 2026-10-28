"""Fixed level geometry and zero-based (row, column) coordinates."""
MAP_ROWS = ('S......', '##...#.', '..#.E..', '#.E^...', '.....^#', '...^...', '##...#T')
START = (0, 0)
TREASURE = (6, 6)
ENEMIES = ((2, 4), (3, 2))
TRAPS = frozenset({(3, 3), (4, 5), (5, 3)})
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))
