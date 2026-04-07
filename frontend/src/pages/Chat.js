/**
 * Chat Page
 * LLM-powered Q&A interface with RAG
 */

import React, { useState, useEffect, useRef } from 'react';
import { chatService } from '../services/apiService';

function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hello! I am your Supply Chain AI Assistant. Ask me about delivery performance, quality metrics, production efficiency, suppliers, or inventory.',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    initializeConversation();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeConversation = async () => {
    try {
      const response = await chatService.createConversation();
      setConversationId(response.conversation_id);
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!input.trim() || loading) return;

    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatService.askQuestion(
        input,
        null,
        conversationId
      );

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        confidence: response.confidence,
        sources: response.sources,
        timestamp: new Date(response.timestamp),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <div>
            <h1 className="card-title">💬 Supply Chain AI Assistant</h1>
            <p className="card-subtitle">
              Ask questions about your supply chain operations
            </p>
          </div>
        </div>
      </div>

      {/* Suggested Topics */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3 style={{ marginBottom: '12px', fontSize: '14px', fontWeight: '600' }}>
          Quick Questions
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {[
            "What's our on-time delivery rate?",
            "Show me defect trends",
            "How is PROD_GLASS_A1 performing?",
            "What's our supplier performance?",
            "Tell me about inventory levels",
          ].map((question, index) => (
            <button
              key={index}
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setInput(question);
              }}
            >
              {question}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-bubble">
                {message.content}

                {/* Confidence & Sources for Assistant Messages */}
                {message.role === 'assistant' && message.confidence && (
                  <div style={{
                    marginTop: '8px',
                    paddingTop: '8px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.2)',
                    fontSize: '11px',
                    opacity: 0.8,
                  }}>
                    <div>Confidence: {(message.confidence * 100).toFixed(0)}%</div>
                    {message.sources && message.sources.length > 0 && (
                      <div>Sources: {message.sources.join(', ')}</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="message-bubble">
                <div className="spinner" style={{
                  width: '20px',
                  height: '20px',
                  borderWidth: '2px',
                }}></div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form className="chat-input-area" onSubmit={handleSendMessage}>
          <input
            type="text"
            className="chat-input"
            placeholder="Ask about deliveries, quality, production, suppliers, or inventory..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            autoFocus
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !input.trim()}
          >
            {loading ? '⏳' : '📤'} Send
          </button>
        </form>
      </div>

      {/* Info Box */}
      <div className="card" style={{ marginTop: '20px', backgroundColor: '#eff6ff', borderLeft: '4px solid #0284c7' }}>
        <p style={{ fontSize: '12px', margin: '0' }}>
          <strong>ℹ️ About this AI:</strong> This assistant uses Retrieval-Augmented Generation (RAG) to answer questions based on your supply chain data. It provides contextual insights and recommends actions based on real data patterns.
        </p>
      </div>
    </div>
  );
}

export default Chat;
