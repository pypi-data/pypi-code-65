from geo_coor import OutputFormat
from pathlib import Path

SOURCE_CSV = Path('')
COL_X = 'E'  # The header must contains this value.
NEW_COL_X = 'X'  # The new column name corresponding the COL_X
COL_Y = 'N'
NEW_COL_Y = 'Y'
FMT = OutputFormat.WGS84  # OutputFormat.WGS84, TWD97

# suffix support {csv, xlsx}
OUTPUT_FILE = None  # Path(...)  # if None, then print the result on the console screen.
# COLUMNS = [COL_X, COL_Y, NEW_COL_X, NEW_COL_Y, ...]  # You can reorder the column
