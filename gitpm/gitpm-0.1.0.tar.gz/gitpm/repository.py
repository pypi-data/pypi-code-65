
import os

class Repository:

  id_width = 4
  hash_abbr_len = 8

  file_name = 'description'
  file_about = 'social-description'
  file_status = 'maintainance'
  file_tags = 'social-tags'

  status_set = {'new', 'maintained', 'discontinued', 'completed'}

  @staticmethod
  def list(directory):
    dirList = os.listdir(directory)

    folderList = [d for d in dirList if (os.path.isdir(d) and d != '.git'
      and len(d) == R.id_width)]
    folderList.sort(
      key = lambda s : int(s, 16),
      reverse = True
    )

    return [Repository(id) for id in folderList]

  @staticmethod
  def formatId(id):
    formatedId = hex(id)[2:]

    while Repository.id_width > len(formatedId):
      formatedId = '0' + formatedId

    return formatedId

  @staticmethod
  def create(directory, name = ''):
    repositories = Repository.list(directory)

    if len(repositories) == 0:
      newId = Repository.formatId(0)
    else:
      newId = int(repositories[0].id, 16) + 1
      newId = Repository.formatId(newId)

    os.mkdir(newId)
    r = Repository(newId)
    r.execute('git init --bare')
    r.writeFile(R.file_name, name)
    r.writeFile(R.file_status, 'new')

    return r

  def __init__(self, id):
    self.id = id

  def execute(self, command):
    os.system('cd ' + self.id + ' && ' + command)

  # -- Files

  def readFile(self, f):
    try:
      with open(self.id + '/' + f) as descriptor:
        content = descriptor.read()
    except IOError:
      content = ''

    return content.strip()

  def writeFile(self, f, data):
    with open(self.id + '/' + f, 'w') as descriptor:
      descriptor.write(data)

R = Repo = Repository # synonymous classes
