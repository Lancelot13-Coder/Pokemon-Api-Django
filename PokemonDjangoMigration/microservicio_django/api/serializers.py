from rest_framework import serializers

from .models import Ataque, Pokemon


class AtaqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ataque
        fields = ["id", "nombre_ataque"]


class PokemonSerializer(serializers.ModelSerializer):
    ataques = AtaqueSerializer(many=True, read_only=True)

    class Meta:
        model = Pokemon
        fields = [
            "id",
            "nombre",
            "imagen_frontal",
            "imagen_posterior",
            "imagen_shiny",
            "altura",
            "peso",
            "tipos",
            "ataques",
        ]
