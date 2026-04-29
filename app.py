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

# URL DO SEU MOTOR NO KOYEB
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

TIMEOUT = 10
CACHE = {}
CACHE_TEMPO = 600

# =========================
# FUNÇÕES DE APOIO
# =========================

def buscar_tmdb(url):
    agora = time.time()
    if url in CACHE:
        dados, timestamp = CACHE[url]
        if agora - timestamp < CACHE_TEMPO:
            return dados
    try:
        res = requests.get(url, timeout=TIMEOUT)
        dados = res.json().get("results", [])
        CACHE[url] = (dados, agora)
        return dados
    except Exception as e:
        print(f"Erro TMDB: {e}")
        return []

def gerar_link_play(titulo):
    """
    AJUSTE MESTRE: Não fazemos mais o requests.head aqui.
    Isso evita que a Vercel bloqueie o link por demora do servidor IPTV.
    """
    return f"{MOTOR_URL}/buscar?titulo={quote(titulo)}"

@app.context_processor
def controle_de_anuncios():
    user_agent = request.headers.get('User-Agent', '').lower()
    is_app = 'wv' in user_agent
    return dict(mostrar_ads=not is_app)

# =========================
# ROTAS DO SITE
# =========================

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
        filmes = buscar_tmdb(url)
        return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca="🔍 Resultados da Busca")

    try:
        destaques = buscar_tmdb(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR")[:5]
        populares = buscar_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR")
        comedia = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=35")
        ficcao = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=878")
        terror = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27")
    except:
        destaques = populares = comedia = ficcao = terror = []

    return render_template("index.html", destaques=destaques, populares=populares, comedia=comedia, ficcao=ficcao, terror=terror, img=IMG, bg=BG, nome_site=NOME_SITE, busca=False)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url_detalhes = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations"
        data = requests.get(url_detalhes, timeout=TIMEOUT).json()
        
        titulo_base = data.get("title", "")
        ano = data.get("release_date", "")[:4]
        titulo_busca = f"{titulo_base} ({ano})" if ano else titulo_base

        # LINK DE PLAY DIRETO PRO MOTOR
        play_link = gerar_link_play(titulo_busca)

        generos = [g["name"] for g in data.get("genres", [])]
        duracao = f"{data.get('runtime', 0)} min"
        nota = round(data.get("vote_average", 0), 1)
        
        videos = data.get("videos", {}).get("results", [])
        trailer = next((v["key"] for v in videos if v["site"] == "YouTube"), None)
        recomendados = data.get("recommendations", {}).get("results", [])[:6]

        return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, trailer_key=trailer, recomendados=recomendados, generos=generos, duracao=duracao, nota=nota, nome_site=NOME_SITE)
    except Exception as e:
        print(f"Erro detalhes: {e}")
        return "Erro ao carregar detalhes", 404

@app.route("/health")
def health():
    return {"status": "online", "site": NOME_SITE}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
