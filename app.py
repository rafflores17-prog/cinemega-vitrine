from flask import Flask, render_template, request, send_from_directory
import requests
from urllib.parse import quote

app = Flask(__name__)

NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        # Se for busca, foca apenas no resultado da pesquisa
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
        try:
            res = requests.get(url, timeout=10).json().get("results", [])
        except: res = []
        return render_template("index.html", filmes=res, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True)
    
    # Se for Home Normal, carrega o Nível Pro
    try:
        # 🎬 Destaques (Banner topo)
        destaques = requests.get(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR").json().get("results", [])[:5]
        # 🔥 Populares
        populares = requests.get(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR").json().get("results", [])
        # 🍿 Terror (Exemplo de trilho por gênero)
        terror = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27").json().get("results", [])
    except:
        destaques, populares, terror = [], [], []
        
    return render_template("index.html", destaques=destaques, populares=populares, terror=terror, img=IMG, bg=BG, nome_site=NOME_SITE, busca=False)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url_detalhes = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations"
        data = requests.get(url_detalhes, timeout=10).json()
        titulo = data.get('title', '')
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(titulo)}"
        generos = [g['name'] for g in data.get('genres', [])]
        duracao = f"{data.get('runtime', 0)} min"
        nota = round(data.get('vote_average', 0), 1)
        videos = data.get('videos', {}).get('results', [])
        trailer = next((v['key'] for v in videos if v['site'] == 'YouTube'), None)
        recomendados = data.get('recommendations', {}).get('results', [])[:6]
        return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, trailer_key=trailer, recomendados=recomendados, generos=generos, duracao=duracao, nota=nota, nome_site=NOME_SITE)
    except: return "Erro", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
