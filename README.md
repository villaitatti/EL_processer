# EL_processer

Entity Linking (EL) processer is a python script that calls the Neural Network created with the code in https://github.com/dalab/end2end_neural_el.

The core EL code has been downloaded and executed. After the training, it opens a server providing data as described in the repository.

This project takes the html file of the letters in the [Yashiro website](https://collection.itatti.harvard.edu/resource/yashiro:Letters?semanticSearch=N4IgZiBcDaC6A0IBOBTAzgVwDYBcrAF9EATAQx1LRRzSjkVKwEsBzAOwFsU29JQAVKCAAi5UgDoAsqQCeAIxQhEANXwEiIFklIAHABYBlAMYB7HSgMpSSI3vwhBkEWKmyFSkKr7qCQA) and for each of them, the code makes a POST request for having back 
the list of entities, disambiguated against Wikipedia.

Each annotation is then manipulated and converted into RDF, which is compliant to the Researchspace (RS) instance where the yashiro letters are stored. The RS 
environment is rensponsible of handling the rendering for the annotations.
