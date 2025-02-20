from db import get_database
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi import Body
from bson import ObjectId
import logging

# Logging level and format
logger = logging.getLogger(__name__)

# Creating FastAPI application
app = FastAPI()

# Try to connect to the database
try:
    db = get_database()
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")

# Inserting students into the database
class Student(BaseModel):
    name: str
    age: int

@app.post("/students")
async def create_students(student: Student):
    result = db["students"].insert_one(student.dict())

    return {
        "id": str(result.inserted_id),
        "message": "Student added successfully"
    }

# Simple route creation and call
@app.get("/students")
async def get_students():
    students = list(db.students.find())
    logger.info(students)
    for student in students:
        logger.info(student)
        student["_id"] = str(student["_id"])
    return {"message": "Students fetched successfully"}     


# Route call to get one student (just the first)
@app.get("/students/{name}")
async def get_one_student(name: str):
    student = db["students"].find_one({"name": name})

    if student:
        logger.info(f"Student retrieved successfully.")
        return {
            "id": str(student["_id"]),
            "name": student["name"],
            "age": student["age"]
        }
    else:
        logger.warning(f"Student not found in the database.")
        return {"message": f"Student not found"}

# Get students by name
@app.get("/students/name/{name}")
async def get_students_by_name(name: str):
    students = db["students"].find({"name": name})
    students_list = [
        {"id": str(student["_id"]), "name": student["name"], "age": student["age"]}
        for student in students
    ]

    if not students_list:
        logger.warning(f"No students found with name '{name}'")
        return {"message": f"No students found with name '{name}'"}
    
    logger.info(f"Students with name '{name}' retrieved successfully.")
    return students_list

# Get student by ID
@app.get("/students/id/{student_id}")
async def get_student_by_id(student_id: str):
    try:
        # Convertir el ID a ObjectId
        obj_id = ObjectId(student_id)
        student = db["students"].find_one({"_id": obj_id})

        if student:
            student_json = {
                "id": str(student["_id"]),  # Convertimos ObjectId a string
                "name": student["name"],
                "age": student["age"]
            }
            logger.info(f"Student with ID '{student_id}' retrieved successfully: {student_json}")
            return student_json
        else:
            logger.warning(f"Student with ID '{student_id}' not found in the database.")
            return {"message": f"Student with ID '{student_id}' not found"}

    except Exception as e:
        logger.error(f"Invalid ID format: {student_id}, Error: {e}")
        return {"message": "Invalid ID format"}

# Update student by ID
@app.put("/students/updateStudent/{id}")
async def update_student(id: str, student: Student):
    try:
        obj_id = ObjectId(id) 
    except Exception:
        logger.error("Invalid ID format")
        return {"message": "Invalid ID format"}

    result = db.students.update_one({"_id": obj_id}, {"$set": {
        "name": student.name,
        "age": student.age
    }})

    if result.matched_count == 0:
        logger.warning("Student not found")
        return {"message": "Student not found"}

    logger.info("Student updated successfully")
    return {"message": "Student updated successfully"}

# Delete student by ID
@app.delete("/students/deleteById/{id}")
async def delete_student_by_id(id: str):
    try:
        result = db.students.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            logger.warning(f"No student found with ID '{id}' to delete.")
            return {"message": f"No student found with ID '{id}' to delete"}

        logger.info(f"Student with ID '{id}' deleted successfully.")
        return {"message": f"Student with ID '{id}' deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting student with ID '{id}': {e}")
        return {"message": "Error deleting student"}
