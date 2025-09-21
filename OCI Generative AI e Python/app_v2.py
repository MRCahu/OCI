import os
import sqlite3
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.llms.oci_generative_ai import OCIAuthType
from langchain_core.language_models.llms import LLM

# =========================
# Configuração Inicial
# =========================
load_dotenv()
st.set_page_config(
    page_title="OCI Chatbot v4 — LangChain, Tools & Memória Avançada",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .small { font-size: 0.85rem; color: #666; }
    .bubble-user { background: #e1f5fe; padding: 0.8rem 1rem; border-radius: 1rem 1rem 0 1rem; margin: 0.5rem 0; border: 1px solid #bbdefb; }
    .bubble-bot { background: #f3e5f5; padding: 0.8rem 1rem; border-radius: 1rem 1rem 1rem 0; margin: 0.5rem 0; border: 1px solid #e1bee7; }
    .tag { display:inline-block; padding: 4px 10px; border-radius: 12px; background:#f1f5f9; margin-right:8px; font-size: 0.8rem; border: 1px solid #e2e8f0; }
    .metrics { background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border: 1px solid #e2e8f0; }
    .stButton button { width: 100%; background-color: #4f46e5; color: white; }
    .thought-bubble { background: #fffbe6; border: 1px solid #ffe58f; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; font-family: monospace; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# =========================
# Personas & Estilos
# =========================
PERSONAS = {
    "Professor": "Explique com exemplos simples e analogias, seja didático e paciente.",
    "Suporte Técnico": "Seja objetivo, passo a passo, com troubleshooting e validações.",
    "Contador de Histórias": "Use narrativa leve, metáforas curtas e exemplos envolventes.",
    "Analista": "Forneça dados estruturados, análise objetiva e insights acionáveis."
}

STYLES = {
    "Formal": "Escreva em tom profissional, claro e direto, evitando coloquialismos.",
    "Técnico": "Use termos técnicos quando necessário, inclua listas numeradas e considerações práticas.",
    "Simples": "Frases curtas, vocabulário simples, vá direto ao ponto.",
    "Empático": "Seja caloroso, encorajador e demonstre compreensão emocional."
}

# =========================
# Ferramenta de API Externa (Country Info)
# =========================
def get_country_info(country_name: str) -> str:
    """Busca informações sobre um país específico, como capital, população e região. Use esta ferramenta quando o usuário perguntar sobre dados de um país."""
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}?fields=name,capital,population,region,subregion")
        response.raise_for_status()
        data = response.json()[0]
        return f"Informações sobre {data['name']['common']}:\n- Capital: {data['capital'][0]}\n- População: {data['population']:,}\n- Região: {data['region']} ({data['subregion']})"
    except Exception as e:
        return f"Não foi possível obter informações para '{country_name}'. Verifique o nome e tente novamente. Erro: {e}"

# Criar a ferramenta usando a classe Tool
country_tool = Tool(
    name="get_country_info",
    description="Busca informações sobre um país específico, como capital, população e região. Use esta ferramenta quando o usuário perguntar sobre dados de um país.",
    func=get_country_info
)

tools = [country_tool]

# =========================
# LLM Customizado (Modo Simulação)
# =========================
class MockOCI(LLM):
    @property
    def _llm_type(self) -> str:
        return "mock_oci"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        # Extrai a última pergunta do usuário do prompt complexo do agente
        user_last_question = prompt.split("Pergunta:")[-1].strip()

        # Verifica se a pergunta é sobre um país
        if "brasil" in user_last_question.lower() or "france" in user_last_question.lower() or "japan" in user_last_question.lower():
            return """
            Pensamento: O usuário está perguntando sobre um país. Devo usar a ferramenta `get_country_info`.
            Ação: get_country_info
            Entrada da Ação: Brasil
            """
        else:
            return f"""
            Pensamento: O usuário está fazendo uma pergunta geral. Não preciso de ferramentas.
            Resposta Final: Entendi sua pergunta sobre '{user_last_question}'. Como um modelo de linguagem avançado, posso ajudar com informações gerais, mas para dados em tempo real, minhas ferramentas são mais úteis.
            """

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": "mock_oci_v1"}

# =========================
# Sistema de Banco de Dados (sem alterações)
# =========================
def init_db():
    conn = sqlite3.connect('feedback_v2.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, timestamp TEXT, persona TEXT, style TEXT, rating TEXT, comment TEXT, user_msg TEXT, assistant_msg TEXT)')
    conn.commit()
    conn.close()

def save_feedback_db(feedback_data: Dict[str, Any]):
    conn = sqlite3.connect('feedback_v2.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (timestamp, persona, style, rating, comment, user_msg, assistant_msg) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (feedback_data.get("timestamp"), feedback_data.get("persona"), feedback_data.get("style"), feedback_data.get("rating"),
               feedback_data.get("comment"), feedback_data.get("user_msg"), feedback_data.get("assistant_msg")))
    conn.commit()
    conn.close()

def get_feedback_data():
    conn = sqlite3.connect('feedback_v2.db')
    df = pd.read_sql_query("SELECT * FROM feedback", conn)
    conn.close()
    return df

# =========================
# Página Principal do Chat (com LangChain)
# =========================
def main_chat_page():
    st.sidebar.title("⚙️ Configurações Avançadas")
    persona = st.sidebar.selectbox("Persona", list(PERSONAS.keys()), index=0)
    style = st.sidebar.selectbox("Estilo", list(STYLES.keys()), index=0)

    st.sidebar.markdown("---")
    st.sidebar.info("✅ LangChain e Tools integrados!")

    # UI - Cabeçalho
    st.title("🧠 Chatbot OCI v4")
    st.caption("Agora com LangChain, Memória Avançada e Ferramentas de API Externa")

    # Inicializar estado da sessão para LangChain
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferWindowMemory(
            k=5, memory_key="chat_history", return_messages=True
        )

    # Constrói o prompt do sistema
    system_prompt_text = f"""Você é um assistente especializado com foco em {persona}.
    Persona: {PERSONAS[persona]}
    Estilo: {style}. {STYLES[style]}
    Regras: Responda em PT-BR. Seja útil e honesto. Use suas ferramentas quando necessário."""

    # Configuração do Agente LangChain
    llm = MockOCI()
    prompt = PromptTemplate.from_template(
        f"""{system_prompt_text}

Você tem acesso às seguintes ferramentas:
{{tools}}

Use o seguinte formato:

Pergunta: a pergunta de entrada que você deve responder
Pensamento: você deve sempre pensar sobre o que fazer
Ação: a ação a ser tomada, deve ser uma de [{{tool_names}}]
Entrada da Ação: a entrada para a ação
Observação: o resultado da ação
... (este Pensamento/Ação/Entrada da Ação/Observação pode se repetir N vezes)
Pensamento: Agora sei a resposta final
Resposta Final: a resposta final para a pergunta original

Comece!

{{chat_history}}

Pergunta: {{input}}
Pensamento: {{agent_scratchpad}}"""
    )
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=st.session_state.memory, verbose=True, handle_parsing_errors=True)

    # Botão para limpar memória
    if st.button("🗑️ Limpar Memória da Conversa", use_container_width=True):
        st.session_state.memory.clear()
        st.rerun()

    # Renderizar histórico de conversa da memória LangChain
    for msg in st.session_state.memory.chat_memory.messages:
        if msg.type == "human":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(f'<div class="bubble-user">{msg.content}</div>', unsafe_allow_html=True)
        elif msg.type == "ai":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f'<div class="bubble-bot">{msg.content}</div>', unsafe_allow_html=True)

    # Entrada do usuário
    user_msg = st.chat_input("Pergunte sobre um país ou converse normalmente...")
    if user_msg:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f'<div class="bubble-user">{user_msg}</div>', unsafe_allow_html=True)

        with st.spinner("🤖 Pensando e usando ferramentas..."):
            try:
                response = agent_executor.invoke({"input": user_msg})
                assistant_text = response["output"]

                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f'<div class="bubble-bot">{assistant_text}</div>', unsafe_allow_html=True)

                # Mostra o "pensamento" do agente
                with st.expander("Ver o processo de pensamento do Agente", expanded=False):
                    st.markdown(f'<div class="thought-bubble">{response}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ Erro ao executar o agente: {e}")

# =========================
# Página de Analytics (sem alterações)
# =========================
def analytics_page():
    st.title("📊 Analytics - Feedback do Chatbot v4")
    df = get_feedback_data()
    if df.empty:
        st.info("📝 Ainda não há dados de feedback coletados.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    total_feedbacks = len(df)
    positive_feedbacks = len(df[df['rating'] == '👍'])
    satisfaction_rate = (positive_feedbacks / total_feedbacks * 100) if total_feedbacks > 0 else 0

    st.metric("Taxa de Satisfação Geral", f"{satisfaction_rate:.1f}%")
    st.dataframe(df)

# =========================
# App principal
# =========================
def main():
    init_db()
    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Selecione a página:", ["💬 Chat Avançado", "📊 Analytics"])

    if page == "💬 Chat Avançado":
        main_chat_page()
    elif page == "📊 Analytics":
        analytics_page()

if __name__ == "__main__":
    main()

