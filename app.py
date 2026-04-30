from flask import Flask, render_template, request
import requests
import time
from urllib.parse import quote

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

TIMEOUT = 10
CACHE = {}
CACHE_TEMPO = 600

def buscar_tmdb(url):
    agora = time.time()
    if url in CACHE:
        dados, timestamp = CACHE[url]
        if agora - timestamp < CACHE_TEMPO:
            return dados
    try:
        res = requests.get(url, timeout=TIMEOUT)
        if res.status_code == 200:
            dados = res.json().get("results", [])
            CACHE[url] = (dados, agora)
            return dados
        return []
    except:
        return []

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
        filmes = buscar_tmdb(url)
        return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca=f"🔍 Resultados: {q}")

    try:
        destaques = buscar_tmdb(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR")[:5]
        populares = buscar_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR")
        comedia = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=35")
        terror = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27")
    except:
        destaques = populares = comedia = terror = []

    return render_template("index.html", destaques=destaques, populares=populares, comedia=comedia, terror=terror, img=IMG, bg=BG, nome_site=NOME_SITE, busca=False)

@app.route("/genero/<int:id>/<string:nome>")
def ver_genero(id, nome):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres={id}"
    filmes = buscar_tmdb(url)
    return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca=f"🎬 Categoria: {nome}")

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url_detalhes = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations"
        res = requests.get(url_detalhes, timeout=TIMEOUT)
        if res.status_code != 200:
            return "Filme não encontrado", 404
            
        data = res.json()
        titulo_base = data.get("title", "Filme")
        ano = data.get("release_date", "")[:4]
        titulo_busca = f"{titulo_base} ({ano})" if ano else titulo_base
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(titulo_busca)}"

        return render_template("detalhes.html", 
                               filme=data, 
                               img=IMG, 
                               bg=BG, 
                               play_link=play_link, 
                               generos=data.get("genres", []), 
                               nota=round(data.get("vote_average", 0), 1),
                               duracao=f"{data.get('runtime', 0)} min",
                               recomendados=data.get("recommendations", {}).get("results", [])[:6],
                               nome_site=NOME_SITE)
    except Exception as e:
        print(f"Erro Detalhes: {e}")
        return "Erro interno no servidor", 500
