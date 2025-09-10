import sqlite3
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog

# ==============================
# Database Setup
# ==============================
class Database:
    def __init__(self, db_name="Data.sqlite3"):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS Student (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_name TEXT,
            Student_id INTEGER UNIQUE,
            Email TEXT UNIQUE
        )
        """)
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS Project (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Project_name TEXT UNIQUE,
            Description TEXT,
            Student_id INTEGER,
            Year REAL,
            Owner TEXT,
            FOREIGN KEY(Student_id) REFERENCES Student(Student_id)
        )
        """)
        self.conn.commit()


# ==============================
# Student Class
# ==============================
class Student:
    def __init__(self, db, student_name=None, student_id=None, student_email=None):
        self.db = db
        self.name = student_name
        self.student_id = student_id
        self.email = student_email

    def exists(self):
        self.db.c.execute("SELECT 1 FROM Student WHERE Student_id=?", (self.student_id,))
        return self.db.c.fetchone() is not None

    def email_exists(self):
        self.db.c.execute("SELECT 1 FROM Student WHERE Email=?", (self.email,))
        return self.db.c.fetchone() is not None

    def save(self):
        try:
            with self.db.conn:
                self.db.c.execute(
                    "INSERT INTO Student (Student_name, Student_id, Email) VALUES (?,?,?)",
                    (self.name, self.student_id, self.email)
                )
            print(f"✅ เพิ่มนักศึกษา {self.name} เรียบร้อยแล้ว")
        except sqlite3.IntegrityError as e:
            print("❌ Error:", e)


# ==============================
# Project Class
# ==============================
class Project:
    def __init__(self, db, project_name=None, description=None, year=None, student_id=None, owner=None):
        self.db = db
        self.name = project_name
        self.description = description
        self.year = year
        self.student_id = student_id
        self.owner = owner

    def exists(self):
        self.db.c.execute("SELECT 1 FROM Project WHERE Project_name=?", (self.name,))
        return self.db.c.fetchone() is not None

    def save(self):
        try:
            with self.db.conn:
                self.db.c.execute(
                    "INSERT INTO Project (Project_name, Description, Year, Student_id, Owner) VALUES (?,?,?,?,?)",
                    (self.name, self.description, self.year, self.student_id, self.owner)
                )
            print(f"✅ สร้างโครงการ {self.name} เรียบร้อยแล้ว")
        except sqlite3.IntegrityError as e:
            print("❌ Error:", e)

    def create_folder(self, parent="Project_list"):
        path = os.path.join(parent, self.name)
        os.makedirs(path, exist_ok=True)
        print(f"📂 สร้างโฟลเดอร์ {path}")


# ==============================
# Project File Manager
# ==============================
class ProjectFileManager:
    def __init__(self, parent_folder="Project_list"):
        self.parent_folder = parent_folder

    def upload_file(self, project_name):
        file_path = filedialog.askopenfilename(title="เลือกไฟล์")
        if not file_path:
            return
        path = os.path.join(self.parent_folder, project_name)
        os.makedirs(path, exist_ok=True)
        shutil.copy(file_path, path)
        print(f"✅ อัปโหลดไฟล์ {file_path} ไปยัง {path}")

    def list_files(self, project_name):
        path = os.path.join(self.parent_folder, project_name)
        if os.path.exists(path):
            files = os.listdir(path)
            print(f"📂 ไฟล์ใน {project_name}: {files}")
            return files
        else:
            print("❌ ไม่มีโฟลเดอร์นี้")
            return []

    def delete_file(self, project_name, filename):
        path = os.path.join(self.parent_folder, project_name, filename)
        if os.path.exists(path):
            os.remove(path)
            print(f"🗑️ ลบไฟล์ {filename} สำเร็จ")
        else:
            print("❌ ไม่พบไฟล์")

    def delete_project_folder(self, project_name):
        path = os.path.join(self.parent_folder, project_name)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"🗑️ ลบโฟลเดอร์ {project_name} สำเร็จ")
        else:
            print("❌ ไม่พบโฟลเดอร์")


# ==============================
# Main Program
# ==============================
def main():
    db = Database()
    file_manager = ProjectFileManager()

    while True:
        action = input(
            "\n--- เมนูหลัก ---\n"
            "[1] เพิ่มข้อมูลนักศึกษา\n"
            "[2] เพิ่มโครงการใหม่\n"
            "[3] อัปโหลดไฟล์\n"
            "[4] เรียกดูไฟล์โครงการ\n"
            "[5] ยกเลิก\n"
            "เลือกเมนู: "
        )

        if action == '1':
            name = input("ชื่อ: ")
            sid = input("รหัสนักศึกษา: ")
            email = input("อีเมล: ")

            s = Student(db, name, sid, email)
            if s.exists():
                print("❌ รหัสนักศึกษานี้มีอยู่แล้ว")
                continue
            if s.email_exists():
                print("❌ Email นี้มีอยู่แล้ว")
                continue
            s.save()

        elif action == '2':
            sid = input("รหัสนักศึกษาเจ้าของโครงการ: ")
            db.c.execute("SELECT Student_name FROM Student WHERE Student_id=?", (sid,))
            result = db.c.fetchone()
            if not result:
                print("❌ ไม่พบนักศึกษา")
                continue
            owner = result[0]

            pname = input("ชื่อโครงการ: ")
            desc = input("รายละเอียด: ")
            year = input("ปีการศึกษา: ")

            p = Project(db, pname, desc, year, sid, owner)
            if p.exists():
                print("❌ โครงการนี้มีอยู่แล้ว")
                continue
            p.save()
            p.create_folder()

        elif action == '3':
            pname = input("ชื่อโครงการ: ")
            file_manager.upload_file(pname)

        elif action == '4':
            pname = input("ชื่อโครงการ: ")
            file_manager.list_files(pname)

        elif action == '5':
            print("👋 ออกจากโปรแกรม")
            break

        else:
            print("❌ เลือกเมนูไม่ถูกต้อง")


if __name__ == "__main__":
    main()
