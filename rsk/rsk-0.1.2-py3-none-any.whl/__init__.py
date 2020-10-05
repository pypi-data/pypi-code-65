# Given a sorted list L, and a number x, find the smallest j >= 0 such 
# that L[j] > x, or return len(L) if no such j exists.
# This can be improved: please do!
def proc1(L, x):
  j = 0
  while j < len(L) and L[j] <= x:
    j += 1
  return j


# Given a pair of semistandard tableau, insert (y x) into it.
#   Example:
#  p = [[1, 2, 3], [3]]
#  q = [[1, 1, 1], [2]]
#  x = 2
#  y = 4
#  insert(x, y, p, q)
# This corresponds to 
#
#   Insert ( 4 )
#          ( 2 )
# 
#   into       123     111
#              3       2,
# yielding
#              122     111
#              33      24,
# or p = [[1, 2, 2], [3, 3]],
#    q = [[1, 1, 1], [2, 4]]
def insert(x,y, p, q):
  i = 0
  while True:
    if len(p) <= i:
      p.append([x])
      q.append([y])
      break
    j = proc1(p[i], x);
    if j < len(p[i]):
      (x, p[i][j]) = (p[i][j], x)
      i += 1
    else:
      p[i].append(x)
      q[i].append(y)
      break

def single_insertion():
  p = [[1,2,3],[3]]
  q = [[1,1,1],[2]]
  x = 2
  y = 4
  insert(x,y, p, q)
  print(p)
  print(q)

#https://en.wikipedia.org/wiki/Robinson%E2%80%93Schensted%E2%80%93Knuth_correspondence
def wikipedia_example():
  p = []
  q = []
  example = [ (1,1), (3,1), (3,1),(2,2), (2,2),(1,3),(2,3)]
  for (x,y) in example:
    insert(x,y,p,q)
  print(p)
  print(q)

#single_insertion()
#wikipedia_example()

