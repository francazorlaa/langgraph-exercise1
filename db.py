import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environmental variables
load_dotenv()

# Nivel y formato de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Probar la conexión
def get_database():
    try: 
        # Obtener la URI de MongoDB de las variables de entorno
        MONGO_URI = os.getenv("MONGODB_URI")
        # Crear un cliente de MongoDB
        client = MongoClient(MONGO_URI)
        # El comando ismaster es barato y no requiere autenticación
        client.admin.command('ismaster')

        # Usando logger
        db = client['test']
        logger.info("Conectado a MongoDB")
        return db
    except Exception as e:
        logger.error(f"Error al conectar a MongoDB: {e}")
        raise
