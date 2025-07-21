import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import EntradaEstoque from './components/EntradaEstoque';

function App() {
  return (
    <div className="App">
      <div className="container">
        <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
          Dashboard Estoque v2.0
        </h1>
        <EntradaEstoque />
      </div>
      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}

export default App;