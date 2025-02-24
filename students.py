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


# Definición del modelo de datos para un estudiante
class Student(BaseModel):
    name: str  # Nombre del estudiante
    age: int   # Edad del estudiante

# Ruta para crear un nuevo estudiante
@app.post("/students")
async def create_students(student: Student):
    try:
        result = db["students"].insert_one(student.dict())
        logger.info("Estudiante añadido exitosamente")
        return {
            "id": str(result.inserted_id),
            "message": "Estudiante añadido exitosamente"
        }
    except Exception as e:
        logger.error(f"Error al añadir estudiante: {e}")
        raise HTTPException(status_code=500, detail="Error al añadir estudiante")

# Ruta para obtener todos los estudiantes
@app.get("/students")
async def get_students():
    try:
        students = list(db.students.find())
        for student in students:
            student["_id"] = str(student["_id"])
        logger.info("Estudiantes obtenidos exitosamente")
        return {"students": students, "message": "Estudiantes obtenidos exitosamente"}
    except Exception as e:
        logger.error(f"Error al obtener estudiantes: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estudiantes")

# Ruta para obtener un estudiante por nombre (solo el primero que coincida)
@app.get("/students/{name}")
async def get_one_student(name: str):
    try:
        student = db["students"].find_one({"name": name})
        if student:
            student["_id"] = str(student["_id"])
            logger.info("Estudiante recuperado exitosamente")
            return student
        logger.warning("Estudiante no encontrado")
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    except Exception as e:
        logger.error(f"Error al buscar estudiante: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar estudiante")

# Ruta para obtener estudiantes por nombre
@app.get("/students/name/{name}")
async def get_students_by_name(name: str):
    try:
        students = db["students"].find({"name": name})
        students_list = [{"id": str(student["_id"]), "name": student["name"], "age": student["age"]} for student in students]
        if not students_list:
            logger.warning(f"No se encontraron estudiantes con el nombre '{name}'")
            raise HTTPException(status_code=404, detail=f"No se encontraron estudiantes con el nombre '{name}'")
        logger.info(f"Estudiantes con el nombre '{name}' recuperados exitosamente")
        return students_list
    except Exception as e:
        logger.error(f"Error al buscar estudiantes por nombre: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar estudiantes por nombre")

# Ruta para obtener un estudiante por ID
@app.get("/students/id/{student_id}")
async def get_student_by_id(student_id: str):
    try:
        obj_id = ObjectId(student_id)
        student = db["students"].find_one({"_id": obj_id})
        if student:
            student["_id"] = str(student["_id"])
            logger.info(f"Estudiante con ID '{student_id}' recuperado exitosamente")
            return student
        logger.warning(f"Estudiante con ID '{student_id}' no encontrado")
        raise HTTPException(status_code=404, detail=f"Estudiante con ID '{student_id}' no encontrado")
    except Exception as e:
        logger.error(f"Error al buscar estudiante por ID: {e}")
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

# Ruta para actualizar un estudiante por ID
@app.put("/students/updateStudent/{id}")
async def update_student(id: str, student: Student):
    try:
        obj_id = ObjectId(id)
        result = db.students.update_one({"_id": obj_id}, {"$set": student.dict()})
        if result.matched_count == 0:
            logger.warning("Estudiante no encontrado")
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        logger.info("Estudiante actualizado exitosamente")
        return {"message": "Estudiante actualizado exitosamente"}
    except Exception as e:
        logger.error(f"Error al actualizar estudiante: {e}")
        raise HTTPException(status_code=400, detail="Formato de ID inválido")

# Ruta para eliminar un estudiante por ID
@app.delete("/students/deleteById/{id}")
async def delete_student_by_id(id: str):
    try:
        result = db.students.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            logger.warning(f"No se encontró estudiante con ID '{id}' para eliminar")
            raise HTTPException(status_code=404, detail=f"No se encontró estudiante con ID '{id}' para eliminar")
        logger.info(f"Estudiante con ID '{id}' eliminado exitosamente")
        return {"message": f"Estudiante con ID '{id}' eliminado exitosamente"}
    except Exception as e:
        logger.error(f"Error al eliminar estudiante con ID '{id}': {e}")
        raise HTTPException(status_code=400, detail="Formato de ID inválido")
