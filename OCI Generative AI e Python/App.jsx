import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { MessageCircle, Settings, BarChart3, ThumbsUp, ThumbsDown, Send, Trash2, Bot, User } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

// Configurações das personas e estilos
const PERSONAS = {
  "Professor": "Explique com exemplos simples e analogias, seja didático e paciente.",
  "Suporte Técnico": "Seja objetivo, passo a passo, com troubleshooting e validações.",
  "Contador de Histórias": "Use narrativa leve, metáforas curtas e exemplos envolventes.",
  "Analista": "Forneça dados estruturados, análise objetiva e insights acionáveis."
}

const STYLES = {
  "Formal": "Escreva em tom profissional, claro e direto, evitando coloquialismos.",
  "Técnico": "Use termos técnicos quando necessário, inclua listas numeradas e considerações práticas.",
  "Simples": "Frases curtas, vocabulário simples, vá direto ao ponto.",
  "Empático": "Seja caloroso, encorajador e demonstre compreensão emocional."
}

// Simulador de cliente OCI
class OCIClient {
  constructor(mode = "mock") {
    this.mode = mode
  }

  async generate(messages, params) {
    // Simular delay de API
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    
    const userLast = messages.filter(m => m.role === "user").pop()?.content || ""
    const systemMsg = messages.find(m => m.role === "system")?.content || ""
    
    // Identificar persona ativa
    let persona = "Assistente"
    for (const [key] of Object.entries(PERSONAS)) {
      if (systemMsg.toLowerCase().includes(key.toLowerCase())) {
        persona = key
        break
      }
    }
    
    // Respostas simuladas baseadas na persona
    const responses = {
      "Professor": `Como educador, vou explicar isso passo a passo. Primeiro, é importante entender que "${userLast}" pode ser abordado de várias perspectivas. Vamos começar com os fundamentos e construir o conhecimento gradualmente. Imagine que isso é como aprender a andar de bicicleta - precisamos dominar o equilíbrio antes de pensar em velocidade.`,
      
      "Suporte Técnico": `Para resolver "${userLast}", vamos seguir um processo estruturado de troubleshooting:\n\n1. **Verificação inicial**: Confirme se todos os pré-requisitos estão atendidos\n2. **Diagnóstico**: Execute os testes de conectividade básicos\n3. **Implementação**: Aplique a solução recomendada\n4. **Validação**: Teste se o problema foi resolvido\n\nSe persistir, escale para o nível 2 de suporte.`,
      
      "Contador de Histórias": `Isso me lembra uma história interessante... Era uma vez uma empresa que enfrentou exatamente o mesmo desafio relacionado a "${userLast}". No início, eles tentaram várias abordagens sem sucesso, mas descobriram que a chave estava em uma perspectiva completamente diferente. Como diz o ditado, "às vezes é preciso dar um passo para trás para enxergar o quadro completo".`,
      
      "Analista": `Analisando sua questão sobre "${userLast}", os dados históricos mostram que:\n\n• 72% dos casos similares são resolvidos com a abordagem A\n• 23% requerem a metodologia B\n• 5% necessitam intervenção especializada\n\n**Recomendação**: Baseado no padrão identificado, sugiro iniciar pela abordagem A, com fallback para B se necessário. ROI estimado: 85% de eficácia.`,
      
      "Assistente": `Entendi sua pergunta sobre "${userLast}". Posso ajudar com informações detalhadas, exemplos práticos e orientações passo a passo. Que aspecto específico você gostaria de explorar primeiro?`
    }
    
    const response = responses[persona] || responses["Assistente"]
    return `${response}\n\n*Modo simulação - ${persona} | temp=${params.temperature}*`
  }
}

function App() {
  // Estados principais
  const [activeTab, setActiveTab] = useState("chat")
  const [chatHistory, setChatHistory] = useState([])
  const [currentMessage, setCurrentMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [feedbacks, setFeedbacks] = useState([])
  const [showFeedback, setShowFeedback] = useState(false)
  
  // Configurações
  const [persona, setPersona] = useState("Professor")
  const [style, setStyle] = useState("Formal")
  const [temperature, setTemperature] = useState([0.7])
  const [topP, setTopP] = useState([0.9])
  const [maxTokens, setMaxTokens] = useState([512])
  const [memoryTurns, setMemoryTurns] = useState([6])
  
  // Refs
  const chatEndRef = useRef(null)
  const client = new OCIClient("mock")
  
  // Auto-scroll do chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chatHistory])
  
  // Inicializar com prompt do sistema
  useEffect(() => {
    const systemPrompt = {
      role: "system",
      content: buildSystemPrompt(persona, style)
    }
    
    if (chatHistory.length === 0 || chatHistory[0].role !== "system") {
      setChatHistory([systemPrompt])
    } else {
      setChatHistory(prev => [systemPrompt, ...prev.slice(1)])
    }
  }, [persona, style])
  
  // Construir prompt do sistema
  function buildSystemPrompt(persona, style) {
    const guardrails = "Responda em PT-BR. Seja útil, claro e honesto sobre limitações. Quando apropriado, proponha próximos passos práticos. Se a pergunta for ambígua, peça uma clarificação curta. Nunca invente números ou políticas internas."
    
    return `Você é um assistente especializado com foco em ${persona}.
Persona: ${PERSONAS[persona]}
Estilo: ${style}. ${STYLES[style]}
Regras: ${guardrails}`
  }
  
  // Recortar histórico para manter memória
  function trimHistory(history, maxTurns) {
    const system = history.filter(m => m.role === "system")
    const dialog = history.filter(m => m.role === "user" || m.role === "assistant")
    
    if (maxTurns <= 0) return system
    return [...system, ...dialog.slice(-(maxTurns * 2))]
  }
  
  // Enviar mensagem
  async function sendMessage() {
    if (!currentMessage.trim() || isLoading) return
    
    const userMessage = { role: "user", content: currentMessage.trim() }
    const newHistory = [...chatHistory, userMessage]
    setChatHistory(newHistory)
    setCurrentMessage("")
    setIsLoading(true)
    setShowFeedback(false)
    
    try {
      const messages = trimHistory(newHistory, memoryTurns[0])
      const params = {
        temperature: temperature[0],
        top_p: topP[0],
        max_tokens: maxTokens[0],
        memory_turns: memoryTurns[0]
      }
      
      const response = await client.generate(messages, params)
      const assistantMessage = { role: "assistant", content: response }
      
      setChatHistory(prev => [...prev, assistantMessage])
      setShowFeedback(true)
    } catch (error) {
      console.error("Erro ao gerar resposta:", error)
      const errorMessage = { 
        role: "assistant", 
        content: "⚠️ Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente." 
      }
      setChatHistory(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }
  
  // Limpar conversa
  function clearChat() {
    const systemPrompt = { role: "system", content: buildSystemPrompt(persona, style) }
    setChatHistory([systemPrompt])
    setShowFeedback(false)
  }
  
  // Salvar feedback
  function saveFeedback(rating, comment = "") {
    if (chatHistory.length < 2) return
    
    const lastUser = chatHistory.filter(m => m.role === "user").pop()?.content || ""
    const lastBot = chatHistory.filter(m => m.role === "assistant").pop()?.content || ""
    
    const feedback = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      persona,
      style,
      rating,
      comment: comment.trim(),
      user_msg: lastUser,
      assistant_msg: lastBot
    }
    
    setFeedbacks(prev => [...prev, feedback])
    setShowFeedback(false)
  }
  
  // Calcular métricas
  const totalFeedbacks = feedbacks.length
  const positiveFeedbacks = feedbacks.filter(f => f.rating === "👍").length
  const negativeFeedbacks = feedbacks.filter(f => f.rating === "👎").length
  const satisfactionRate = totalFeedbacks > 0 ? (positiveFeedbacks / totalFeedbacks * 100) : 0
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto p-4 max-w-7xl">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-6"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            💬 Chatbot OCI v3
          </h1>
          <p className="text-muted-foreground">
            Sistema de conversação com memória, personas e feedback - Pronto para integração com Oracle Cloud
          </p>
        </motion.div>
        
        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="w-4 h-4" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Analytics
            </TabsTrigger>
          </TabsList>
          
          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Sidebar de Configurações */}
              <Card className="lg:col-span-1">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    Configurações
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Persona */}
                  <div>
                    <Label>Persona</Label>
                    <Select value={persona} onValueChange={setPersona}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.keys(PERSONAS).map(p => (
                          <SelectItem key={p} value={p}>{p}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  {/* Estilo */}
                  <div>
                    <Label>Estilo</Label>
                    <Select value={style} onValueChange={setStyle}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.keys(STYLES).map(s => (
                          <SelectItem key={s} value={s}>{s}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  {/* Temperature */}
                  <div>
                    <Label>Temperature: {temperature[0]}</Label>
                    <Slider
                      value={temperature}
                      onValueChange={setTemperature}
                      max={1}
                      min={0}
                      step={0.05}
                      className="mt-2"
                    />
                  </div>
                  
                  {/* Top-P */}
                  <div>
                    <Label>Top-P: {topP[0]}</Label>
                    <Slider
                      value={topP}
                      onValueChange={setTopP}
                      max={1}
                      min={0}
                      step={0.05}
                      className="mt-2"
                    />
                  </div>
                  
                  {/* Max Tokens */}
                  <div>
                    <Label>Max Tokens: {maxTokens[0]}</Label>
                    <Slider
                      value={maxTokens}
                      onValueChange={setMaxTokens}
                      max={2048}
                      min={64}
                      step={32}
                      className="mt-2"
                    />
                  </div>
                  
                  {/* Memory */}
                  <div>
                    <Label>Memória: {memoryTurns[0]} trocas</Label>
                    <Slider
                      value={memoryTurns}
                      onValueChange={setMemoryTurns}
                      max={20}
                      min={0}
                      step={1}
                      className="mt-2"
                    />
                  </div>
                  
                  {/* Modo Simulação */}
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-sm text-green-700 dark:text-green-300">
                      ✅ Modo simulação ativo. Desative quando tiver as credenciais OCI.
                    </p>
                  </div>
                </CardContent>
              </Card>
              
              {/* Área de Chat */}
              <div className="lg:col-span-3 space-y-4">
                {/* Tags de Configuração */}
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline">🧑‍💼 {persona}</Badge>
                  <Badge variant="outline">🎨 {style}</Badge>
                  <Badge variant="outline">🌡️ {temperature[0]}</Badge>
                  <Badge variant="outline">📊 top-p={topP[0]}</Badge>
                  <Badge variant="outline">🧠 mem={memoryTurns[0]}</Badge>
                </div>
                
                {/* Chat Container */}
                <Card className="h-[600px] flex flex-col">
                  <CardHeader className="flex-row items-center justify-between">
                    <CardTitle>Conversa</CardTitle>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={clearChat}
                      className="flex items-center gap-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      Limpar
                    </Button>
                  </CardHeader>
                  
                  <CardContent className="flex-1 overflow-y-auto space-y-4">
                    <AnimatePresence>
                      {chatHistory.filter(m => m.role !== "system").map((message, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                          {message.role === "assistant" && (
                            <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                              <Bot className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                            </div>
                          )}
                          
                          <div className={`max-w-[70%] p-4 rounded-2xl ${
                            message.role === "user" 
                              ? "bg-blue-500 text-white rounded-br-sm" 
                              : "bg-gray-100 dark:bg-gray-800 rounded-bl-sm"
                          }`}>
                            <p className="whitespace-pre-wrap">{message.content}</p>
                          </div>
                          
                          {message.role === "user" && (
                            <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                              <User className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </AnimatePresence>
                    
                    {isLoading && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-3"
                      >
                        <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                          <Bot className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-2xl rounded-bl-sm">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                    
                    <div ref={chatEndRef} />
                  </CardContent>
                  
                  {/* Input Area */}
                  <div className="p-4 border-t">
                    <div className="flex gap-2">
                      <Input
                        value={currentMessage}
                        onChange={(e) => setCurrentMessage(e.target.value)}
                        placeholder="Digite sua mensagem..."
                        onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                        disabled={isLoading}
                        className="flex-1"
                      />
                      <Button 
                        onClick={sendMessage} 
                        disabled={isLoading || !currentMessage.trim()}
                        className="px-6"
                      >
                        <Send className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
                
                {/* Feedback */}
                {showFeedback && chatHistory.length > 2 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">💡 Feedback desta resposta</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex gap-4 items-center">
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => saveFeedback("👍")}
                              className="flex items-center gap-2"
                            >
                              <ThumbsUp className="w-4 h-4" />
                              👍
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => saveFeedback("👎")}
                              className="flex items-center gap-2"
                            >
                              <ThumbsDown className="w-4 h-4" />
                              👎
                            </Button>
                          </div>
                          <Input
                            placeholder="Comentário opcional..."
                            className="flex-1"
                            onKeyPress={(e) => {
                              if (e.key === "Enter") {
                                saveFeedback("👍", e.target.value)
                                e.target.value = ""
                              }
                            }}
                          />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                )}
              </div>
            </div>
          </TabsContent>
          
          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>📊 Analytics - Feedback do Chatbot</CardTitle>
              </CardHeader>
              <CardContent>
                {feedbacks.length === 0 ? (
                  <div className="text-center py-12">
                    <BarChart3 className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">📝 Ainda não há dados de feedback coletados</h3>
                    <div className="text-muted-foreground space-y-1">
                      <p>🚀 Como usar:</p>
                      <p>1. Vá para a página de Chat</p>
                      <p>2. Faça algumas perguntas ao chatbot</p>
                      <p>3. Avalie as respostas com 👍 ou 👎</p>
                      <p>4. Volte aqui para ver as análises!</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Métricas */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <Card>
                        <CardContent className="p-4 text-center">
                          <div className="text-2xl font-bold">{totalFeedbacks}</div>
                          <div className="text-sm text-muted-foreground">Total Feedbacks</div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <div className="text-2xl font-bold text-green-600">{positiveFeedbacks}</div>
                          <div className="text-sm text-muted-foreground">👍 Positivos</div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <div className="text-2xl font-bold text-red-600">{negativeFeedbacks}</div>
                          <div className="text-sm text-muted-foreground">👎 Negativos</div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <div className="text-2xl font-bold text-blue-600">{satisfactionRate.toFixed(1)}%</div>
                          <div className="text-sm text-muted-foreground">Taxa de Satisfação</div>
                        </CardContent>
                      </Card>
                    </div>
                    
                    {/* Comentários */}
                    <Card>
                      <CardHeader>
                        <CardTitle>📝 Comentários dos Usuários</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {feedbacks.filter(f => f.comment).length === 0 ? (
                          <p className="text-muted-foreground">Nenhum comentário foi registrado ainda.</p>
                        ) : (
                          <div className="space-y-4">
                            {feedbacks.filter(f => f.comment).map(feedback => (
                              <Card key={feedback.id}>
                                <CardContent className="p-4">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Badge variant="outline">{feedback.persona}</Badge>
                                    <Badge variant={feedback.rating === "👍" ? "default" : "destructive"}>
                                      {feedback.rating}
                                    </Badge>
                                    <span className="text-sm text-muted-foreground">
                                      {new Date(feedback.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                  <p className="text-sm">{feedback.comment}</p>
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App
