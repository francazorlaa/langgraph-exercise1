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



# ------------------------------ CURSOS ------------------------------
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



# ------------------------------ UNIVERSIDADES ------------------------------
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
