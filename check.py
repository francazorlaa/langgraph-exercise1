import os
from dotenv import load_dotenv

# Cargar las variables del .env
load_dotenv()

# Imprimir todas las variables de entorno disponibles
for key, value in os.environ.items():
    if "KEY" in key or "SECRET" in key:  # Evitar mostrar credenciales en la consola
        print(f"{key}: [HIDDEN]")
    else:
        print(f"{key}: {value}")
