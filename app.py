from flask import Flask, render_template, request
import requests
import time
import os
from urllib.parse import quote

app = Flask(__name__)

# =========================
# CONFIG
# =========================

NOME_SITE = "Cine Mega"

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"

MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

TIMEOUT = 10

# =========================
# CACHE INTELIGENTE
# =========================

CACHE = {}

CACHE_TEMPO = 600  # 10 minutos


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

        print("Erro TMDB:", e)

        return []


# =========================
# GERAR LINK PLAY SEGURO
# =========================

def gerar_link_play(titulo):

    try:

        url = f"{MOTOR_URL}/buscar?titulo={quote(titulo)}"

        requests.head(url, timeout=3)

        return url

    except:

        print("Motor offline")

        return None


# =========================
# DETECTAR APP (SEM ADS)
# =========================

@app.context_processor
def controle_de_anuncios():

    user_agent = request.headers.get(
        'User-Agent',
        ''
    ).lower()

    is_app = 'wv' in user_agent

    return dict(mostrar_ads=not is_app)


# =========================
# HOME
# =========================

@app.route("/")
def home():

    q = request.args.get("q")

    if q:

        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}"
            "&language=pt-BR"
            f"&query={q}"
        )

        filmes = buscar_tmdb(url)

        return render_template(

            "index.html",

            filmes=filmes,

            img=IMG,
            bg=BG,

            nome_site=NOME_SITE,

            busca=True,

            titulo_busca="🔍 Resultados da Busca"

        )

    try:

        destaques = buscar_tmdb(

            f"https://api.themoviedb.org/3/movie/now_playing"
            f"?api_key={TMDB_API_KEY}"
            "&language=pt-BR"

        )[:5]

        populares = buscar_tmdb(

            f"https://api.themoviedb.org/3/movie/popular"
            f"?api_key={TMDB_API_KEY}"
            "&language=pt-BR"

        )

        comedia = buscar_tmdb(

            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={TMDB_API_KEY}"
            "&language=pt-BR"
            "&with_genres=35"

        )

        ficcao = buscar_tmdb(

            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={TMDB_API_KEY}"
            "&language=pt-BR"
            "&with_genres=878"

        )

        terror = buscar_tmdb(

            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={TMDB_API_KEY}"
            "&language=pt-BR"
            "&with_genres=27"

        )

    except:

        destaques = []
        populares = []
        comedia = []
        ficcao = []
        terror = []

    return render_template(

        "index.html",

        destaques=destaques,
        populares=populares,

        comedia=comedia,
        ficcao=ficcao,
        terror=terror,

        img=IMG,
        bg=BG,

        nome_site=NOME_SITE,

        busca=False

    )


# =========================
# GÊNERO
# =========================

@app.route("/genero/<int:gen_id>")
def genero(gen_id):

    nomes_generos = {

        28: "Ação",
        12: "Aventura",
        16: "Animação",
        35: "Comédia",
        80: "Crime",
        99: "Documentário",
        18: "Drama",
        10751: "Família",
        14: "Fantasia",
        36: "História",
        27: "Terror",
        10402: "Música",
        9648: "Mistério",
        10749: "Romance",
        878: "Ficção Científica",
        10770: "Cinema TV",
        53: "Thriller",
        10752: "Guerra",
        37: "Faroeste"

    }

    nome_gen = nomes_generos.get(
        gen_id,
        "Filmes"
    )

    url = (

        "https://api.themoviedb.org/3/discover/movie"

        f"?api_key={TMDB_API_KEY}"

        "&language=pt-BR"

        f"&with_genres={gen_id}"

    )

    filmes = buscar_tmdb(url)

    return render_template(

        "index.html",

        filmes=filmes,

        img=IMG,
        bg=BG,

        nome_site=NOME_SITE,

        busca=True,

        titulo_busca=f"📌 Gênero: {nome_gen}"

    )


# =========================
# DETALHES DO FILME
# =========================

@app.route("/filme/<int:id>")
def detalhes(id):

    try:

        url_detalhes = (

            "https://api.themoviedb.org/3/movie/"

            f"{id}"

            f"?api_key={TMDB_API_KEY}"

            "&language=pt-BR"

            "&append_to_response=videos,recommendations"

        )

        data = requests.get(
            url_detalhes,
            timeout=TIMEOUT
        ).json()

        titulo = data.get(
            "title",
            ""
        )

        ano = data.get(
            "release_date",
            ""
        )[:4]

        if ano:

            titulo = f"{titulo} ({ano})"

        play_link = gerar_link_play(
            titulo
        )

        if not play_link:

            play_link = "#"

        generos = [

            g["name"]

            for g in data.get(
                "genres",
                []
            )

        ]

        duracao = f"{data.get('runtime', 0)} min"

        nota = round(

            data.get(
                "vote_average",
                0
            ),

            1

        )

        videos = data.get(
            "videos",
            {}
        ).get(
            "results",
            []
        )

        trailer = next(

            (

                v["key"]

                for v in videos

                if v["site"] == "YouTube"

            ),

            None

        )

        recomendados = data.get(
            "recommendations",
            {}
        ).get(
            "results",
            []
        )[:6]

        return render_template(

            "detalhes.html",

            filme=data,

            img=IMG,
            bg=BG,

            play_link=play_link,

            trailer_key=trailer,

            recomendados=recomendados,

            generos=generos,

            duracao=duracao,

            nota=nota,

            nome_site=NOME_SITE

        )

    except Exception as e:

        print("Erro detalhes:", e)

        return "Erro", 404


# =========================
# ADS.TXT
# =========================

@app.route("/ads.txt")
def ads_txt():

    return (

        "google.com, pub-2866002449649160, DIRECT, f08c47fec0942fa0",

        200,

        {

            "Content-Type": "text/plain"

        }

    )


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    return {

        "status": "online",

        "site": NOME_SITE

    }


# =========================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000

    )
