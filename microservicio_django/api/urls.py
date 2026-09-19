from django.urls import path

from . import views

urlpatterns = [
    path("pokemon/", views.lista_pokemon, name="lista_pokemon"),
    path("pokemon/<str:nombre>/", views.detalle_pokemon, name="detalle_pokemon"),
    path("health/", views.health, name="health"),
]
