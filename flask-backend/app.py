from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuração CORS
    CORS(app, origins=["http://localhost:3000"])
    
    # Configurações
    app.config['JSON_AS_ASCII'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Registrar blueprints
    from app.api.estoque import estoque_bp
    app.register_blueprint(estoque_bp, url_prefix='/api/v2/estoque')
    
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'flask-backend'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8000)