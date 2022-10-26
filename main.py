from ProjectSentenceTransformer import *
import os

if __name__ == "__main__":

    #create embedder
    #embedder = ProjectTransformer('multi-qa-MiniLM-L6-cos-v1')
    #this is a general model that creates higher quality but is slower
    embedder = ProjectTransformer('all-mpnet-base-v2')

    #alternative with lower quality but much faster
    #embedder = ProjectTransformer('all-MiniLM-L6-v2')

    #create encoding of all the .txt files in /txtList
 
    #corpus = 
    corpus = ["My first paragraph. That contains information", "Python is a programming language."]
    
    #main application loop

    #get data from mic
    qeury = "What is Python?"
    
    document_embedding = embedder.doc_encode(qeury)
    q_embedding = embedder.doc_query(qeury)

 

