from flask import Flask, render_template, request, send_from_directory
import requests
from urllib.parse import quote

app = Flask(__name__)

NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"

# 🛡️ URL DO SEU MOTOR NO KOYEB
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

@app.route("/")
def home():
    q = request.args.get("q")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}" if q else f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR"
    try:
        res = requests.get(url, timeout=10).json().get("results", [])
    except: res = []
    return render_template("index.html", filmes=res[:20], img=IMG, nome_site=NOME_SITE)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        # Busca detalhes, trailers e recomendações tudo de uma vez
        url_detalhes = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations"
        data = requests.get(url_detalhes, timeout=10).json()
        
        titulo = data.get('title', '')
        # O link de play aponta para o buscador do seu motor
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(titulo)}"
        
        # Pega o primeiro trailer do YouTube disponível
        trailer = next((v['key'] for v in data.get('videos', {}).get('results', []) if v['type'] == 'Trailer'), None)
        
        # Pega até 6 filmes recomendados
        recomendados = data.get('recommendations', {}).get('results', [])[:6]
        
        return render_template("detalhes.html", 
                               filme=data, 
                               img=IMG, 
                               bg=BG, 
                               play_link=play_link, 
                               trailer_key=trailer, 
                               recomendados=recomendados,
                               nome_site=NOME_SITE)
    except:
        return "Erro ao carregar detalhes", 404

@app.route('/sw.js')
def sw(): return send_from_directory('.', 'sw.js', mimetype='application/javascript')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
