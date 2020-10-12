import requests
from bs4 import  BeautifulSoup
from tqdm import tqdm
import pickle
import pkg_resources
    
knowledge_base_path = pkg_resources.resource_filename(__name__, 'KB.p')

class Helppy:
  def __init__(self, kb=None):
    self.default_repo = 'https://github.com/vvaezian/Data-Science-Fundamentals'
    self.kb = kb
    self.load_KB()
  
  class Topic:
    def __init__(self, title=None, body='', header_size=None):
      self.title = title
      self.body = body
      self.header_size = header_size  
    
    def add_to_body(self, line):
      self.body += line
  
  
  def load_KB(self):
    '''load the pre-build knowledge-base'''
    self.kb = pickle.load(open(knowledge_base_path, 'rb'))
  
  
  def save_KB(self, kb_name='KB.p'):
    '''Save the KB to the current directory'''
    pickle.dump(self.kb, open(kb_name, 'wb'))
    
    
  def refresh_KB(self, new_repo=None, replace_default_repo=True):
    '''reload the topics of the knowledge-base in case there has been some changes.
       Can also add a new repository to the knowledge-base by passing the new repo url 
       and setting 'replace_default_repo=False'.
    '''
    repository = new_repo if new_repo else self.default_repo
    seachTerms_and_links = self.get_seachTerms_and_links(repository)
    
    kb = {} if replace_default_repo else self.kb
    
    for item in tqdm(seachTerms_and_links):
      search_terms, page_url = item
      topics, page_body = self.process_page(self.get_raw_url(page_url))
      if topics != [] or page_body != '':
        kb[(page_url, search_terms)] = (topics, page_body.lower())
    
    self.kb = kb
    
  
  def find(self, header=None, subject=None, text_in_page=None, results_cap=3):
    '''Search the knowledge-base by providing a keyword that appears in the header of the section,
    or search by providing a keyword that appears in the page.
    In either case can optionally provide a keyword for page name (subject) to limit the search to those pages.
    '''
    if (header is None and text_in_page is None) or (header and text_in_page):
      print("One of 'header' or 'text_in_page' arguments must to be provided.")
      return

    counter = 0
    if header:
      for (url, subjects), (topics, page_body) in self.kb.items():
        if not subject or subject.lower() in subjects:
          for topic in topics:
            if header.lower() in topic.title.lower():
              counter += 1
              print(url + '#' + topic.title.replace(':', '').replace(' ','-') + '\n' + '#' * topic.header_size + ' ' + topic.title + '\n' + topic.body)
              if results_cap != 0 and counter >= results_cap:
                print("\nBy default at most three results are shown. You can change it by passing a different number to the 'results_cap' parameter (pass 0 for no cap).")
                break

    else:  # text_in_page is provided instead of header
      for (url, subjects), (topics, page_body) in self.kb.items():
        if not subject or subject.lower() in subjects:
          if text_in_page.lower() in page_body:
            print(url)


  def get_seachTerms_and_links(self, url, all_page_links=None):

    if all_page_links is None:
      all_page_links = []

    res = requests.get(url)
    soup = BeautifulSoup(res.text)
    rows = soup.findAll('div', {'role':'rowheader'})
    links = [ row.select('a')[0]['href'] for row in rows ]

    dir_links = [ 'https://github.com' + link for link in links if '/tree/' in link ]

    page_links = []
    for link in links:
      if link.endswith('.md') and not link.lower().endswith('readme.md'):
        sections_split = link.split('/')
        sections = sections_split[2].lower().replace('-', ' ') + '/' + '/'.join(sections_split[5:]).lower().rstrip('.md').replace('-', ' ').replace('%20', ' ')
        page_links.append( (sections, 'https://github.com' + link) ) 

    all_page_links.extend(page_links)

    for url in dir_links:
      self.get_seachTerms_and_links(url, all_page_links)

    return all_page_links
  

  @staticmethod          
  def get_raw_url(url):
    sections = url.replace('/blob/', '/').split('/')
    return 'https://raw.githubusercontent.com/' + '/'.join(sections[3:])
  
  
  def process_page(self, url):

    res = requests.get(url).text
    res_lines = res.split('\n')

    topics = []
    any_header_detected_sofar = False
    code_section = False

    for line in res_lines:

      if line.startswith('```'):  # it is start or end of a code section
        # toggle the code_section flag
        code_section = not code_section

      if line.startswith('#') and not code_section:  # new header
        if any_header_detected_sofar:
          # add the previous topic to topics
          topics.append(topic)

        topic = self.Topic()
        topic.header_size = len(line) - len(line.lstrip('#'))
        topic.title = line.strip('#').strip(' ')
        any_header_detected_sofar = True
        continue

      if any_header_detected_sofar:
        topic.add_to_body(line.strip(' ') + '\n')

    # adding the last section
    if any_header_detected_sofar:
      topics.append(topic)

    return topics, res