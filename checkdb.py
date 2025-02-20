from db import get_database

# Comprobación de la conexión con la base de datos MongoDB
db = get_database()
print(f"db: {db}") 
if db is None:
    raise RuntimeError("La conexión a la base de datos falló")
