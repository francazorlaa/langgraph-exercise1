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

# Definición del modelo de datos para un curso
class Course(BaseModel):
    name: str  # Nombre del curso
    faculty: str  # Facultad del curso
    students: list  # Lista de estudiantes en el curso

# Ruta para crear un nuevo curso
@app.post("/courses")
async def create_course(course: Course):
    try:
        result = db["courses"].insert_one(course.dict())
        logger.info("Curso añadido exitosamente")
        return {
            "id": str(result.inserted_id),
            "message": "Curso añadido exitosamente"
        }
    except Exception as e:
        logger.error(f"Error al añadir curso: {e}")
        raise HTTPException(status_code=500, detail="Error al añadir curso")

# Ruta para obtener todos los cursos
@app.get("/courses")
async def get_courses():
    try:
        courses = list(db.courses.find())
        for course in courses:
            course["_id"] = str(course["_id"])
        logger.info("Cursos obtenidos exitosamente")
        return {"courses": courses, "message": "Cursos obtenidos exitosamente"}
    except Exception as e:
        logger.error(f"Error al obtener cursos: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener cursos")

# Ruta para obtener un curso por nombre (solo el primero que coincida)
@app.get("/courses/{name}")
async def get_one_course(name: str):
    try:
        course = db["courses"].find_one({"name": name})
        if course:
            course["_id"] = str(course["_id"])
            logger.info("Curso recuperado exitosamente")
            return course
        logger.warning("Curso no encontrado")
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    except Exception as e:
        logger.error(f"Error al buscar curso: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar curso")

# Ruta para obtener cursos por nombre
@app.get("/courses/name/{name}")
async def get_courses_by_name(name: str):
    try:
        courses = db["courses"].find({"name": name})
        courses_list = [{"id": str(course["_id"]), "name": course["name"], "faculty": course["faculty"], "students": course["students"]} for course in courses]
        if not courses_list:
            logger.warning(f"No se encontraron cursos con el nombre '{name}'")
            raise HTTPException(status_code=404, detail=f"No se encontraron cursos con el nombre '{name}'")
        logger.info(f"Cursos con el nombre '{name}' recuperados exitosamente")
        return courses_list
    except Exception as e:
        logger.error(f"Error al buscar cursos por nombre: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar cursos por nombre")

# Ruta para obtener un curso por ID
@app.get("/courses/id/{course_id}")
async def get_course_by_id(course_id: str):
    try:
        obj_id = ObjectId(course_id)
        course = db["courses"].find_one({"_id": obj_id})
        if course:
            course["_id"] = str(course["_id"])
            logger.info(f"Curso con ID '{course_id}' recuperado exitosamente")
            return course
        logger.warning(f"Curso con ID '{course_id}' no encontrado")
        raise HTTPException(status_code=404, detail=f"Curso con ID '{course_id}' no encontrado")
    except Exception as e:
        logger.error(f"Error al buscar curso por ID: {e}")
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

# Ruta para actualizar un curso por ID
@app.put("/courses/updateCourse/{id}")
async def update_course(id: str, course: Course):
    try:
        obj_id = ObjectId(id)
        result = db.courses.update_one({"_id": obj_id}, {"$set": course.dict()})
        if result.matched_count == 0:
            logger.warning("Curso no encontrado")
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        logger.info("Curso actualizado exitosamente")
        return {"message": "Curso actualizado exitosamente"}
    except Exception as e:
        logger.error(f"Error al actualizar curso: {e}")
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

# Ruta para eliminar un curso por ID
@app.delete("/courses/deleteById/{id}")
async def delete_course_by_id(id: str):
    try:
        # Intenta eliminar un curso de la base de datos usando el ID proporcionado
        result = db.courses.delete_one({"_id": ObjectId(id)})
        # Verifica si no se eliminó ningún curso
        if result.deleted_count == 0:
            # Registra una advertencia si no se encontró el curso
            logger.warning(f"No se encontró curso con ID '{id}' para eliminar")
            # Lanza una excepción HTTP 404 si no se encontró el curso
            raise HTTPException(status_code=404, detail=f"No se encontró curso con ID '{id}' para eliminar")
        # Registra un mensaje de éxito si el curso fue eliminado
        logger.info(f"Curso con ID '{id}' eliminado exitosamente")
        # Devuelve un mensaje de éxito
        return {"message": f"Curso con ID '{id}' eliminado exitosamente"}
    except Exception as e:
        # Registra un error si ocurre una excepción
        logger.error(f"Error al eliminar curso con ID '{id}': {e}")
        # Lanza una excepción HTTP 400 si el formato del ID es inválido
        raise HTTPException(status_code=400, detail="Formato de ID inválido")


# ------------------------------ AÑADIR O ELIMINAR ESTUDIANTE A CURSO ------------------------------
# Ruta para añadir el ID de un estudiante al array de estudiantes de un curso
@app.post("/courses/addstudent/{course_id}/{student_id}")
async def add_student_to_course(course_id: str, student_id: str):
    try:
        # Validar y convertir course_id y student_id a ObjectId si es necesario
        try:
            obj_course_id = ObjectId(course_id)
            obj_student_id = ObjectId(student_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de ID inválido")

        # Actualizar el curso agregando el student_id al array de estudiantes
        result = db.courses.update_one(
            {"_id": obj_course_id},
            {"$push": {"students": str(obj_student_id)}}  # Se almacena como string en el array
        )

        # Verificar si el curso fue encontrado y actualizado
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        logger.info(f"ID del estudiante {student_id} añadido al curso con ID {course_id} exitosamente")
        return {"message": f"ID del estudiante {student_id} añadido al curso con ID {course_id} exitosamente"}

    except Exception as e:
        logger.error(f"Error al añadir ID del estudiante al curso: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Ruta para eliminar el ID de un estudiante del array de estudiantes de un curso
@app.delete("/courses/removestudent/{course_id}/{student_id}")
async def remove_student_from_course(course_id: str, student_id: str):
    try:
        # Validar y convertir course_id y student_id a ObjectId si es necesario
        try:
            obj_course_id = ObjectId(course_id)
            obj_student_id = ObjectId(student_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de ID inválido")

        # Actualizar el curso eliminando el student_id del array de estudiantes
        result = db.courses.update_one(
            {"_id": obj_course_id},
            {"$pull": {"students": str(obj_student_id)}}  # Se elimina el ID del array
        )

        # Verificar si el curso fue encontrado y actualizado
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        logger.info(f"ID del estudiante {student_id} eliminado del curso con ID {course_id} exitosamente")
        return {"message": f"ID del estudiante {student_id} eliminado del curso con ID {course_id} exitosamente"}

    except Exception as e:
        logger.error(f"Error al eliminar ID del estudiante del curso: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

