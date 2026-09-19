# Pokédex — Migración a Django (Expo/React/Node → Django)

Migración de tu proyecto original (Expo + React Native ⇄ microservicio
Node/Express ⇄ Supabase, desplegado en Railway) a **Django puro**,
manteniendo Supabase como base en la nube y cambiando el despliegue del
microservicio de Railway a **Render**.

## Arquitectura

```
┌─────────────────────────┐        HTTP (requests)        ┌──────────────────────────────┐
│      frontend_django     │ ─────────────────────────────▶│      microservicio_django     │
│  (la vista que ves en    │                                │   (Django + DRF, API REST)    │
│   la imagen que enviaste)│ ◀───────────────────────────── │   Desplegado en Render,       │
│                          │        JSON                    │   conectado por GitHub        │
│  DB propia: SQLite       │                                │   DB propia: Supabase (Postgres)
│  (offline, la llenas tú  │                                │                               │
│  desde /admin)           │                                │                               │
└─────────────────────────┘                                └──────────────────────────────┘
```

- **`microservicio_django/`**: reemplaza tu backend Node/Express. Es la
  única parte que habla con Supabase. Se sube a GitHub y se despliega en
  Render (igual patrón que antes con Railway).
- **`frontend_django/`**: reemplaza tu app Expo/React. Tiene la vista con
  el buscador. Le pega por HTTP al microservicio; si no hay internet o el
  microservicio no responde, **cae automáticamente a su propia base
  SQLite local**, sin mostrar ningún error de conexión al usuario.
- **`supabase/schema.sql`**: tu esquema original + una tabla nueva
  `pokemon_ataques` (no existía antes, y la necesitas porque la vista
  pide mínimo 2 ataques por pokémon).

---

## 1. Base de datos en Supabase

1. Entra a tu proyecto de Supabase → **SQL Editor**.
2. Pega y ejecuta el contenido de `supabase/schema.sql`.
   - Crea (si no existe) la tabla `pokemon` con tus 10 pokémon.
   - Crea la tabla nueva `pokemon_ataques` con al menos 2 ataques por
     pokémon.
3. En **Project Settings → Database → Connection string → URI**, copia la
   cadena de conexión. La usarás como `DATABASE_URL` del microservicio.

> Si ya tenías la tabla `pokemon` creada de antes, el script no la
> duplica (usa `IF NOT EXISTS` y `ON CONFLICT ... DO NOTHING`); solo
> agrega lo que falta (la tabla de ataques).

---

## 2. Microservicio Django (`microservicio_django/`) → Render

### Probarlo en local primero

```bash
cd microservicio_django
python -m venv venv
# Windows: venv\Scripts\activate    |    Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edita .env y pon tu DATABASE_URL real de Supabase

python manage.py migrate      # crea solo las tablas propias de Django (auth, admin, etc.)
python manage.py createsuperuser
python manage.py runserver 8001
```

Prueba en el navegador:
- `http://127.0.0.1:8001/api/pokemon/` → lista completa
- `http://127.0.0.1:8001/api/pokemon/pikachu/` → un pokémon
- `http://127.0.0.1:8001/api/health/` → chequeo de salud

### Desplegar en Render (conectado a GitHub)

1. Sube la carpeta `microservicio_django/` como repositorio a GitHub
   (puede ser el mismo repo que ya tenías, reemplazando el contenido del
   backend Node por este).
2. En [render.com](https://render.com) → **New +** → **Web Service** →
   conecta ese repositorio de GitHub.
3. Configura:
   - **Build Command:** `pip install -r requirements.txt && python manage.py migrate`
   - **Start Command:** `gunicorn microservicio.wsgi:application`
4. En la pestaña **Environment**, agrega las variables de `.env.example`:
   - `DATABASE_URL` (la de Supabase)
   - `SECRET_KEY` (cualquier cadena larga y aleatoria)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=tu-servicio.onrender.com`
   - `CORS_ALLOWED_ORIGINS` (la URL donde corra tu `frontend_django`, por
     ejemplo `https://tu-frontend.onrender.com`)
5. Deploy. Render te da una URL pública tipo
   `https://pokemon-microservicio.onrender.com`; esa es la que usarás en
   el frontend como `MICROSERVICE_URL`.

(Incluí también un `render.yaml` opcional por si prefieres usar
"Blueprints" de Render en vez de configurar todo a mano.)

---

## 3. Django frontend (`frontend_django/`) — la vista de la imagen

### En local

```bash
cd frontend_django
python -m venv venv
# Windows: venv\Scripts\activate    |    Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Pon aquí la URL del microservicio (local en 8001, o ya la de Render)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

Abre `http://127.0.0.1:8000/`.

### Cargar los 10 pokémon en SQLite (modo offline)

Como pediste, esto lo haces tú mismo desde el panel de administrador:

1. Entra a `http://127.0.0.1:8000/admin/` con el superusuario que creaste.
2. Ve a **Pokémon (local / SQLite)** → **Agregar**.
3. Llena nombre, imagen frontal, altura, peso, tipos, y agrega **mínimo 2
   ataques** en la sección de abajo (ya viene con 2 filas listas).
4. Repite para tus 10 pokémon.

Si en algún momento quieres cargarlos todos de una sola vez en vez de
uno por uno (por ejemplo para probar rápido), incluí un fixture opcional:

```bash
python manage.py loaddata pokedex/fixtures/pokemon_offline.json
```

### Cómo funciona la búsqueda (la lógica que pediste)

En `pokedex/views.py`, cuando buscas un pokémon:

1. Primero intenta el microservicio (`MICROSERVICE_URL`), que consulta
   Supabase.
2. Si el microservicio responde pero el pokémon **no existe**, revisa si
   lo tienes cargado en tu copia local SQLite.
3. Si **no hay conexión a internet** o el microservicio no responde a
   tiempo (`MICROSERVICE_TIMEOUT`, 4 segundos por defecto), cae
   automáticamente a SQLite local, **sin mostrar ningún mensaje de error
   de conexión** — la búsqueda simplemente funciona con los datos
   locales.

La vista muestra un pequeño indicador ("🌐 datos de Supabase" /
"💾 datos de SQLite local") para que en tus pruebas puedas confirmar
cuál fuente respondió, pero nunca un mensaje de error de red.

### Desplegar el frontend

Puedes desplegarlo igual que el microservicio (Render, otro servicio
web con `gunicorn frontend_django.wsgi:application`) o correrlo en tu
propio equipo — recuerda que su base SQLite vive en el disco donde corra
el proceso, así que si lo despliegas en Render con el plan gratuito
(disco efímero), los datos locales se perderán en cada redeploy; para
mantenerlos de forma persistente en la nube usarían un "Persistent Disk"
de Render, o simplemente correr este frontend en tu máquina/local para
el modo offline.

---

## 4. Resumen de endpoints del microservicio

| Método | Ruta                     | Descripción                              |
|--------|--------------------------|-------------------------------------------|
| GET    | `/api/pokemon/`          | Lista todos los pokémon (con sus ataques) |
| GET    | `/api/pokemon/<nombre>/` | Un pokémon por nombre (case-insensitive)  |
| GET    | `/api/health/`           | Chequeo de disponibilidad                 |

Cada pokémon incluye: `nombre`, `imagen_frontal`, `imagen_posterior`,
`imagen_shiny`, `altura`, `peso`, `tipos`, y `ataques` (lista de objetos
`{id, nombre_ataque}`, mínimo 2 por pokémon).

---

## 5. Qué cambia respecto al proyecto original

| Antes                              | Ahora                                        |
|-------------------------------------|-----------------------------------------------|
| App Expo / React Native             | Vista Django (`frontend_django`)              |
| Backend Node.js + Express + `pg`    | Microservicio Django + DRF (`microservicio_django`) |
| Deploy backend en Railway           | Deploy backend en Render                      |
| Solo base en Supabase               | Supabase (nube) **+** SQLite local (offline)  |
| Sin campo de ataques                | Tabla `pokemon_ataques` (mínimo 2 por pokémon)|
| Sin modo offline                    | Fallback automático a SQLite si no hay internet |

---

## 6. Carpeta `proyecto_original_react/`

No se incluye en este zip (pesa mucho por `node_modules`), pero la
tienes intacta en tu `PokemonApi.zip` original, por si necesitas comparar
algo puntual de la lógica anterior (por ejemplo, los tipos y sus colores
en `app/(tabs)/index.tsx`).
