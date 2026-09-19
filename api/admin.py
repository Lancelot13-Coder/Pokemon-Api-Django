from django.contrib import admin

from .models import Ataque, Pokemon


class AtaqueInline(admin.TabularInline):
    model = Ataque
    extra = 1


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "altura", "peso", "tipos")
    search_fields = ("nombre",)
    inlines = [AtaqueInline]
