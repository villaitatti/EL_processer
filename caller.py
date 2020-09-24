import requests
import os
import json
import ast
from bs4 import BeautifulSoup
from rdflib import Graph, URIRef, namespace, Namespace, Literal

class End2End: 
  
    """Class for End2End"""

    headers = {
      'Content-Type': 'application/json'
    }
  
    def __init__(self, data): 
        self.name = "e2e"
        self.data = data
  
    def annotations(self): 
        return list(ast.literal_eval(requests.post('http://localhost:5555', json=self.data, headers=self.headers).text))
  
  
class Adapter: 
    """ 
    Adapts an object by replacing methods. 
    Usage: 
    End2End = End2End() 
    End2End = Adapter(End2End, annotations = End2End.annotations) 
    """
  
    def __init__(self, obj, **adapted_methods): 
        """We set the adapted methods in the object's dict"""
        self.obj = obj 
        self.__dict__.update(adapted_methods) 
  
    def __getattr__(self, attr): 
        """All non-adapted calls are passed to the object"""
        return getattr(self.obj, attr) 
  
    def original_dict(self): 
        """Print original object dict"""
        return self.obj.__dict__ 
  
  
""" main method """
if __name__ == "__main__": 
  
  """list to store objects"""
  objects = [] 

  End2End = End2End(data={'text':'Obama will visit Germany and have a meeting with Merkel tomorrow.','spans':[]}) 
  objects.append(Adapter(End2End, annotations = End2End.annotations)) 

  for obj in objects: 
    print(obj.annotations())

"""
def get_wikidata_id(wikipedia_title):
r = requests.get(f'https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&titles={wikipedia_title}&format=json')

result = ast.literal_eval(r.text).get('query').get('pages')

for k, v in result.items():
return v.get('pageprops').get('wikibase_item')

#https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf
def xpath_soup(element):
# type: (typing.Union[bs4.element.Tag, bs4.element.NavigableString]) -> str

Generate xpath from BeautifulSoup4 element.
:param element: BeautifulSoup4 element.
:type element: bs4.element.Tag or bs4.element.NavigableString
:return: xpath as string
:rtype: str
Usage
-----
>>> import bs4
>>> html = (
...     '<html><head><title>title</title></head>'
...     '<body><p>p <i>1</i></p><p>p <i>2</i></p></body></html>'
...     )
>>> soup = bs4.BeautifulSoup(html, 'html.parser')
>>> xpath_soup(soup.html.body.p.i)
'/html/body/p[1]/i'
>>> import bs4
>>> xml = '<doc><elm/><elm/></doc>'
>>> soup = bs4.BeautifulSoup(xml, 'lxml-xml')
>>> xpath_soup(soup.doc.elm.next_sibling)
'/doc/elm[2]'
components = []
child = element if element.name else element.parent
for parent in child.parents:  # type: bs4.element.Tag
siblings = parent.find_all(child.name, recursive=False)
components.append(
child.name if 1 == len(siblings) else '%s[%d]' % (
child.name,
next(i for i, s in enumerate(siblings, 1) if s is child)
)
)
child = parent
components.reverse()
return '/%s' % '/'.join(components)

#https://stackoverflow.com/questions/21842885/python-find-a-substring-in-a-string-and-returning-the-index-of-the-substring
def find_str(s, char):
index = 0

if char in s:
c = char[0]
for ch in s:
if ch == c:
if s[index:index+len(char)] == char:
  return index

index += 1

return -1

def create_rdf(annotation):
g = Graph()

BASE_NODE = URIRef()

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_data = 'data'
dir_txt = 'txt'
dir_rdf = 'rdf'

dir_input = os.path.join(dir_path, dir_data, dir_txt)

key_text = 'text'
key_spans = 'spans'

key_pos = 'pos'
key_off = 'off'
key_id = 'id'

key_start = 'start'
key_end = 'end'

key_xpath_selector = 'xpath_selector'
key_text_position_selector = 'text_position_selector'

for root, dirs, src_files in os.walk(dir_input):
for filename in src_files:
with open(os.path.join(dir_input, filename)) as in_f:
body = in_f.read()

body = bytes(body, 'utf-8').decode('utf-8', 'ignore')

data = {
key_text: body,
key_spans: []
}

r = requests.post(url, json=data, headers=headers)

# Reverse the annotations
annotations = list(ast.literal_eval(r.text))
annotations.sort()
annotations.reverse()

for annotation in annotations:
start = annotation[0]
l = annotation[1]
end = start + l

text = body[start:end]

wikidata_id = get_wikidata_id(annotation[2])

body = f'{body[:start]}<annotation text="{text}" end_offset="{l}" wikidata_id="{wikidata_id}">{text}</annotation>{body[end:]}'


soup = BeautifulSoup(body, 'html.parser')

annotations_json = []

for annotation in soup.findAll('annotation'):

annotations_json.append({
'text':annotation['text'],
'wikidata_id':annotation['wikidata_id'],
key_start: {
key_xpath_selector: xpath_soup(annotation.parent),
key_text_position_selector: {
key_start: find_str(annotation.parent.text, annotation['text']),
key_end: find_str(annotation.parent.text, annotation['text']) + int(annotation['end_offset'])
}
}
})

print(annotations_json)

with open(os.path.join(dir_path, dir_data, dir_rdf, filename), 'w') as out_f:
out_f.write(str(soup))
"""