from django.contrib import admin

from .models import AtaqueLocal, PokemonLocal


class AtaqueLocalInline(admin.TabularInline):
    model = AtaqueLocal
    extra = 2  # deja 2 filas listas: se piden mínimo 2 ataques por pokémon


@admin.register(PokemonLocal)
class PokemonLocalAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "altura", "peso", "tipos")
    search_fields = ("nombre",)
    inlines = [AtaqueLocalInline]
