from nhlapip.const import NHLAPI_BASEURL
from nhlapip.nhl_player import Player
from nhlapip.nhl_url import NhlUrl

import pandas as pd

sakic = Player("8451101")
sakic.get_stats_allseasons()
sakic.get_data()

print(sakic.stats)
sakic.stats.__class__

statsdf = pd.json_normalize(sakic.stats)

print(statsdf)

statsdf.describe()

