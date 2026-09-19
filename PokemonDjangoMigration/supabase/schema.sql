-- =========================================================
-- Esquema Supabase (PostgreSQL) para el proyecto Pokédex Django
-- =========================================================
-- Se mantiene la tabla "pokemon" tal como ya la tenías, solo se
-- le agrega UNIQUE a "nombre" (para poder hacer upsert / búsquedas
-- por nombre sin duplicados) y se agrega la tabla "pokemon_ataques"
-- porque la vista nueva exige mínimo 2 ataques por pokémon, y esa
-- información no existía en el esquema original.
-- =========================================================

CREATE TABLE IF NOT EXISTS pokemon (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(50) UNIQUE NOT NULL,
  imagen_frontal TEXT,
  imagen_posterior TEXT,
  imagen_shiny TEXT,
  altura NUMERIC,
  peso NUMERIC,
  tipos VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS pokemon_ataques (
  id SERIAL PRIMARY KEY,
  pokemon_id INTEGER NOT NULL REFERENCES pokemon(id) ON DELETE CASCADE,
  nombre_ataque VARCHAR(100) NOT NULL
);

-- =========================================================
-- Datos: los mismos 10 pokémon que ya tenías
-- (ON CONFLICT para poder correr este script varias veces sin duplicar)
-- =========================================================
INSERT INTO pokemon (nombre, imagen_frontal, imagen_posterior, imagen_shiny, altura, peso, tipos) VALUES
('pikachu',    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/25.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png',  0.4, 6.0,  'electric'),
('ditto',      'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/132.png', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/132.png', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/132.png', 0.3, 4.0,  'normal'),
('charizard',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png',   'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/6.png',   'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/6.png',   1.7, 90.5, 'fire,flying'),
('pidgey',     'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/16.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/16.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/16.png',  0.3, 1.8,  'normal,flying'),
('bulbasaur',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png',   'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/1.png',   'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/1.png',   0.7, 6.9,  'grass,poison'),
('psyduck',    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/54.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/54.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/54.png',  0.8, 19.6, 'water'),
('incineroar', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/727.png', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/727.png', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/727.png', 1.8, 83.0, 'fire,dark'),
('scorbunny',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/813.png', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/813.png', 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/813.png', 0.3, 4.5,  'fire'),
('fearow',     'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/22.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/22.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/22.png',  1.2, 38.0, 'normal,flying'),
('ekans',      'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/23.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/23.png',  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/23.png',  2.0, 6.9,  'poison')
ON CONFLICT (nombre) DO NOTHING;

-- =========================================================
-- Ataques (mínimo 2 por pokémon)
-- =========================================================
INSERT INTO pokemon_ataques (pokemon_id, nombre_ataque)
SELECT id, ataque FROM pokemon, (VALUES
  ('pikachu',    'Impactrueno'),
  ('pikachu',    'Ataque Rápido'),
  ('pikachu',    'Cola de Hierro'),
  ('ditto',      'Transformación'),
  ('ditto',      'Placaje'),
  ('charizard',  'Lanzallamas'),
  ('charizard',  'Ataque Ala'),
  ('charizard',  'Garra Dragón'),
  ('pidgey',     'Placaje'),
  ('pidgey',     'Tornado'),
  ('bulbasaur',  'Placaje'),
  ('bulbasaur',  'Látigo Cepa'),
  ('bulbasaur',  'Hoja Afilada'),
  ('psyduck',    'Pistola Agua'),
  ('psyduck',    'Confusión'),
  ('incineroar', 'Golpe Oscuro'),
  ('incineroar', 'Envite Ígneo'),
  ('scorbunny',  'Ascuas'),
  ('scorbunny',  'Ataque Rápido'),
  ('fearow',     'Pico Taladro'),
  ('fearow',     'Furia'),
  ('ekans',      'Envolver'),
  ('ekans',      'Picotazo Veneno')
) AS ataques(nombre_pokemon, ataque)
WHERE pokemon.nombre = ataques.nombre_pokemon;
