from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    # Se existir pasta static (build do React), usa ela como static_folder
    static_folder = 'static' if os.path.exists('static') else None
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    
    # Configuração CORS
    CORS(app, origins=["http://localhost:3000", "https://dashboard-estoque-v2.fly.dev"])
    
    # Configurações
    app.config['JSON_AS_ASCII'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Registrar blueprints
    from app.api.estoque import estoque_bp
    app.register_blueprint(estoque_bp, url_prefix='/api/v2/estoque')
    
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'flask-backend'}
    
    # Servir React app
    @app.route('/')
    def serve_react():
        if static_folder:
            return send_from_directory(app.static_folder, 'index.html')
        return {'message': 'API Flask rodando! Use /estoque para acessar a interface.'}
    
    @app.route('/estoque')
    def serve_estoque():
        if static_folder:
            return send_from_directory(app.static_folder, 'index.html')
        return {'message': 'Interface não encontrada. Execute npm run build primeiro.'}
    
    # Catch all para React Router
    @app.errorhandler(404)
    def not_found(e):
        if static_folder and os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')
        return {'error': 'Not found'}, 404
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8000)