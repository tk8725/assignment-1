from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel

# --- Database Setup ---
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/student"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    experience = Column(Integer, nullable=False)


# --- Schemas ---
class StudentBase(BaseModel):
    name: str
    age: int
    grade: str


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    grade: str | None = None


class StudentOut(StudentBase):
    id: int

    class Config:
        orm_mode = True


class TeacherBase(BaseModel):
    name: str
    subject: str
    experience: int


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    name: str | None = None
    subject: str | None = None
    experience: int | None = None


class TeacherOut(TeacherBase):
    id: int

    class Config:
        orm_mode = True


# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- FastAPI App ---
app = FastAPI()


# --- Create Tables on Startup ---
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


# --- Student Endpoints ---
@app.get("/students/", response_model=list[StudentOut])
def read_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@app.get("/students/{student_id}", response_model=StudentOut)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post("/students/", response_model=StudentOut, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    existing = db.get(Student, student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in student.dict(exclude_unset=True).items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/students/{student_id}", response_model=StudentOut)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    existing = db.get(Student, student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(existing)
    db.commit()
    return existing


# --- Teacher Endpoints ---
@app.get("/teachers/", response_model=list[TeacherOut])
def read_teachers(db: Session = Depends(get_db)):
    return db.query(Teacher).all()


@app.get("/teachers/{teacher_id}", response_model=TeacherOut)
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@app.post("/teachers/", response_model=TeacherOut, status_code=201)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    new_teacher = Teacher(**teacher.dict())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@app.put("/teachers/{teacher_id}", response_model=TeacherOut)
def update_teacher(teacher_id: int, teacher: TeacherUpdate, db: Session = Depends(get_db)):
    existing = db.get(Teacher, teacher_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Teacher not found")
    for key, value in teacher.dict(exclude_unset=True).items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/teachers/{teacher_id}", response_model=TeacherOut)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    existing = db.get(Teacher, teacher_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(existing)
    db.commit()
    return existing
