from .models import Document, Risk

from workflows.search import search_by_name

def search_documents(search, similarity_threshold=0.38, rank_threshold=0.05):
    return search_by_name(Document, search, similarity_threshold=similarity_threshold, rank_threshold=rank_threshold)

def search_risks(search, similarity_threshold=0.38, rank_threshold=0.05):
    return search_by_name(Risk, search, similarity_threshold=similarity_threshold, rank_threshold=rank_threshold)
