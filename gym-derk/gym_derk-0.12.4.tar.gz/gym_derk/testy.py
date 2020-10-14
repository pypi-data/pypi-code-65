import numpy as np
from typing import List
# import enum

def print_table(columns: List[str], data: np.ndarray, padding=20):
  print(" |".join([k.rjust(padding) for k in columns]))
  print("|".join(["".rjust(padding + 1, "-") for k in columns]))

  indices = np.array(list(np.ndindex(data.shape[0:-1])))
  data = data.reshape((-1, data.shape[-1]))
  combined = np.concatenate((indices, data), axis=1)

  for i in range(combined.shape[0]):
    print(" |".join([str(x).rjust(padding) for x in combined[i, :]]))

team_stats = np.random.rand(2, 4, 6)
team_stats_keys = [str(x) for x in range(6)]

print_table(["side", "arena"] + team_stats_keys, team_stats)

# indices = np.array(list(np.ndindex(team_stats.shape[0:-1])))
# print(indices)
# team_stats = team_stats.reshape((-1, team_stats.shape[-1]))
# print(team_stats.shape)
# combined = np.concatenate((indices, team_stats), axis=1)
# print(combined)
# while len(team_stats.shape) > 1:
# indices = np.arange(team_stats.shape[0])
# print(indices.shape)
# while len(indices.shape) < len(team_stats.shape):
#   indices = np.expand_dims(indices, 1)
#   print(indices.shape)
# team_stats = np.concatenate((indices, team_stats), axis=0)
# print(team_stats.shape)
# print(team_stats)
  # team_stats = team_stats.reshape()

# print(" | ".join([k.rjust(20) for k in ["side", "arena"] + team_stats_keys]))
# for side in [0, 1]:
#   for arena in range(team_stats.shape[1]):
#     values = [side, arena] + [team_stats[side, arena, i] for i in range(team_stats.shape[2])]
#     print(" | ".join([str(x).rjust(20) for x in values]))