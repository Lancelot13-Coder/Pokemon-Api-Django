from django.apps import AppConfig


class PokedexConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pokedex"
    verbose_name = "Pokédex (vista + copia local SQLite)"
