import requests
import os
import json
import ast
from bs4 import BeautifulSoup

class End2End: 
  
    """Class for End2End"""

    headers = {
      'Content-Type': 'application/json'
    }
  
    def __init__(self, data, name): 
        self.name = name
        self.body = data.get(key_text)

        notes = list(ast.literal_eval(requests.post('http://localhost:5555', json=data, headers=self.headers).text))
        notes.sort()
        notes.reverse()

        self.annotations = notes

    def get_wikidata_id(self, wikipedia_title):
        r = requests.get(f'https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&titles={wikipedia_title}&format=json')

        result = ast.literal_eval(r.text).get('query').get('pages')

        for k, v in result.items():
            return v.get('pageprops').get('wikibase_item')
  
    def get_annotations(self):
        return self.annotations

    def xpath_soup(self, element):
        # type: (typing.Union[bs4.element.Tag, bs4.element.NavigableString]) -> str

        """
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
        """
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:  # type: bs4.element.Tag
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name if 1 == len(siblings) else '%s[%d]' % (child.name,
                    next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
            child = parent
            components.reverse()
        return '/%s' % '/'.join(components)

    #https://stackoverflow.com/questions/21842885/python-find-a-substring-in-a-string-and-returning-the-index-of-the-substring
    def find_str(self, s, char):
        index = 0

        if char in s:
            c = char[0]
            for ch in s:
                if ch == c:
                    if s[index:index+len(char)] == char:
                        return index

            index += 1

        return -1

    def update_body(self):
        for annotation in self.annotations:

            start = annotation[0]
            l = annotation[1]
            end = start + l
            text = body[start:end]

            wikidata_id = self.get_wikidata_id(annotation[2])

            self.body = f'{self.body[:start]}<annotation text="{text}" end_offset="{l}" wikidata_id="{wikidata_id}">{text}</annotation>{self.body[end:]}'

    def get_rdf_annotation(self):

        self.update_body()

        self.soup = BeautifulSoup(self.body, 'html.parser')
        self.annotations_json = []

        for annotation in self.soup.findAll('annotation'):

            self.annotations_json.append({
                'text': annotation['text'],
                'wikidata_id': annotation['wikidata_id'],
                key_start: {
                    key_xpath_selector: self.xpath_soup(annotation.parent),
                    key_text_position_selector: {
                        key_start: self.find_str(annotation.parent.text, annotation['text']),
                        key_end: self.find_str(annotation.parent.text, annotation['text']) + int(annotation['end_offset'])
                    }
                }
            })

        return self.annotations_json

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

    key_text = 'text'
    key_spans = 'spans'

    key_pos = 'pos'
    key_off = 'off'
    key_id = 'id'

    key_start = 'start'
    key_end = 'end'

    key_xpath_selector = 'xpath_selector'
    key_text_position_selector = 'text_position_selector'

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_data = 'data'
    dir_txt = 'txt'
    dir_rdf = 'rdf'

    dir_input = os.path.join(dir_path, dir_data, dir_txt)

    objects = [] 

    for root, dirs, src_files in os.walk(dir_input):
        for filename in src_files:
            with open(os.path.join(dir_input, filename)) as in_f:

                body = bytes(in_f.read(), 'utf-8').decode('utf-8', 'ignore')

                data = {
                    key_text: body,
                    key_spans: []
                }
                    
                End2End = End2End(data=data, name=filename) 
                objects.append(Adapter(End2End, annotations = End2End.get_annotations)) 

    for obj in objects: 
        print(obj.get_rdf_annotation())
