import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import EntradaEstoque from './components/EntradaEstoque';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/estoque" replace />} />
          <Route path="/estoque" element={
            <div className="container">
              <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
                Dashboard Estoque v2.0
              </h1>
              <EntradaEstoque />
            </div>
          } />
        </Routes>
        <ToastContainer position="top-right" autoClose={3000} />
      </div>
    </Router>
  );
}

export default App;