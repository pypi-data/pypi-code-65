from html.parser import HTMLParser
import pathlib

class TagWithSourceParser(HTMLParser):
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self.sources = list()

  def handle_starttag(self, tag, attrs):
    attrs = dict(attrs)
    if 'src' in attrs:
      self.sources.append(pathlib.Path(attrs["src"]))
