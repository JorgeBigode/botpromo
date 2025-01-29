from flask import Flask, render_template, request, flash
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'uma-chave-secreta-muito-segura')

def carregar_config():
    try:
        with open('config.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def enviar_telegram(token, chat_id, texto):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    config = carregar_config()
    template_path = config.get('TEMPLATE_PATH', 'mensagem.txt') if config else 'mensagem.txt'
    
    if request.method == 'POST':
        try:
            template = Path(template_path).read_text(encoding='utf-8')
            
            dados = {
                'produto': request.form['produto'],
                'desconto': request.form['desconto'],
                'detalhes': request.form['detalhes'],
                'link': request.form['link']
            }
            
            mensagem = template.format(**dados)
            
            if config:
                resultado = enviar_telegram(
                    config['TOKEN'],
                    config['CHAT_ID'],
                    mensagem
                )
                
                if resultado.get('ok'):
                    flash('✅ Mensagem enviada com sucesso!', 'success')
                else:
                    flash(f'❌ Erro: {resultado.get("description")}', 'danger')
            else:
                flash('❌ Configurações não encontradas!', 'danger')
                
        except Exception as e:
            flash(f'❌ Erro: {str(e)}', 'danger')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)