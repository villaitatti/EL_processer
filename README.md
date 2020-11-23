# ResearchSpace Entitiy Linking Processor

The ResearchSpace Entity Linking (REL) processer is a python script that calls the Neural Network created with the code from here: https://github.com/dalab/end2end_neural_el.

After the training, it opens a server providing data as described in the repository.

This project takes the html files of projects using the Semantic Digital Publishing functionality of ResearchSpace, makes a POST request for each one against the Wikipedia/Wikidata endpoint to retrieve related entities. I encodes the results in RDF usng the same data model as the Semantic Digital Publishing project, including the exact position of the text that is being annotated. The ResearchSpace platform is then rensponsible for the handling and rendering of the annotations, which can be further refined and edited by users.
