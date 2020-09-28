import requests
import os
import json
import ast
import uuid
from bs4 import BeautifulSoup
from rdflib import Graph, URIRef, namespace, Namespace, Literal
from datetime import datetime

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

    def write_rdf_annotation(self):

        filename = self.name.replace('.html','')

        self.update_body()

        self.soup = BeautifulSoup(self.body, 'html.parser')
        self.annotations_json = []

        for annotation in self.soup.findAll('annotation'):

            base_uri = 'https://collection.itatti.harvard.edu/yashiro/annotation/'
            wikidata_base_uri = 'https://www.wikidata.org/wiki/'

            xpath = self.xpath_soup(annotation.parent)
            offset =  self.find_str(annotation.parent.text, annotation['text'])

            g = Graph()

            # namespaces
            RDF = namespace.RDF
            XSD = namespace.XSD
            RDFS = namespace.RDFS
            OA = Namespace('http://www.w3.org/ns/oa#')
            CRMDIG = Namespace('http://www.ics.forth.gr/isl/CRMdig/')
            CRM = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
            USER = Namespace('http://www.metaphacts.com/resource/user/')
            PLATFORM = Namespace('http://www.metaphacts.com/ontologies/platform#')
            LDP = Namespace('http://www.w3.org/ns/ldp#')
            PROV = Namespace('http://www.w3.org/ns/prov#')

            # URIs            https://collection.itatti.harvard.edu/resource/yashiro-document:Letter_036
            base_uri_file = f'https://collection.itatti.harvard.edu/resource/yashiro/document/{filename}'
            
            id = str(uuid.uuid1())
            base_node_uri = f'{base_uri}{id}'
            base_node_body_uri = f'{base_node_uri}/body'
            base_node_event_uri = f'{base_uri_file}/annotation-event-{uuid.uuid1()}'
            base_node_event_date_uri = f'{base_node_event_uri}/modifiedAt'

            range_source_uri = f'{base_uri_file}/range-source-{uuid.uuid1()}'
            range_uri = f'{base_uri_file}/range-{uuid.uuid1()}'
            start_selector_uri = f'{base_uri_file}/xpath-{uuid.uuid1()}'
            end_selector_uri = f'{base_uri_file}/xpath-{uuid.uuid1()}'
            
            start_offset_uri = f'{base_uri_file}/offset-{uuid.uuid1()}'
            end_offset_uri = f'{base_uri_file}/offset-{uuid.uuid1()}'

            wikidata_object_uri = f'{wikidata_base_uri}{annotation["wikidata_id"]}'

            BASE_NODE_CONTAINER = URIRef(f'{base_node_uri}/container')

            BASE_NODE = URIRef(base_node_uri)
            BASE_NODE_BODY = URIRef(base_node_body_uri)
            BASE_NODE_EVENT = URIRef(base_node_event_uri)
            BASE_NODE_EVENT_DATE = URIRef(base_node_event_date_uri)
            RANGE_SOURCE = URIRef(range_source_uri)
            RANGE = URIRef(range_uri)

            START_SELECTOR = URIRef(start_selector_uri)
            START_OFFSET = URIRef(start_offset_uri)

            END_SELECTOR = URIRef(end_selector_uri)
            END_OFFSET = URIRef(end_offset_uri)

            LETTER = URIRef(base_uri_file)
            WIKIDATA_OBJECT = URIRef(wikidata_object_uri)

            g.add( (PLATFORM.formContainer, LDP.contains, BASE_NODE_CONTAINER) )

            g.add( (BASE_NODE_CONTAINER, RDF.type, LDP.Resource) )
            g.add( (BASE_NODE_CONTAINER, RDF.type, PROV.Entity) )
            g.add( (BASE_NODE_CONTAINER, PROV.generatedAtTime, Literal(datetime.now().strftime(timestring))) )
            g.add( (BASE_NODE_CONTAINER, PROV.wasAttributedTo, USER.EL_processer) )


            g.add( (BASE_NODE, RDF.type, CRMDIG.D29_Annotation_Object) )
            g.add( (BASE_NODE, RDF.type, OA.Annotation) )
            g.add( (BASE_NODE, CRMDIG.L48i_was_annotation_created_by, BASE_NODE_EVENT) )
            g.add( (BASE_NODE, OA.hasBody, BASE_NODE_BODY) )
            g.add( (BASE_NODE, OA.hasTarget, RANGE_SOURCE) )

            g.add( (BASE_NODE_BODY, CRM.P1_is_identified_by, WIKIDATA_OBJECT) )
            g.add( (BASE_NODE_BODY, RDF.type, CRM.E1_Entity) )

            g.add( (BASE_NODE_EVENT, RDF.type, CRMDIG.D30_Annotation_Event) )
            g.add( (BASE_NODE_EVENT, CRM.P14_carried_out_by, USER.EL_processer) )
            g.add( (BASE_NODE_EVENT, CRM.P4_has_time_span, BASE_NODE_EVENT_DATE) )

            g.add( (BASE_NODE_EVENT_DATE, CRM.P81a_end_of_the_begin, Literal(datetime.now().strftime(timestring))) )
            g.add( (BASE_NODE_EVENT_DATE, CRM.P81b_begin_of_the_end, Literal(datetime.now().strftime(timestring))) )

            g.add( (RANGE_SOURCE, RDF.type, OA.SpecificResource) )
            g.add( (RANGE_SOURCE, RDF.value, Literal(annotation[key_text])) )
            g.add( (RANGE_SOURCE, OA.hasSource, LETTER) )
            g.add( (RANGE_SOURCE, OA.hasSelector, RANGE) )

            g.add( (RANGE, RDF.type, OA.RangeSelector) )
            g.add( (RANGE, OA.hasStartSelector, START_SELECTOR) )
            g.add( (RANGE, OA.hasEndSelector, END_SELECTOR) )

            g.add( (START_SELECTOR, RDF.type, OA.XPathSelector) )
            g.add( (START_SELECTOR, RDF.value, Literal(xpath)) )
            g.add( (START_SELECTOR, OA.refinedBy, START_OFFSET) )

            g.add( (START_OFFSET, RDF.type, OA.TextPositionSelector) )
            g.add( (START_OFFSET, OA.start, Literal(offset, datatype=XSD.nonNegativeInteger)) )
            g.add( (START_OFFSET, OA.end, Literal(offset, datatype=XSD.nonNegativeInteger)) )

            g.add( (END_SELECTOR, RDF.type, OA.XPathSelector) )
            g.add( (END_SELECTOR, RDF.value, Literal(xpath)) )
            g.add( (END_SELECTOR, OA.refinedBy, END_OFFSET) )

            g.add( (END_OFFSET, RDF.type, OA.TextPositionSelector) )
            g.add( (END_OFFSET, OA.start, Literal(offset + int(annotation['end_offset']), datatype=XSD.nonNegativeInteger)) )
            g.add( (END_OFFSET, OA.end, Literal(offset + int(annotation['end_offset']), datatype=XSD.nonNegativeInteger)) ) 

            g.serialize(destination=f'{os.path.join(dir_path, dir_data, dir_rdf, id)}.ttl', format='turtle')

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

    timestring = '%Y-%m-%dT%H:%M:%S'

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
        obj.write_rdf_annotation()
