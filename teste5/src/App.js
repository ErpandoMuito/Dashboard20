import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [metricas, setMetricas] = useState({
    notas: 0,
    pedidos: 0,
    produtos: 0,
    faturamento: 0
  });
  const [wsConnected, setWsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [realtimeUpdates, setRealtimeUpdates] = useState([]);

  useEffect(() => {
    // Carregar dados iniciais
    loadDashboardData();
    
    // Conectar WebSocket
    connectWebSocket();
    
    return () => {
      // Cleanup
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/teste5/api/dashboard');
      const data = await response.json();
      
      setMetricas({
        notas: data.metricas.total_notas,
        pedidos: data.metricas.pedidos_pendentes,
        produtos: data.metricas.produtos_estoque,
        faturamento: data.metricas.faturamento_mes
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    const wsUrl = window.location.protocol === 'https:' 
      ? `wss://${window.location.host}/ws`
      : `ws://${window.location.host}/ws`;
    
    try {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket conectado!');
        setWsConnected(true);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'update') {
          setRealtimeUpdates(prev => [...prev.slice(-4), data.data]);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket erro:', error);
        setWsConnected(false);
      };
      
      ws.onclose = () => {
        setWsConnected(false);
        // Reconectar após 5 segundos
        setTimeout(connectWebSocket, 5000);
      };
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <div className="container">
      <div className="header">
        <h1>Dashboard Hacker 🚀</h1>
        <p>Sistema ultra-rápido com cache inteligente</p>
        <div className="status">
          <span className={`ws-status ${wsConnected ? 'connected' : 'disconnected'}`}>
            {wsConnected ? '🟢 Real-time ativo' : '🔴 Real-time offline'}
          </span>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Hackeando dados...</p>
        </div>
      ) : (
        <>
          <div className="grid">
            <div className="card glow-purple">
              <div className="card-icon">📊</div>
              <h3>Notas Fiscais</h3>
              <div className="metric">{metricas.notas.toLocaleString('pt-BR')}</div>
              <div className="card-footer">Total emitidas</div>
            </div>
            
            <div className="card glow-green">
              <div className="card-icon">💰</div>
              <h3>Faturamento</h3>
              <div className="metric">{formatCurrency(metricas.faturamento)}</div>
              <div className="card-footer">Este mês</div>
            </div>
            
            <div className="card glow-blue">
              <div className="card-icon">📦</div>
              <h3>Pedidos</h3>
              <div className="metric">{metricas.pedidos}</div>
              <div className="card-footer">Pendentes</div>
            </div>
            
            <div className="card glow-orange">
              <div className="card-icon">🏭</div>
              <h3>Produtos</h3>
              <div className="metric">{metricas.produtos.toLocaleString('pt-BR')}</div>
              <div className="card-footer">Em estoque</div>
            </div>
          </div>

          {realtimeUpdates.length > 0 && (
            <div className="realtime-section">
              <h2>Atualizações em Tempo Real</h2>
              <div className="updates-grid">
                {realtimeUpdates.map((update, index) => (
                  <div key={index} className="update-item">
                    <span className="update-time">
                      {new Date(update.timestamp).toLocaleTimeString('pt-BR')}
                    </span>
                    <span className="update-info">
                      +{update.novas_notas} notas | +{update.novos_pedidos} pedidos
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="features">
            <h2>Features Hackers 🔥</h2>
            <div className="feature-grid">
              <div className="feature-item">
                <span className="feature-icon">⚡</span>
                <h4>Cache Inteligente</h4>
                <p>Redis com fallback automático</p>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🚀</span>
                <h4>Ultra Rápido</h4>
                <p>Resposta em menos de 50ms</p>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🔄</span>
                <h4>Real-time</h4>
                <p>WebSocket para updates instantâneos</p>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🎭</span>
                <h4>Mock Mode</h4>
                <p>Funciona mesmo offline</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;