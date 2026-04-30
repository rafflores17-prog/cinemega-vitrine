from flask import Flask, render_template, request
import requests
from urllib.parse import quote

app = Flask(__name__)

# CONFIG
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
NOME_SITE = "Cine Mega"

def buscar_tmdb(url):
    try:
        res = requests.get(url, timeout=8)
        return res.json().get("results", [])
    except:
        return []

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
        filmes = buscar_tmdb(url)
        return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca=f"Resultados: {q}")

    # Prateleiras da Home
    populares = buscar_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR")
    return render_template("index.html", populares=populares, img=IMG, bg=BG, nome_site=NOME_SITE, busca=False)

@app.route("/genero/<int:id>/<string:nome>")
def ver_genero(id, nome):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres={id}"
    filmes = buscar_tmdb(url)
    return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca=f"Categoria: {nome}")

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=recommendations"
        data = requests.get(url, timeout=8).json()
        titulo = data.get("title")
        ano = data.get("release_date", "")[:4]
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(f'{titulo} ({ano})' if ano else titulo)}"
        
        return render_template("detalhes.html", 
                               filme=data, img=IMG, bg=BG, play_link=play_link,
                               generos=data.get("genres", []), 
                               nota=round(data.get("vote_average", 0), 1),
                               duracao=f"{data.get('runtime', 0)} min",
                               recomendados=data.get("recommendations", {}).get("results", [])[:6],
                               nome_site=NOME_SITE)
    except:
        return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
