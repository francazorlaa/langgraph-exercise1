from db import get_database
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from bson import ObjectId
import logging

# Configuración del logger para el módulo actual
logger = logging.getLogger(__name__)

# Creación de la aplicación FastAPI
app = FastAPI()

# Intentar conectar a la base de datos
try:
    db = get_database()  # Obtener la conexión a la base de datos
    logger.info("Conectado a MongoDB")  # Log de éxito
except Exception as e:
    logger.error(f"Error al conectar a MongoDB: {e}")  # Log de error

# Definición del modelo de datos para una universidad
class University(BaseModel):
    name: str  # Nombre de la universidad
    city: str  # Ciudad de la universidad
    country: str  # País de la universidad
    courses: list[str]  # Lista de IDs de cursos

# Ruta para crear una nueva universidad
@app.post("/universities")
async def create_university(university: University):
    try:
        result = db["universities"].insert_one(university.dict())
        logger.info("Universidad añadida exitosamente")
        return {
            "id": str(result.inserted_id),
            "message": "Universidad añadida exitosamente"
        }
    except Exception as e:
        logger.error(f"Error al añadir universidad: {e}")
        raise HTTPException(status_code=500, detail="Error al añadir universidad")
    
# Ruta para obtener todas las universidades
@app.get("/universities")
async def get_universities():
    try:
        universities = db.universities.find()
        universities_list = []

        for university in universities:
            universities_list.append({
                "id": str(university["_id"]),  # Convertimos ObjectId a str
                "name": university["name"],
                "city": university["city"],
                "country": university["country"],
                "courses": [str(course) for course in university.get("courses", [])]  # Convertimos ObjectId en courses
            })

        logger.info("Universidades obtenidas exitosamente")
        return {"universities": universities_list, "message": "Universidades obtenidas exitosamente"}

    except Exception as e:
        logger.error(f"Error al obtener universidades: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener universidades")

# Ruta para obtener universidades por nombre
@app.get("/universities/name/{name}")
async def get_universities_by_name(name: str):
    try:
        universities = db["universities"].find({"name": name})
        universities_list = []
        
        for university in universities:
            universities_list.append({
                "id": str(university["_id"]),  # Convertimos ObjectId a str
                "name": university["name"],
                "city": university["city"],
                "country": university["country"],
                "courses": [str(course) for course in university.get("courses", [])]  # Convertimos ObjectId en courses
            })

        if not universities_list:
            logger.warning(f"No se encontraron universidades con el nombre '{name}'")
            raise HTTPException(status_code=404, detail=f"No se encontraron universidades con el nombre '{name}'")

        logger.info(f"Universidades con el nombre '{name}' recuperadas exitosamente")
        return universities_list

    except Exception as e:
        logger.error(f"Error al buscar universidades por nombre: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar universidades por nombre")

# Ruta para obtener una universidad por ID
@app.get("/universities/id/{university_id}")
async def get_university_by_id(university_id: str):
    try:
        obj_id = ObjectId(university_id)
        university = db["universities"].find_one({"_id": obj_id})
        if university:
            university["_id"] = str(university["_id"])  # Convertimos ObjectId a str
            university["courses"] = [str(course) for course in university.get("courses", [])]  # Convertimos los IDs de los cursos
            logger.info(f"Universidad con ID '{university_id}' recuperada exitosamente")
            return university
        logger.warning(f"Universidad con ID '{university_id}' no encontrada")
        raise HTTPException(status_code=404, detail=f"Universidad con ID '{university_id}' no encontrada")
    except Exception as e:
        logger.error(f"Error al buscar universidad por ID: {e}")
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

# Ruta para actualizar una universidad por ID
@app.put("/universities/updateUniversity/{id}")
async def update_university(id: str, university: University):
    try:
        obj_id = ObjectId(id)
        update_data = university.dict()
        update_data["courses"] = [ObjectId(course) for course in update_data.get("courses", [])]  # Convertimos a ObjectId
        
        result = db["universities"].update_one({"_id": obj_id}, {"$set": update_data})
        if result.matched_count == 0:
            logger.warning("Universidad no encontrada")
            raise HTTPException(status_code=404, detail="Universidad no encontrada")
        logger.info("Universidad actualizada exitosamente")
        return {"message": "Universidad actualizada exitosamente"}
    except Exception as e:
        logger.error(f"Error al actualizar universidad: {e}")
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

# Ruta para eliminar una universidad por ID
@app.delete("/universities/{university_id}")
async def delete_university(university_id: str):
    try:
        obj_university_id = ObjectId(university_id)
        result = db["universities"].delete_one({"_id": obj_university_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Universidad no encontrada")
        logger.info(f"Universidad con ID {university_id} eliminada exitosamente")
        return {"message": f"Universidad con ID {university_id} eliminada exitosamente"}
    except Exception as e:
        logger.error(f"Error al eliminar universidad: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar universidad")

# Ruta para añadir un curso a una universidad por ID
@app.post("/universities/{university_id}/courses/{course_id}")
async def add_course_to_university(university_id: str, course_id: str):
    try:
        obj_university_id = ObjectId(university_id)
        obj_course_id = ObjectId(course_id)
        result = db["universities"].update_one(
            {"_id": obj_university_id},
            {"$addToSet": {"courses": str(obj_course_id)}}  # Convertimos el ObjectId en string antes de insertar
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Universidad no encontrada")
        logger.info(f"Curso con ID {course_id} añadido a la universidad con ID {university_id} exitosamente")
        return {"message": f"Curso con ID {course_id} añadido a la universidad con ID {university_id} exitosamente"}
    except Exception as e:
        logger.error(f"Error al añadir curso a la universidad: {e}")
        raise HTTPException(status_code=500, detail="Error al añadir curso a la universidad")
