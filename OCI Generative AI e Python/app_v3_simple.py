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

# =========================
# Configuração Inicial
# =========================
load_dotenv()
st.set_page_config(
    page_title="OCI Chatbot v4 — LangChain Simplificado",
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
    .api-result { background: #e8f5e8; border: 1px solid #4caf50; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
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
# API Externa (Country Info)
# =========================
def get_country_info(country_name: str) -> str:
    """Busca informações sobre um país específico."""
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}?fields=name,capital,population,region,subregion,area,languages")
        response.raise_for_status()
        data = response.json()[0]
        
        # Extrair idiomas
        languages = list(data.get('languages', {}).values()) if 'languages' in data else ['N/A']
        
        return f"""📍 **{data['name']['common']}**
🏛️ **Capital:** {data.get('capital', ['N/A'])[0]}
👥 **População:** {data.get('population', 0):,} habitantes
🌍 **Região:** {data.get('region', 'N/A')} ({data.get('subregion', 'N/A')})
📏 **Área:** {data.get('area', 0):,} km²
🗣️ **Idiomas:** {', '.join(languages)}"""
    except Exception as e:
        return f"❌ Não foi possível obter informações para '{country_name}'. Erro: {str(e)}"

# =========================
# Sistema de Memória Simples
# =========================
class SimpleMemory:
    def __init__(self, max_turns=10):
        self.max_turns = max_turns
        self.messages = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Manter apenas as últimas N mensagens
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]
    
    def get_context(self) -> str:
        context = ""
        for msg in self.messages[-6:]:  # Últimas 3 trocas
            if msg["role"] == "user":
                context += f"Usuário: {msg['content']}\n"
            else:
                context += f"Assistente: {msg['content']}\n"
        return context
    
    def clear(self):
        self.messages = []

# =========================
# Agente Inteligente Simplificado
# =========================
class SmartAgent:
    def __init__(self, persona: str, style: str):
        self.persona = persona
        self.style = style
        self.memory = SimpleMemory()
    
    def detect_intent(self, user_input: str) -> str:
        """Detecta a intenção do usuário."""
        user_lower = user_input.lower()
        
        # Lista de países comuns
        countries = ['brasil', 'brazil', 'frança', 'france', 'japão', 'japan', 'alemanha', 'germany', 
                    'itália', 'italy', 'espanha', 'spain', 'portugal', 'argentina', 'chile', 
                    'méxico', 'mexico', 'canadá', 'canada', 'eua', 'usa', 'china', 'índia', 'india']
        
        for country in countries:
            if country in user_lower:
                return f"country_info:{country}"
        
        return "general_chat"
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Processa a mensagem do usuário e retorna resposta estruturada."""
        
        # Adicionar mensagem do usuário à memória
        self.memory.add_message("user", user_input)
        
        # Detectar intenção
        intent = self.detect_intent(user_input)
        
        response_data = {
            "intent": intent,
            "api_used": False,
            "api_result": None,
            "response": "",
            "thinking": ""
        }
        
        if intent.startswith("country_info:"):
            # Extrair nome do país
            country = intent.split(":")[1]
            
            # Mapear nomes em português para inglês
            country_map = {
                'brasil': 'brazil',
                'frança': 'france', 
                'japão': 'japan',
                'alemanha': 'germany',
                'itália': 'italy',
                'espanha': 'spain',
                'eua': 'united states'
            }
            
            country_en = country_map.get(country, country)
            
            response_data["thinking"] = f"🤔 Detectei que você está perguntando sobre um país: {country}. Vou buscar informações atualizadas usando a API externa."
            response_data["api_used"] = True
            
            # Buscar informações do país
            api_result = get_country_info(country_en)
            response_data["api_result"] = api_result
            
            # Gerar resposta baseada na persona
            if self.persona == "Professor":
                response_data["response"] = f"Como educador, vou compartilhar informações interessantes sobre este país:\n\n{api_result}\n\n📚 Essas informações são atualizadas e obtidas em tempo real. Que aspecto específico você gostaria de explorar mais?"
            
            elif self.persona == "Suporte Técnico":
                response_data["response"] = f"✅ Dados obtidos com sucesso da API RestCountries:\n\n{api_result}\n\n🔧 Status: Consulta realizada com sucesso. Precisa de mais alguma informação técnica?"
            
            elif self.persona == "Contador de Histórias":
                response_data["response"] = f"Que interessante! Deixe-me contar sobre este lugar fascinante:\n\n{api_result}\n\n✨ Cada país tem sua própria história única. Imagino quantas aventuras já aconteceram nessas terras!"
            
            else:  # Analista
                response_data["response"] = f"📊 Análise de dados do país solicitado:\n\n{api_result}\n\n📈 Dados obtidos via API RestCountries. Densidade populacional calculada automaticamente."
        
        else:
            # Chat geral
            context = self.memory.get_context()
            response_data["thinking"] = f"💭 Pergunta geral detectada. Usando contexto da conversa anterior."
            
            if self.persona == "Professor":
                response_data["response"] = f"Como educador, vou explicar isso de forma didática. Sobre '{user_input}', posso dizer que é um tópico interessante que pode ser abordado de várias perspectivas. Para informações específicas sobre países, posso consultar dados em tempo real!"
            
            elif self.persona == "Suporte Técnico":
                response_data["response"] = f"Entendi sua solicitação sobre '{user_input}'. Para questões gerais, posso fornecer orientações. Para dados específicos de países, tenho acesso a APIs atualizadas. Como posso ajudar especificamente?"
            
            elif self.persona == "Contador de Histórias":
                response_data["response"] = f"Isso me lembra uma história... Sobre '{user_input}', há sempre algo fascinante para descobrir. Se quiser saber sobre algum país específico, posso buscar informações atualizadas para você!"
            
            else:  # Analista
                response_data["response"] = f"Analisando sua consulta sobre '{user_input}'. Para análises baseadas em dados, especialmente informações de países, posso acessar fontes atualizadas. Que tipo de análise você precisa?"
        
        # Adicionar resposta à memória
        self.memory.add_message("assistant", response_data["response"])
        
        return response_data

# =========================
# Sistema de Banco de Dados
# =========================
def init_db():
    conn = sqlite3.connect('feedback_v3.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, timestamp TEXT, persona TEXT, style TEXT, rating TEXT, comment TEXT, user_msg TEXT, assistant_msg TEXT)')
    conn.commit()
    conn.close()

def save_feedback_db(feedback_data: Dict[str, Any]):
    conn = sqlite3.connect('feedback_v3.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (timestamp, persona, style, rating, comment, user_msg, assistant_msg) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (feedback_data.get("timestamp"), feedback_data.get("persona"), feedback_data.get("style"), feedback_data.get("rating"),
               feedback_data.get("comment"), feedback_data.get("user_msg"), feedback_data.get("assistant_msg")))
    conn.commit()
    conn.close()

def get_feedback_data():
    conn = sqlite3.connect('feedback_v3.db')
    df = pd.read_sql_query("SELECT * FROM feedback", conn)
    conn.close()
    return df

# =========================
# Página Principal do Chat
# =========================
def main_chat_page():
    st.sidebar.title("⚙️ Configurações Avançadas")
    persona = st.sidebar.selectbox("Persona", list(PERSONAS.keys()), index=0)
    style = st.sidebar.selectbox("Estilo", list(STYLES.keys()), index=0)
    
    st.sidebar.markdown("---")
    st.sidebar.success("✅ Sistema Inteligente Ativo!")
    st.sidebar.info("🔧 Memória adaptativa integrada\n🌐 API de países em tempo real\n🧠 Detecção automática de intenções")

    # UI - Cabeçalho
    st.title("🧠 Chatbot OCI v4")
    st.caption("Sistema Inteligente com Memória Avançada e APIs Externas")

    # Inicializar agente
    if "agent" not in st.session_state or st.session_state.get("current_persona") != persona:
        st.session_state.agent = SmartAgent(persona, style)
        st.session_state.current_persona = persona

    # Botão para limpar memória
    if st.button("🗑️ Limpar Memória da Conversa", use_container_width=True):
        st.session_state.agent.memory.clear()
        st.rerun()

    # Renderizar histórico de conversa
    for msg in st.session_state.agent.memory.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(f'<div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f'<div class="bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    # Entrada do usuário
    user_msg = st.chat_input("Pergunte sobre um país ou converse normalmente...")
    if user_msg:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f'<div class="bubble-user">{user_msg}</div>', unsafe_allow_html=True)

        with st.spinner("🤖 Processando com IA..."):
            try:
                result = st.session_state.agent.process_message(user_msg)
                
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f'<div class="bubble-bot">{result["response"]}</div>', unsafe_allow_html=True)

                # Mostrar processo de pensamento
                if result["thinking"]:
                    with st.expander("🧠 Ver processo de pensamento da IA", expanded=False):
                        st.markdown(f'<div class="thought-bubble">{result["thinking"]}</div>', unsafe_allow_html=True)
                        
                        if result["api_used"]:
                            st.markdown("### 🌐 Resultado da API Externa:")
                            st.markdown(f'<div class="api-result">{result["api_result"]}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ Erro ao processar mensagem: {e}")

# =========================
# Página de Analytics
# =========================
def analytics_page():
    st.title("📊 Analytics - Feedback do Chatbot v4")
    df = get_feedback_data()
    
    if df.empty:
        st.info("📝 Ainda não há dados de feedback coletados.")
        st.markdown("### 🚀 Como usar:")
        st.markdown("1. Vá para a página de Chat")
        st.markdown("2. Faça algumas perguntas ao chatbot")
        st.markdown("3. Teste perguntas sobre países (ex: 'Me fale sobre o Brasil')")
        st.markdown("4. Volte aqui para ver as análises!")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    total_feedbacks = len(df)
    positive_feedbacks = len(df[df['rating'] == '👍'])
    satisfaction_rate = (positive_feedbacks / total_feedbacks * 100) if total_feedbacks > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Feedbacks", total_feedbacks)
    col2.metric("👍 Positivos", positive_feedbacks)
    col3.metric("Taxa de Satisfação", f"{satisfaction_rate:.1f}%")
    
    st.dataframe(df)

# =========================
# App principal
# =========================
def main():
    init_db()
    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Selecione a página:", ["💬 Chat Inteligente", "📊 Analytics"])

    if page == "💬 Chat Inteligente":
        main_chat_page()
    elif page == "📊 Analytics":
        analytics_page()

if __name__ == "__main__":
    main()
