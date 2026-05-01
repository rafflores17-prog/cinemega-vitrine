from flask import Flask, render_template, request, redirect
import requests
from urllib.parse import quote, unquote

app = Flask(__name__)

# CONFIG
NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

# BUSCA TMDB
def buscar_tmdb(url):
    try:
        res = requests.get(url, timeout=10)
        return res.json().get("results", [])
    except:
        return []

# HOME
@app.route("/")
def home():
    q = request.args.get("q")

    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={quote(q)}"
        filmes = buscar_tmdb(url)

        return render_template("index.html",
                               filmes=filmes,
                               img=IMG,
                               bg=BG,
                               nome_site=NOME_SITE,
                               busca=True,
                               q=q)

    destaques = buscar_tmdb(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR")[:5]
    populares = buscar_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR")
    comedia = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=35")
    terror = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27")
    ficcao = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=878")
    trash = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27,35")

    return render_template("index.html",
                           destaques=destaques,
                           populares=populares,
                           comedia=comedia,
                           terror=terror,
                           ficcao=ficcao,
                           trash=trash,
                           img=IMG,
                           bg=BG,
                           nome_site=NOME_SITE,
                           busca=False)

# GENERO
@app.route("/genero/<int:id>/<string:nome>")
def ver_genero(id, nome):
    nome_limpo = unquote(nome)

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres={id}"
    filmes = buscar_tmdb(url)

    return render_template("index.html",
                           filmes=filmes,
                           img=IMG,
                           bg=BG,
                           nome_site=NOME_SITE,
                           busca=True,
                           q=nome_limpo)

# DETALHES (CLIQUE DO FILME)
@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations,credits"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return f"Erro TMDB: {response.status_code}"

        data = response.json()

        titulo = data.get("title", "")
        ano = data.get("release_date", "")[:4]

        # 🔥 BUSCA CORRIGIDA (resolve filme errado)
        busca = f"{titulo} {ano}"
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(busca)}"

        # TRAILER
        videos = data.get("videos", {}).get("results", [])
        trailer = next((v["key"] for v in videos if v["site"] == "YouTube"), None)

        # RECOMENDADOS
        recomendados = data.get("recommendations", {}).get("results", [])[:6]

        # ELENCO
        elenco = data.get("credits", {}).get("cast", [])[:10]

        return render_template("detalhes.html",
                               filme=data,
                               img=IMG,
                               bg=BG,
                               play_link=play_link,
                               generos=data.get("genres", []),
                               nota=round(data.get("vote_average", 0), 1),
