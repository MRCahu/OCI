# 💬 Chatbot OCI v3 - Streamlit Edition

Sistema de conversação inteligente com **memória**, **personas** e **sistema de feedback** integrado, pronto para integração com Oracle Cloud Infrastructure (OCI).

## 🚀 Funcionalidades

### ✨ Principais Recursos
- **4 Personas Distintas**: Professor, Suporte Técnico, Contador de Histórias, Analista
- **4 Estilos de Comunicação**: Formal, Técnico, Simples, Empático
- **Sistema de Memória**: Controle de quantas interações anteriores o bot lembra
- **Parâmetros Ajustáveis**: Temperature, Top-P, Max Tokens
- **Sistema de Feedback**: Avaliação com 👍/👎 e comentários
- **Analytics Dashboard**: Visualizações dos feedbacks coletados
- **Modo Simulação**: Funciona sem credenciais OCI para desenvolvimento

### 🎯 Personas Disponíveis

| Persona | Descrição |
|---------|-----------|
| **Professor** | Explica com exemplos simples e analogias, didático e paciente |
| **Suporte Técnico** | Objetivo, passo a passo, com troubleshooting e validações |
| **Contador de Histórias** | Usa narrativa leve, metáforas e exemplos envolventes |
| **Analista** | Fornece dados estruturados, análise objetiva e insights acionáveis |

### 🎨 Estilos de Comunicação

| Estilo | Características |
|--------|----------------|
| **Formal** | Tom profissional, claro e direto, evita coloquialismos |
| **Técnico** | Usa termos técnicos, listas numeradas e considerações práticas |
| **Simples** | Frases curtas, vocabulário simples, vai direto ao ponto |
| **Empático** | Caloroso, encorajador e demonstra compreensão emocional |

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.8+
- pip

### Passos para Execução

1. **Clone ou baixe os arquivos do projeto**

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**:
   ```bash
   streamlit run app.py
   ```

4. **Acesse no navegador**: `http://localhost:8501`

## ⚙️ Configuração OCI (Opcional)

Para conectar com Oracle Cloud Infrastructure:

1. **Copie o arquivo de exemplo**:
   ```bash
   cp .env.example .env
   ```

2. **Configure as variáveis no arquivo `.env`**:
   ```env
   OCI_ENDPOINT_URL=https://inference.generativeai.us-chicago-1.oci.oraclecloud.com
   OCI_REGION=us-chicago-1
   OCI_COMPARTMENT_OCID=ocid1.compartment.oc1..aaaaaaaaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Desative o "Modo Simulação"** na interface do Streamlit

## 📊 Como Usar

### Página de Chat
1. **Selecione uma Persona** no menu lateral
2. **Escolha um Estilo** de comunicação
3. **Ajuste os parâmetros** do modelo (Temperature, Top-P, etc.)
4. **Digite sua mensagem** e converse com o bot
5. **Avalie as respostas** com 👍 ou 👎
6. **Deixe comentários** para melhorar o sistema

### Página de Analytics
1. **Visualize métricas** de satisfação
2. **Analise distribuição** por personas
3. **Leia comentários** dos usuários
4. **Acompanhe tendências** de uso

## 🗂️ Estrutura do Projeto

```
chatbot_oci/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências Python
├── .env.example       # Exemplo de configuração
├── README.md          # Este arquivo
└── feedback.db        # Banco SQLite (criado automaticamente)
```

## 🔧 Tecnologias Utilizadas

- **Streamlit**: Interface web interativa
- **SQLite**: Banco de dados para feedbacks
- **Plotly**: Visualizações e gráficos
- **Pandas**: Manipulação de dados
- **Pydantic**: Validação de parâmetros

## 📈 Próximos Passos

1. **Integração OCI**: Conectar com Oracle Cloud Infrastructure
2. **Autenticação**: Sistema de login de usuários
3. **Exportação**: Relatórios em PDF/Excel
4. **API REST**: Endpoints para integração externa
5. **Deploy**: Containerização com Docker

## 🤝 Contribuição

Este projeto está pronto para desenvolvimento e pode ser facilmente estendido com novas funcionalidades.

---

**Desenvolvido com ❤️ para demonstrar as capacidades do Streamlit + OCI**
