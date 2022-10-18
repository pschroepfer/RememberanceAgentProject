from ProjectSentenceTransformer import *

if __name__ == "__main__":


    #example of doing sentence encoding, 
    # TODO we need to add the other packages here to do the data processing and loading first
    d = ["My first paragraph. That contains information", "Python is a programming language."]
    q = "What is Python?"
    s = ProjectTransformer('multi-qa-MiniLM-L6-cos-v1')
    document_embedding = s.doc_encode(d)
    q_embedding = s.doc_query(q)
    print(q_embedding)
