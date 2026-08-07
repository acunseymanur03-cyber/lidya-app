import os
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma

# Hafif ve bağımsız test edilebilir gömme (embedding) ve vektör saklama katmanı
embeddings = FakeEmbeddings(size=128)

def process_and_query_document(document_text: str, question: str) -> str:
    # 1. Metni parçalara böl
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_text(document_text)
    
    if not texts:
        return "Analiz edilecek geçerli metin bulunamadı."
    
    # 2. Vektör veritabanını bellekte oluştur
    vectorstore = Chroma.from_texts(texts, embeddings)
    
    # 3. İlgili doküman parçasını bul (Retrieval)
    docs = vectorstore.similarity_search(question, k=1)
    
    if docs:
        context = docs[0].page_content
        # 4. RAG yanıt sentezi (Generation simülasyonu / LLM yanıtı)
        return f"[RAG Yanıtı] Bulunan İlgili Bağlam: '{context}' | Soru: '{question}'"
    
    return "Doküman içerisinde bu soruya uygun bir yanıt bulunamadı."
