from flask import Flask, render_template, request, redirect
import requests
from urllib.parse import quote

app = Flask(__name__)

# CONFIGURAÇÕES
NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

def buscar_tmdb(url):
    try:
        res = requests.get(url, timeout=10)
        return res.json().get("results", [])
    except:
        return []

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
        filmes = buscar_tmdb(url)
        # 🔑 AJUSTE: Enviamos 'filmes' para a grade de busca
        return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, q=q)

    # Dados para a Home (Slider + Banner)
    # 🔑 AJUSTE: 'destaques' (plural) para o loop do banner rotativo
    destaques = buscar_tmdb(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR")[:5]
    populares = buscar_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR")
    comedia = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=35")
    terror = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27")

    return render_template("index.html", 
                           destaques=destaques, 
                           populares=populares, 
                           comedia=comedia, 
                           terror=terror, 
                           img=IMG, bg=BG, 
                           nome_site=NOME_SITE, 
                           busca=False)

@app.route("/genero/<int:id>/<string:nome>")
def ver_genero(id, nome):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres={id}"
    filmes = buscar_tmdb(url)
    return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, q=nome)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations"
        data = requests.get(url, timeout=10).json()
        
        titulo = data.get("title")
        ano = data.get("release_date", "")[:4]
        # O link do play vai pro seu motor no Koyeb
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(f'{titulo} ({ano})')}"
        
        videos = data.get("videos", {}).get("results", [])
        trailer = next((v["key"] for v in videos if v["site"] == "YouTube"), None)
        
        # 🚀 AQUI ESTÁ O QUE SUMIU: Pegamos as recomendações do TMDB
        recomendados = data.get("recommendations", {}).get("results", [])[:6]

        return render_template("detalhes.html", 
                               filme=data, 
                               img=IMG, bg=BG, 
                               play_link=play_link,
                               generos=data.get("genres", []), 
                               nota=round(data.get("vote_average", 0), 1),
                               duracao=f"{data.get('runtime', 0)} min",
                               trailer_key=trailer,
                               recomendados=recomendados, # Variável enviada!
                               nome_site=NOME_SITE)
    except:
        return redirect("/")
