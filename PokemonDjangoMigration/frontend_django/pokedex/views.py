import requests
from django.conf import settings
from django.shortcuts import render

from .models import PokemonLocal


def _consultar_local(nombre):
    """Busca el pokémon en la base de datos local SQLite."""
    try:
        pokemon = PokemonLocal.objects.prefetch_related("ataques").get(
            nombre__iexact=nombre
        )
    except PokemonLocal.DoesNotExist:
        return None

    return {
        "nombre": pokemon.nombre,
        "imagen_frontal": pokemon.imagen_frontal,
        "altura": pokemon.altura,
        "peso": pokemon.peso,
        "tipos": pokemon.lista_tipos(),
        "ataques": [a.nombre_ataque for a in pokemon.ataques.all()],
        "origen": "local",
    }


def _consultar_microservicio(nombre):
    """
    Llama al microservicio propio (Django + DRF desplegado en Render),
    que a su vez consulta Supabase.

    Devuelve:
      - dict con los datos si lo encontró
      - "not_found" si el microservicio respondió pero no existe ese pokémon
      - lanza requests.RequestException si no hay internet / el servicio
        no responde (quien llama a esta función debe capturarlo)
    """
    url = f"{settings.MICROSERVICE_URL}/api/pokemon/{nombre}/"
    respuesta = requests.get(url, timeout=settings.MICROSERVICE_TIMEOUT)

    if respuesta.status_code == 404:
        return "not_found"

    respuesta.raise_for_status()
    data = respuesta.json()

    return {
        "nombre": data.get("nombre"),
        "imagen_frontal": data.get("imagen_frontal"),
        "altura": data.get("altura"),
        "peso": data.get("peso"),
        "tipos": (data.get("tipos") or "").split(",") if data.get("tipos") else [],
        "ataques": [a.get("nombre_ataque") for a in data.get("ataques", [])],
        "origen": "nube",
    }


def home(request):
    """
    Vista principal (la del wireframe), con DOS botones separados:

    - Botón "Buscar" (origen=auto): intenta primero el microservicio propio
      (Supabase, en la nube). Si NO hay conexión a internet o el
      microservicio no responde, cae automáticamente a la copia local en
      SQLite, SIN mostrar ningún mensaje de error de conexión al usuario.
      Si sí hay conexión pero ese pokémon no existe en Supabase, igual
      revisa la copia local (por si el usuario solo lo cargó ahí).

    - Botón "SQLite" (origen=local): consulta ÚNICAMENTE la base de datos
      local en SQLite, sin intentar red para nada. Útil para forzar el
      modo offline manualmente, o para probar los datos que cargaste tú
      mismo desde /admin.
    """
    contexto = {
        "pokemon": None,
        "buscado": False,
        "nombre_query": "",
        "no_encontrado": False,
        "origen_elegido": "auto",
    }

    nombre = request.GET.get("pokemon", "").strip()
    origen_elegido = request.GET.get("origen", "auto")
    if origen_elegido not in ("auto", "local"):
        origen_elegido = "auto"

    if nombre:
        contexto["buscado"] = True
        contexto["nombre_query"] = nombre
        contexto["origen_elegido"] = origen_elegido
        pokemon_data = None

        if origen_elegido == "local":
            # El usuario forzó el botón "SQLite": ni se intenta la red.
            pokemon_data = _consultar_local(nombre)
        else:
            try:
                resultado = _consultar_microservicio(nombre)
                if resultado == "not_found":
                    pokemon_data = _consultar_local(nombre)
                else:
                    pokemon_data = resultado
            except (requests.ConnectionError, requests.Timeout, requests.RequestException):
                # Sin internet / microservicio caído -> usar SQLite local, sin error visible
                pokemon_data = _consultar_local(nombre)

        contexto["pokemon"] = pokemon_data
        contexto["no_encontrado"] = pokemon_data is None

    return render(request, "pokedex/home.html", contexto)
