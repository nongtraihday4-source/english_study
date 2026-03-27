import os
from django.conf import settings
from decouple import config
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.chat_models import ChatOllama # Deprecated for Cloud
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv() # Load .env file

class GrammarAnalysisService:
    _instance = None
    _qa_chain = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._initialize_chain()

    def _initialize_chain(self):
        """
        Initialize the RAG chain with ChromaDB and Ollama.
        This is done lazily or on startup.
        """
        print("DEBUG: Starting _initialize_chain...")
        # 1. Path to Vector DB
        chroma_db_path = os.path.join(settings.BASE_DIR, 'chroma_db')
        print(f"DEBUG: Checking ChromaDB path: {chroma_db_path}")
        
        if not os.path.exists(chroma_db_path):
            print(f"WARNING: ChromaDB not found at {chroma_db_path}")
            self._qa_chain = None
            return

        # 2. Embeddings (Must match what was used in Colab)
        print("DEBUG: Loading HuggingFaceEmbeddings...")
        embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("DEBUG: Embeddings loaded.")

        # 3. Load Vector DB
        print("DEBUG: Loading ChromaDB...")
        db = Chroma(
            persist_directory=chroma_db_path, 
            embedding_function=embedding_function
        )
        retriever = db.as_retriever(search_kwargs={"k": 3})
        print("DEBUG: ChromaDB loaded.")

        # 4. LLM (Google Gemini)
        # Replacing Ollama with Gemini 1.5 Flash for speed and free tier usage
        print("DEBUG: Initializing ChatGoogleGenerativeAI (Gemini 1.5 Flash)...")
        google_api_key = config('GOOGLE_API_KEY', default=os.getenv('GOOGLE_API_KEY'))
        
        if not google_api_key:
            print("ERROR: GOOGLE_API_KEY not found in .env or environment variables!")
            self._qa_chain = None
            return

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=google_api_key,
            temperature=0.3,
            convert_system_message_to_human=True # Sometimes needed for older chains
        )
        print("DEBUG: ChatGoogleGenerativeAI initialized.")

        # 5. Prompt
        prompt_template = """Use the following pieces of context to explain the grammar question at the end.
        If you don't know the answer from the context, just say that you don't know, don't try to make up an answer.
        Use Vietnamese to explain.

        CONTEXT:
        {context}

        QUESTION:
        {question}

        EXPLANATION (in Vietnamese):"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )

        # 6. Chain
        print("DEBUG: Creating RetrievalQA chain...")
        self._qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        print("DEBUG: Chain created successfully.")

    def analyze_text(self, query):
        """
        Analyze the query using the RAG chain.
        Returns: { 'result': str, 'sources': list }
        """
        if not self._qa_chain:
            self._initialize_chain()
            if not self._qa_chain:
                return {
                    "result": "Hệ thống chưa tìm thấy cơ sở dữ liệu ngữ pháp (chroma_db). Vui lòng kiểm tra lại cấu hình.",
                    "sources": []
                }

        try:
            response = self._qa_chain.__call__({"query": query})
            
            result_text = response['result']
            sources = []
            for doc in response['source_documents']:
                sources.append({
                    'source': os.path.basename(doc.metadata.get('source', '')),
                    'page': doc.metadata.get('page', 0)
                })
            
            return {
                "result": result_text,
                "sources": sources
            }
        except Exception as e:
            return {
                "result": f"Đã có lỗi xảy ra khi xử lý: {str(e)}",
                "sources": []
            }
