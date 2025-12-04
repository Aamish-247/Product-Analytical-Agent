import glob
from rank_bm25 import BM25Okapi
import os


DOCS_PATH = os.path.join(os.path.dirname(__file__), "../docs")

if not os.path.exists(DOCS_PATH):
    print(f"Documents path not found at {DOCS_PATH}")

class documents_retriever:
    def __init__(self):
        self.chunks = []
        self.chunk_ids = []
        self.bm25 = None
        self.load_and_index_make()

    def load_and_index_make(self):
        """this function will load all the  documents and create the search index."""

        file  = glob.glob(os.path.join(DOCS_PATH, "*.md"))

        data = []

        for filepath in file:
            file_name = os.path.basename(filepath)
            with open (filepath, "r", encoding="utf-8")as f:
                content = f.read()
            
            raw_chunks = content.split("\n\n")
            for i, chunk in enumerate(raw_chunks):
                if chunk.strip():
                    chunk_id = f"{file_name}_chunk{i}"
                    self.chunks.append({
                        "id": chunk_id,
                        "text": chunk.strip(),
                        "source": file
                    })

                    data.append(chunk.lower().split())

        if data:
            self.bm25 = BM25Okapi(data)            



    def search_query(self, query: str, top_k:int = 3):
        """fetch the top k documents relevant to the  query."""

        if not self.bm25:
            return []
    
        splitted_query = query.lower().split()
        relative_data = self.bm25.get_scores(splitted_query)

        top_k_indices = sorted(range(len(relative_data)), key = lambda i: relative_data[i] ,reverse= True)[:top_k]

        results = []

        for index in top_k_indices:
            if relative_data[index]>0:
                results.append({
                "id": self.chunks[index]["id"],
                "text": self.chunks[index]["text"],
                "score": relative_data[index]            
            })
            
        return results        

retriever = documents_retriever()

def retriever_documents(query: str):
    """retrieve relevant documents for the given query."""
    return retriever.search_query(query)