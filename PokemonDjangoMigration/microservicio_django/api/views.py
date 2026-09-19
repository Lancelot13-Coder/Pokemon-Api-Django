from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Pokemon
from .serializers import PokemonSerializer


@api_view(["GET"])
def lista_pokemon(request):
    """GET /api/pokemon/ -> lista completa (mínimo 10 pokémon en Supabase)."""
    pokemones = Pokemon.objects.prefetch_related("ataques").all()
    serializer = PokemonSerializer(pokemones, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def detalle_pokemon(request, nombre):
    """GET /api/pokemon/<nombre>/ -> un pokémon por nombre (case-insensitive)."""
    try:
        pokemon = Pokemon.objects.prefetch_related("ataques").get(nombre__iexact=nombre)
    except Pokemon.DoesNotExist:
        return Response(
            {"error": "Pokémon no encontrado"}, status=status.HTTP_404_NOT_FOUND
        )
    serializer = PokemonSerializer(pokemon)
    return Response(serializer.data)


@api_view(["GET"])
def health(request):
    """GET /api/health/ -> usado por Render y por el frontend para chequear disponibilidad."""
    return Response({"status": "ok"})
