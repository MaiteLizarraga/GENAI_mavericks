from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Crear embeddings de descripciones de propiedades
def create_vector_store(docs):
    embeddings = OpenAIEmbeddings()
    store = FAISS.from_texts(docs, embeddings)
    return store

def search_similar(store, query):
    return store.similarity_search(query)
