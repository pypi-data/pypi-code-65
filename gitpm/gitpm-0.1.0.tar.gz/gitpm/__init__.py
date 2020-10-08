
import argparse, sys, os

from .repository import Repository
R = Repo = Repository # synonymous classes

class GitPmError:

  @staticmethod
  def error(e):
    parser.error(e)

  @staticmethod
  def singleArgError(op, arg):
    GitPmError.error(
      'expected a single argument for the "'
        + op + '" operation: "' + arg + '"'
    )

def printTable(widths, data):

  row_format = ''.join(['{:<' + str(w) + '}' for w in widths])

  for row in data:
    print(row_format.format(*row))

def is_hex(string):
  try:
    int(string, 16)
  except ValueError:
    return False
  return True

def run(directory, arguments):

  # --- parse args

  parser = argparse.ArgumentParser(
    description = "Manage multiple bare git-repositories."
  )

  parser.add_argument(
    'verb',
    default = 'list',
    nargs = '?',
    help = "The operation to be carried out."
  )

  parser.add_argument(
    'args',
    nargs = '*',
    help = "Operation-specific data."
  )

  args = parser.parse_args(arguments)

  if args.verb == 'list': # --------------------------------|

    if len(args.args) == 0 or args.args[0] == 'all':
      printTable(
        [R.id_width + 4, 32, 16, R.hash_abbr_len],
        [[
          r.id,
          r.readFile(R.file_name),
          r.readFile(R.file_status),
          r.readFile('refs/heads/master')[0:R.hash_abbr_len]
        ] for r in Repo.list(directory)]
      )
    elif args.args[0] in R.status_set:
      printTable(
        [R.id_width + 4, 32, 16, R.hash_abbr_len],
        [[
          r.id,
          r.readFile(R.file_name),
          r.readFile(R.file_status),
          r.readFile('refs/heads/master')[0:R.hash_abbr_len]
        ] for r in Repo.list(directory) if r.readFile(R.file_status) == args.args[0]]
      )
    else:
      GitPmError.error('unexpected usage of the "list" operation')

  elif args.verb == 'create': # ----------------------------|

    if len(args.args) != 1: # -------------------->
      GitPmError.singleArgError('create', 'name')

    r = Repo.create(directory, args.args[0])
    print("\nNew project id: " + r.id + ".\n")

  elif (is_hex(args.verb) and
      os.path.isdir(R.formatId(int(args.verb, 16)))): # ----|

    r = Repository(R.formatId(int(args.verb, 16)))

    if len(args.args) == 0: # -------------------->

      print("Project:\t" + r.readFile(R.file_name) + ' <' + r.id + '>\n')
      print("Status:\t" + r.readFile(R.file_status) + '\n')
      print("About:\t" + r.readFile(R.file_about) + '')
      print("Tags:\t" + r.readFile(R.file_tags) + '\n')
      print("Master:\t" + r.readFile('refs/heads/master') + '\n')

    elif args.args[0] == 'rename': # ------------->

      if len(args.args) != 2:
        GitPmError.singleArgError('rename', 'new-name')

      r.writeFile(R.file_name, args.args[1])

    elif args.args[0] == 'status': # ------------->

      if len(args.args) != 2:
        GitPmError.singleArgError('status', 'new-status')
      elif args.args[1] not in R.status_set:
        GitPmError.error('unknown staus, expected one in ' + str(R.status_set))

      r.writeFile(R.file_status, args.args[1])

    elif args.args[0] == 'describe': # ----------->

      if len(args.args) != 2:
        GitPmError.singleArgError('describe', 'project-description')

      r.writeFile(R.file_about, args.args[1])

    elif args.args[0] == 'retag': # -------------->

      if len(args.args) != 2:
        GitPmError.singleArgError('retag', 'new-tags')

      r.writeFile(R.file_tags, args.args[1])

  else: # --------------------------------------------------|

    parser.error('unrecognized verb "' + args.verb + '"')
