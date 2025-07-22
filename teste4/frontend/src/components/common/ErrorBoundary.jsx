/**
 * Error Boundary component for handling React errors
 */
import React from 'react';
import { ErrorBoundary as ReactErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        
        <h1 className="mt-4 text-xl font-semibold text-center text-gray-900">
          Oops! Algo deu errado
        </h1>
        
        <p className="mt-2 text-sm text-center text-gray-600">
          Ocorreu um erro inesperado. Por favor, tente novamente.
        </p>
        
        {process.env.NODE_ENV === 'development' && (
          <details className="mt-4 p-4 bg-gray-50 rounded text-xs">
            <summary className="cursor-pointer text-gray-700 font-medium">
              Detalhes do erro (desenvolvimento)
            </summary>
            <pre className="mt-2 text-red-600 overflow-auto">
              {error.message}
              {error.stack}
            </pre>
          </details>
        )}
        
        <div className="mt-6 flex items-center justify-center space-x-4">
          <button
            onClick={resetErrorBoundary}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Tentar novamente
          </button>
          
          <button
            onClick={() => window.location.href = '/'}
            className="px-4 py-2 bg-gray-200 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Ir para início
          </button>
        </div>
      </div>
    </div>
  );
}

export function ErrorBoundary({ children }) {
  return (
    <ReactErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        // Log to error reporting service
        console.error('Error caught by boundary:', error, errorInfo);
        
        // You can send to Sentry, LogRocket, etc. here
        if (window.Sentry) {
          window.Sentry.captureException(error);
        }
      }}
      onReset={() => {
        // Additional cleanup if needed
        window.location.reload();
      }}
    >
      {children}
    </ReactErrorBoundary>
  );
}

export default ErrorBoundary;