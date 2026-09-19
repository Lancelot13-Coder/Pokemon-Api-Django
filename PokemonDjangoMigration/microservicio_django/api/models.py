from django.db import models


class Pokemon(models.Model):
    """Refleja la tabla `pokemon` que ya existe en Supabase."""

    nombre = models.CharField(max_length=50, unique=True)
    imagen_frontal = models.TextField(blank=True, null=True)
    imagen_posterior = models.TextField(blank=True, null=True)
    imagen_shiny = models.TextField(blank=True, null=True)
    altura = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    peso = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    tipos = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "pokemon"
        ordering = ["id"]
        # La tabla ya existe en Supabase (creada con supabase/schema.sql),
        # así que Django no debe intentar crearla/alterarla con migraciones.
        managed = False

    def __str__(self):
        return self.nombre


class Ataque(models.Model):
    """Tabla nueva `pokemon_ataques` (mínimo 2 ataques por pokémon)."""

    pokemon = models.ForeignKey(
        Pokemon,
        related_name="ataques",
        on_delete=models.CASCADE,
        db_column="pokemon_id",
    )
    nombre_ataque = models.CharField(max_length=100)

    class Meta:
        db_table = "pokemon_ataques"
        managed = False

    def __str__(self):
        return f"{self.nombre_ataque} ({self.pokemon.nombre})"
