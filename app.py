from flask import Flask, render_template, request, redirect
import requests
from urllib.parse import quote, unquote

app = Flask(__name__)

NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

def buscar_tmdb(url):
    try:
        res = requests.get(url, timeout=10)
        return res.json().get("results", [])
    except: return []

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={quote(q)}"
        return render_template("index.html", filmes=buscar_tmdb(url), img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, q=q)

    destaques = buscar_tmdb(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR")[:5]
    populares = buscar_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR")
    comedia = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=35")
    terror = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27")
    return render_template("index.html", destaques=destaques, populares=populares, comedia=comedia, terror=terror, img=IMG, bg=BG, nome_site=NOME_SITE, busca=False)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        # Puxa vídeos, recomendações e créditos tudo em uma chamada só
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations,credits"
        data = requests.get(url, timeout=10).json()
        
        titulo = data.get("title")
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(titulo)}"
        
        # Lógica Robusta de Vídeo: 1º Busca Trailer, 2º Busca Teaser, 3º Qualquer vídeo
        videos = data.get("videos", {}).get("results", [])
        video_key = None
        
        # Tenta achar o Trailer oficial no YouTube
        trailer = next((v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if trailer:
            video_key = trailer["key"]
        else:
            # Se não tiver trailer, tenta um Teaser ou Clip
            teaser = next((v for v in videos if v["site"] == "YouTube"), None)
            if teaser: video_key = teaser["key"]

        return render_template("detalhes.html", 
                               filme=data, 
                               img=IMG, 
                               bg=BG, 
                               play_link=play_link, 
                               nota=round(data.get("vote_average", 0), 1), 
                               duracao=f"{data.get('runtime', 0)} min", 
                               trailer_id=video_key, 
                               recomendados=data.get("recommendations", {}).get("results", [])[:6], 
                               elenco=data.get("credits", {}).get("cast", [])[:10], 
                               nome_site=NOME_SITE)
    except: return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
