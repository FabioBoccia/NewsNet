
import nltk
import spacy
from tqdm import tqdm

import spacy_component

nltk.download('punkt')

nlp = spacy.load("en_core_web_sm")

nlp.add_pipe("rebel", after="senter", config={
    'device':-1, # Number of the GPU, -1 if want to use CPU
    'model_name':'Babelscape/rebel-large'} # Model used, will default to 'Babelscape/rebel-large' if not given
    )

def text_to_sentences(texts):
    sentences = []
    for text in texts:
        text_sentences = nltk.tokenize.sent_tokenize(str(text))
        sentences.extend(text_sentences)
    print(f'{len(sentences)} sentences extracted.')
    return sentences

def ner_re(sentences):
    head_entities = []
    tail_entities = []
    relations = []

    for input_sentence in tqdm(sentences):
        doc = nlp(input_sentence)
        for value, rel_dict in doc._.rel.items():
            print(f"{value}: {rel_dict}")
            head_entities.append(rel_dict['head_span'])
            tail_entities.append(rel_dict['tail_span'])
            relations.append(rel_dict['relation'])

    head_entities = [str(entity) for entity in head_entities]
    tail_entities = [str(entity) for entity in tail_entities]
    relations = [str(relation) for relation in relations]

    return head_entities, tail_entities, relations
