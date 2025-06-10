import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or (_ for _ in ()).throw(ValueError("GEMINI_API_KEY ausente"))
genai.configure(api_key=api_key)

mentor = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.8, google_api_key=api_key)
guardiao = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.4, google_api_key=api_key)
embedder = GoogleGenerativeAIEmbeddings(google_api_key=api_key, model="models/embedding-001")

prompt_mentor = """
Você é o Sábio Howl, uma entidade encantada que guia visitantes pelo universo dos filmes do Studio Ghibli.

Ao responder:

1. Fale como se fosse Howl, com um tom poético, elegante, acolhedor e sábio.
2. Sempre que possível, mencione de onde vem a informação (filme, cena, personagem, evento).
3. Reconheça com simpatia quando alguém se dirigir a você como “Howl”, mesmo que você seja apenas uma representação virtual dele.
4. Se a pergunta for vaga ou se a resposta não estiver nos registros, diga algo como:
   “Ah... Essa memória talvez esteja escondida entre os ventos do castelo. Tente perguntar de outro modo ou me dar mais pistas.”

Adicione um toque encantado ao final da resposta, como:
“Que os espíritos do vento e do tempo guiem sua próxima pergunta.”
""".strip()


prompt_guardiao = """
Você é o Guardião Totoro. Avalie cada resposta:
1) Fidelidade ao cânone (0–10)
2) Clareza (0–10)
3) Uso de referências a filmes (0–10)
4) Contexto cultural (0–10)
5) Valor para iniciantes e fãs (0–10)

📜 Registro do Totoro  
Aprovado 🌿 / Revisar 🍂  

🍄 Pontuação Final: X/10

Detalhes:
- Fidelidade: X
- Clareza: X
- Referências: X
- Contexto: X
- Valor: X

Comentário resumido e sugestões práticas.
""".strip()

def build_rag(corpus_folder: str):
    base = os.path.dirname(__file__)
    folder = os.path.join(base, corpus_folder)
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"{corpus_folder} não encontrado")
    docs = []
    for fname in os.listdir(folder):
        if fname.lower().endswith(".txt"):
            docs.extend(TextLoader(os.path.join(folder, fname), encoding="utf-8").load())
    splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    index = FAISS.from_documents(chunks, embedder)
    return RetrievalQA.from_chain_type(llm=mentor, retriever=index.as_retriever(), return_source_documents=True)

RAG = build_rag("BaseGhibli")

def responder(pergunta: str) -> str:
    documentos_relevantes = RAG.retriever.get_relevant_documents(pergunta)
    contexto = "\n".join(doc.page_content for doc in documentos_relevantes)

    mensagens_howl = [
        SystemMessage(content=prompt_mentor),
        HumanMessage(content=f"Documentos de apoio:\n{contexto}\n\nPergunta: {pergunta}")
    ]

    resposta_texto = mentor.invoke(mensagens_howl).content.strip()

    fontes = [doc.metadata.get("source", "") for doc in documentos_relevantes]

    mensagens_totoro = [
        SystemMessage(content=prompt_guardiao),
        HumanMessage(content=f"Pergunta: {pergunta}\nResposta: {resposta_texto}\nFontes: {', '.join(fontes)}")
    ]

    avaliacao = guardiao.invoke(mensagens_totoro).content.strip()

    return "\n".join([
        "📚 Resposta do Howl:",
        resposta_texto,
        "",
        "👨‍⚖️ Avaliação do Totoro:",
        avaliacao,
        ""
    ])