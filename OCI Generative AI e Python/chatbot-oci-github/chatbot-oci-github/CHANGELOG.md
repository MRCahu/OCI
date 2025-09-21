# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [4.0.0] - 2025-09-21

### ✨ Adicionado
- **Sistema de Memória Adaptativa**: Implementação da classe `SimpleMemory` com janela deslizante para manter contexto da conversa
- **Integração com APIs Externas**: Conexão com RestCountries API para informações de países em tempo real
- **Detecção Inteligente de Intenções**: Algoritmo que identifica automaticamente quando usar ferramentas externas
- **Agente Inteligente**: Classe `SmartAgent` que orquestra todo o processamento de mensagens
- **Processo de Pensamento Visível**: Interface que mostra como a IA está processando as solicitações
- **Suporte Multilíngue**: Mapeamento de nomes de países em português e inglês

### 🔄 Modificado
- **Interface de Usuário**: Redesign completo com CSS customizado e componentes responsivos
- **Sistema de Personas**: Melhorada a implementação das 4 personas com respostas mais contextuais
- **Arquitetura**: Refatoração completa para arquitetura modular e extensível
- **Performance**: Otimizações de memória e processamento

### 🐛 Corrigido
- **Gerenciamento de Memória**: Correção de vazamentos de memória em conversas longas
- **Tratamento de Erros**: Implementação robusta de fallbacks para falhas de API
- **Responsividade**: Correções na interface para diferentes tamanhos de tela

## [3.0.0] - 2025-09-20

### ✨ Adicionado
- **Sistema de Feedback**: Coleta de avaliações dos usuários com 👍/👎
- **Dashboard de Analytics**: Página dedicada para visualização de métricas
- **Banco de Dados SQLite**: Persistência de feedbacks e histórico
- **4 Estilos de Comunicação**: Formal, Técnico, Simples, Empático

### 🔄 Modificado
- **Sistema de Personas**: Expansão para 4 personas distintas
- **Interface**: Melhorias na navegação e layout

## [2.0.0] - 2025-09-19

### ✨ Adicionado
- **Sistema de Personas**: Professor, Suporte Técnico, Contador de Histórias, Analista
- **Configurações Avançadas**: Controles de temperatura, top-p, max tokens
- **Modo Simulação**: Funcionamento sem credenciais OCI para demonstração

### 🔄 Modificado
- **Interface Streamlit**: Redesign com sidebar e controles avançados
- **Estrutura do Código**: Organização modular das funcionalidades

## [1.0.0] - 2025-09-18

### ✨ Adicionado
- **Chatbot Básico**: Implementação inicial com Streamlit
- **Integração OCI**: Conexão com Oracle Generative AI
- **Interface Simples**: Chat básico funcional
- **Configuração Inicial**: Setup básico do projeto

---

## Tipos de Mudanças

- **✨ Adicionado** para novas funcionalidades
- **🔄 Modificado** para mudanças em funcionalidades existentes
- **🗑️ Removido** para funcionalidades removidas
- **🐛 Corrigido** para correções de bugs
- **🔒 Segurança** para vulnerabilidades corrigidas
