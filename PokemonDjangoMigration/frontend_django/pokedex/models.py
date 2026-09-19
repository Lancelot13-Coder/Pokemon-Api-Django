from django.db import models


class PokemonLocal(models.Model):
    """
    Copia local (SQLite) de los mismos pokémon que están en Supabase.
    Se llena manualmente desde /admin, tal como pediste, para que la
    app funcione sin conexión a internet.
    """

    nombre = models.CharField(max_length=50, unique=True)
    imagen_frontal = models.TextField(
        blank=True, null=True, help_text="URL o ruta de la imagen frontal del pokémon"
    )
    imagen_posterior = models.TextField(blank=True, null=True)
    imagen_shiny = models.TextField(blank=True, null=True)
    altura = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    peso = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    tipos = models.CharField(
        max_length=100, blank=True, help_text="Ej: fire,flying (separados por coma)"
    )

    class Meta:
        verbose_name = "Pokémon (local / SQLite)"
        verbose_name_plural = "Pokémon (local / SQLite)"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def lista_tipos(self):
        return [t.strip() for t in self.tipos.split(",") if t.strip()]


class AtaqueLocal(models.Model):
    """Ataques del pokémon local (mínimo 2 por pokémon, como en Supabase)."""

    pokemon = models.ForeignKey(
        PokemonLocal, related_name="ataques", on_delete=models.CASCADE
    )
    nombre_ataque = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Ataque (local)"
        verbose_name_plural = "Ataques (local)"

    def __str__(self):
        return f"{self.nombre_ataque} ({self.pokemon.nombre})"
