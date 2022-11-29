from sentence_transformers import SentenceTransformer

class Transformer():
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def doc_encode(self, docs):
        return self.model.encode(docs)
