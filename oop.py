from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, ttk
import shutil
import os
import sqlite3
from datetime import datetime
import re
# PATH = os.getcwd()
class Database:
    def __init__(self, db_name="Data.sqlite3"):
        self.conn = sqlite3.connect(db_name) #สร้างฐานข้อมูล
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.c = self.conn.cursor()
        self.create_tables()

        #สร้างตาราง Student ในฐานข้อมูล
    def create_tables(self):
        self.c.execute("""                        
            CREATE TABLE IF NOT EXISTS Student (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Student_name TEXT UNIQUE,
                Student_id INTEGER UNIQUE,
                Email TEXT UNIQUE
            )
        """)
        #สร้างตาราง Project ในฐานข้อมูล
        self.c.execute("""
                CREATE TABLE IF NOT EXISTS Project (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Project_name TEXT UNIQUE,
                    Description TEXT,
                    Owner TEXT,
                    Student_id INTEGER,
                    Year REAL,
                    FOREIGN KEY(Student_id) REFERENCES Student(Student_id)
                )
        """)
        self.conn.commit()

 #เก็บข้อมูลนักศึกษาและส่งไปบันทึกในฐานข้อมูล
class Student: 
    # def __init__(self,student_name = None,student_id = None,student_email = None):
    def __init__(self,db, student_name=None, student_id=None, student_email=None,**kwargs):
        self.db = db
        self.student_name = student_name
        self.student_id = student_id
        self.student_email = student_email

    #Method รับข้อมูลนักศึกษาและบันทึกลงฐานข้อมูล
    def New_Student(self):
        try:
            with self.db.conn:
                #  เพิ่มข้อมูลนักศึกษาในตาราง Student
                command1 = '''
                    INSERT INTO Student (Student_name, Student_id, Email) VALUES (?,?,?)
                '''
                self.db.c.execute(command1, (self.student_name, self.student_id, self.student_email))
            self.db.conn.commit()
            print(f"สร้างเพิ่มข้อมูลนักศึกษาของ {self.student_name} เสร็จสิ้น")

        except sqlite3.IntegrityError as e:
            print("เกิดข้อผิดพลาด: ", e)

    #ตรวจสอบรูปแบบอีเมล
    def is_valid_email(self):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, self.student_email) is not None
    
    #เช็คอีเมลซ้ำหรือไม่
    def check_email(self):
        with self.db.conn:
            self.db.c.execute("SELECT 1 FROM Student WHERE Email = ?", (self.student_email,))
            return self.db.c.fetchone() is not None
    
    def check_student_id(self):
        with self.db.conn:
            self.db.c.execute("SELECT 1 FROM Student WHERE Student_id = ?", (self.student_id,))
            return self.db.c.fetchone() is not None


 #เก็บข้อมูลโครงการและส่งไปบันทึกในฐานข้อมูล
class Project(Student): 
    def __init__(self,db, project_name=None, description=None, year=None,student_id=None, student_name=None, **kwargs):
        super().__init__(db,student_name, student_id, **kwargs)
        self.project_name = project_name
        self.description = description
        self.year = year
        self.db = db

    #Method รับข้อมูลโครงการและบันทึกลงฐานข้อมูล
    def New_Project(self):
        try:
            with self.db.conn:
                #เพิ่มข้อมูลโปรเจกต์ พร้อมเชื่อมกับ student_id และ owner
                command = '''
                    INSERT INTO Project (Project_name, Description, Year, Owner, Student_id) VALUES (?,?,?,?,?)
                '''
                self.db.c.execute(command, (self.project_name, self.description, self.year, self.student_name, self.student_id))

            self.db.conn.commit()
            print(f"สร้างโครงการ {self.project_name} เสร็จสิ้น")
        except sqlite3.IntegrityError as e:
            print("เกิดข้อผิดพลาด: ", e)

    def check_Project_name(self):
        with self.db.conn:
            self.db.c.execute("SELECT 1 FROM Project WHERE Project_name = ?", (self.project_name,))
            return self.db.c.fetchone() is not None

    #สร้างโฟลเดอร์ของโครงการหลังสร้างโครงการใหม่
    def create_project(self, parent_folder="Project_list"):
        if parent_folder:
            path = os.path.join(parent_folder, self.project_name)
        else:
            path = self.project_name
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"สร้างโฟลเดอร์สำหรับ {self.project_name} แล้ว.")
        else:
            print(f"มี '{self.project_name}' อยู่แล้ว.")

    

#ติดต่อฐานข้อมูล
class Database_manager(Database): 
    def __init__(self):
        super().__init__()

    def fetch_Students(self):
        # self.c.execute("SELECT * FROM Project")
        self.c.execute("""SELECT Student.Student_name, Student.Student_id, Student.Email, Student.ID
            FROM Student
        """)
        # print(self.c.fetchall())
        # return self.c.fetchall()
        results = self.c.fetchall()
        if results:
            for student_name, student_id, email ,ID in results:
                print("-" * 100)
                print(f"ID: {ID}, ชื่อ: {student_name}, รหัสนักศึกษา: {student_id}, Email: {email}")
    
    # ดึงข้อมูลโปรเจกต์ทั้งหมด
    def fetch_Projects(self):
        # self.c.execute("SELECT * FROM Project")
        self.c.execute("""SELECT Student.Student_name, Student.Student_id, Student.Email, Project.Project_name, Project.Year, Project.ID
            FROM Project
            JOIN Student ON Project.Student_id = Student.Student_id
        """)

        results = self.c.fetchall()
        if results:
            for student_name, student_id, email, project_name, year, ID in results:
                print("-" * 100)
                print(f"ID: {ID}, ชื่อโครงการ: {project_name}, เจ้าของโครงการ: {student_name}, รหัสนักศึกษา: {student_id}, Email: {email}, ปี: {year}")

    #ค้นหาข้อมูลโครงการ
    def search_project(self, Keyword): 
        self.c.execute(
            """
            SELECT Student.Student_name, Student.Student_id, Student.Email, Project.Project_name, Project.Year
            FROM Project
            LEFT JOIN Student ON Project.Student_id = Student.Student_id
            WHERE Project.Project_name LIKE ? OR Student.Student_id LIKE ?
            """,
            ('%' + Keyword + '%', '%' + Keyword + '%')
        )
        results = self.c.fetchall()
        if results:
            for student_name, student_id, email, project_name, year in results:
                print(f"เจ้าของโครงการ: {student_name}")
                print(f"รหัสนักศึกษา: {student_id}")
                print(f"Email: {email}")
                print(f"ชื่อโครงการ: {project_name}")
                print(f"ปี: {year}")
                print("-" * 40)
        else:
            print(f"ไม่พบข้อมูลของโครงการ {Keyword}")

    #เรียกดูไฟล์ของโครงการที่ต้องการ
    def open_project_file(self, project_name,parent_folder="Project_list"):
        if parent_folder:
            path = os.path.join(parent_folder, project_name)
        else:
            path = project_name
        if os.path.exists(path):
            os.startfile(path)
            print(f"เปิดไฟล์ของโครงการ {project_name}")
        else:
            print(f"ไม่พบไฟล์ของโครงการ {project_name}")
        
    def get_studentinfo_by_id(self, student_id):
        self.c.execute("SELECT Student_name FROM Student WHERE Student_id=?", (student_id,))
        result = self.c.fetchall()  # คืนค่า Student_name หรือ None ถ้าไม่เจอ
        if result:  
            return result[0][0] # เอาแค่แถวแรก, คอลัมน์แรก
    def get_Projectinfo_by_id(self, project_id):
        self.c.execute("SELECT Project_name FROM Project WHERE ID=?", (project_id,))
        result = self.c.fetchall()  # คืนค่า Project_name หรือ None ถ้าไม่เจอ
        if result:  
            return result[0][0]

#classของ adminไว้แก้ไขข้อมูลใน database
class Admin(Database): 
    def __init__(self,pin = "1111"): #กำหนด pin คือ 1111
        super().__init__()
        self.__pin = pin

    #ตรวจสอบpin 
    def check_pin(self,input_pin):
        if input_pin == self.__pin:
            print("รหัสถูก")
            return True
        
    #อัพเดตข้อมูลโครงการในฐานข้อมูล
    def update_Project_Data(self,project_name,description,year,ID): #ฟังชัน อัปเดตข้อมูลในตาราง Project
        with self.conn:
            command = 'UPDATE Project SET Project_name = ?, Description = ?, Year = ? WHERE ID = ?'
            self.c.execute(command,(project_name,description,year,ID))
        self.conn.commit()

    #อัพเดตข้อมูลนักศึกษาในฐานข้อมูล
    def update_Student_Data(self,new_student_name,new_student_id,new_student_email,ID): #ฟังชัน อัปเดตข้อมูลในตาราง Student
        with self.conn:
            command = 'UPDATE Student SET Student_name = ?, Student_id = ?, Email = ? WHERE ID = ?'
            self.c.execute(command,(new_student_name,new_student_id,new_student_email,ID))
        self.conn.commit()

    #ลบข้อมูลโครงการออกจากฐานข้อมูล
    def Delete_Project_data (self, ID):
        with self.conn:
            command = 'DELETE FROM Project WHERE ID=(?)'
            self.c.execute(command,([ID]))
        self.conn.commit()

    #ลบข้อมูลนักศึกษาออกจากฐานข้อมูล
    def Delete_Student_data (self, ID):
        with self.conn:
            command = 'DELETE FROM Student WHERE ID=(?)'
            self.c.execute(command,([ID]))
        self.conn.commit()
        print("ลบข้อมูลนักศึกษาเรียบร้อยแล้ว")
    
#ไว้อัพโหลดไฟล์ต่างๆ
class UploadFile:
    def __init__(self,Project_name):

        #กำหนดรูปแบบของ GUI
        self.root = tk.Tk()
        self.root.title("Upload File")
        self.root.geometry("350x200")
        self.label = ttk.Label(self.root, text="ยังไม่ได้เลือกไฟล์")
        self.label.pack(pady=10)
        self.btn_upload = ttk.Button(self.root, text="เลือกไฟล์", command=lambda : self.upload_file(Project_name))
        self.btn_upload.pack(pady=10)
        self.root.mainloop()

    #อัปโหลดไฟล์
    def upload_file(self, Project_name, parent_folder="Project_list"):
        # เปิด dialog ให้เลือกไฟล์
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์",
            filetypes=(("All files", "*.*"), ("Text files", "*.txt"))
        )

        if not file_path:
            return  # ผู้ใช้กดยกเลิก
        path = os.path.join(parent_folder, Project_name)
        PATH = os.getcwd()

        os.makedirs(path, exist_ok=True)
        shutil.copy(file_path, path)

        self.label.config(text=f"อัปโหลดไฟล์: {os.path.basename(file_path)} เสร็จสิ้น")
        print(f"ไฟล์ {os.path.basename(file_path)} ถูกอัปโหลดไปที่ {PATH}/{path}")

class ProjectFileManager:
    def __init__(self, parent_folder="Project_list"):
        self.parent_folder = parent_folder

    def delete_project_folder(self, project_name):
        path = os.path.join(self.parent_folder, project_name)
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
            print(f"ลบโฟลเดอร์ {project_name} เรียบร้อยแล้ว")
        else:
            print(f"ไม่พบโฟลเดอร์ของโครงการ {project_name}")

    def delete_file_in_project(self, project_name, filename):
        file_path = os.path.join(self.parent_folder, project_name, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            print(f"ลบไฟล์ {filename} ในโครงการ {project_name} เรียบร้อยแล้ว")
        else:
            print(f"ไม่พบไฟล์ {filename} ในโครงการ {project_name}")

    def list_files_in_project(self, project_name):
        folder_path = os.path.join(self.parent_folder, project_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            files = os.listdir(folder_path)
            if files:
                print(f"ไฟล์ทั้งหมดในโครงการ {project_name}:")
                for f in files:
                    print(" -", f)
                return files
            else:
                print(f"โครงการ {project_name} ยังไม่มีไฟล์")
                return []
        else:
            print(f"ไม่พบโฟลเดอร์ของโครงการ {project_name}")
            return None


#เรียกใช้งาน
def main():
    db = Database()
    while True:
         #สร้างฐานข้อมูล
        action = input(
            "---------------------------------------- \n"
            "ระบบจัดเก็บไฟล์โครงการของนักศึกษา \n"            
            "[1] เพิ่มข้อมูลนักศึกษา \n"   #(ชื่อ รหัสนักศึกษา )
            "[2] เพิ่มโครงการใหม่ \n"                  #( [ ลงในที่สร้างจาก 1 ] ใส่แค่ชื่อโปคเจค รายะเอียด ปี)
            "[3] จัดการไฟล์ \n"                         #(เลือกโครงการที่สร้างจาก 2 แล้วเพิ่มไฟล์เข้าไป)                         
            "[4] แก้ไขข้อมูล \n"                          
            "[5] ค้นหาข้อมูลโครงการ \n"            #(แสดงชื่อโครงการ ชื่อเจ้าของโครงการ รหัสนักศึกษา Email ปี)
            "[6] เรียกดูไฟล์โครงการ\n"
            "[7] ตัวเลือกแอดมิน \n"
            "[8] ยกเลิก \n"
            "---------------------------------------- \n"
            "เลือกรายการที่ต้องการ: "
            )

        if not action.isdigit() or int(action) not in range(1, 9):
            print("เกิดข้อผิดพลาด: กรุณาเลือกรายการให้ถูกต้อง")
            continue

        if action == '1':
            print("-"*40)
            # NewStudent = Student()
            StudentData = Database_manager()

            input_name = input("Enter Student Name: ")
            input_student_id = input("Enter Student ID: ")
            input_email = input("Enter Student Email: ")
            NewStudent = Student(db,input_name, input_student_id, input_email)
            if NewStudent.check_student_id():
                print("รหัสนักศึกษานี้มีอยู่แล้ว")
                continue
            if not NewStudent.is_valid_email():
                print("รูปแบบอีเมลไม่ถูกต้อง")
                continue
            if NewStudent.check_email():
                print("Email นี้มีอยู่แล้ว")
                continue
            NewStudent.New_Student()
            StudentData.fetch_Students()

        elif action == '2':
            while True:
                print("-"*40)
                # NewProject = Project()
                ProjectData = Database_manager()
                # check = Student(db)

                input_student_id2 = input("Enter Student ID: ")
                student_info = ProjectData.get_studentinfo_by_id(input_student_id2)
                if not student_info:
                    print("❌ ไม่พบนักศึกษาที่มีรหัสนี้")
                    continue

                input_student_name = student_info
                input_project_name = input("Enter Project Name: ")
                input_description = input("Enter Project Description: ")
                input_year = input("Enter Academic Year: ")
                NewProject = Project(db,input_project_name, input_description, input_year,input_student_id2,input_student_name)

                check_student = Student(db, student_id=input_student_id2)
                if not check_student.check_student_id():
                    print("ไม่พบรหัสนักศึกษานี้ในระบบ กรุณาเพิ่มข้อมูลนักศึกษาก่อน")
                    continue
                
                if NewProject.check_Project_name():
                    print("Project นี้มีอยู่แล้ว")
                    continue


                NewProject.New_Project()
                NewProject.create_project()
                ProjectData.fetch_Projects()
                break

        elif action == '3':
            while True:
                show_Projects_info = Database_manager()
                CheckProject = Project()
                ManageFile = ProjectFileManager()

                managefile_action = input(
                    "---------------------------------------- \n"
                    "เลือกรายการที่ต้องการ \n"
                    "[1] อัปโหลดไฟล์ \n"
                    "[2] ลบไฟล์ในโฟลเดอร์ \n"
                    "[3] ออก \n"
                    "---------------------------------------- \n"
                    "เลือกรายการที่ต้องการ: "
                )
                if not managefile_action.isdigit() or int(managefile_action) not in range(1, 5):
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
                        continue
                
                if managefile_action == '1': 
                    show_Projects_info.fetch_Projects()
                    input_upload_Project_name = input("Enter Project Name to upload file: ")
                    if not CheckProject.check_Project_name(input_upload_Project_name):
                        print(f"ไม่พบโครงการ {input_upload_Project_name} ในระบบ")
                        continue
                    UploadFile(input_upload_Project_name)
                elif managefile_action == '2':
                    show_Projects_info.fetch_Projects()
                    input_project_name = input("Enter Project Name to Delete files: ")
                    ManageFile.list_files_in_project(input_project_name)
                    input_filename = input("Enter filename to delete: ")
                    ManageFile.delete_file_in_project(input_project_name,input_filename)
            

                
                elif managefile_action == '3':
                        print("ออกจาก [ จัดการไฟล์ ]")
                        break

        elif action == '4':
            while True:
                    
                    edit_action = input(
                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการแก้ไข \n"
                        "[1] แก้ไขข้อมูลนักศึกษา \n"
                        "[2] แก้ไขข้อมูลโครงการ \n"
                        "[3] ลบไฟล์ในโฟลเดอร์ \n"
                        "[4] ออก \n"

                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการ: "
                    )
                    if not edit_action.isdigit() or int(edit_action) not in range(1, 5):
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
                        continue

                    if edit_action == '1':
                        print("-"*40)
                        admin1 = Database_manager()
                        admin2 = Admin()
                        admin1.fetch_Students()
                        input_id1 = input("Select ID to update: ")
                        new_name = input("Enter new Student Name: ")
                        new_id = input("Enter new Student ID: ")
                        new_email = input("Enter new Student Email: ")
                        admin2.update_Student_Data(new_name, new_id, new_email, input_id1)
                        admin1.fetch_Students()
                        print("อัปเดตข้อมูลนักศึกษาเรียบร้อยแล้ว")
                        print("-"*40)

                    elif edit_action == '2':
                        print("-"*40)
                        admin1 = Database_manager()
                        admin2 = Admin()
                        admin1.fetch_Projects()
                        input_id2 = input("Enter Project ID to update: ")
                        input_new_project_name = input("Enter new Project Name: ")
                        input_new_description = input("Enter new Description: ")
                        input_new_year = input("Enter new Year: ")
                        admin2.update_Project_Data(input_new_project_name, input_new_description, input_new_year, input_id2)
                        admin1.fetch_Projects()
                        print("อัปเดตข้อมูลโครงการเรียบร้อยแล้ว")
                        print("-"*40)

                    elif edit_action == '3':
                        print("asd")

                    elif edit_action == '4':
                        print("ออกจากโหมดแอดมิน")
                        break

        elif action == '5':
            print("-"*40)
            input_keyword = input("ใส่ชื่อโครงการ หรือ รหัสนักศึกษา  : ")
            Search = Database_manager()
            Search.search_project(input_keyword)

        elif action == '6':
            print("-"*40)
            Search = Database_manager()
            Search.fetch_Projects()
            input_open_Project_name = input("ใส่ชื่อโครงการที่ต้องการดูไฟล์: ")
            Search.open_project_file(input_open_Project_name)

        elif action == '7':
            input_PIN = input("Enter Admin PIN: ")
            admin = Admin()
            if admin.check_pin(input_PIN):
                while True:
                    admin1 = Database_manager()
                    admin2 = Admin()
                    admin3 = ProjectFileManager()
                    admin_action = input(
                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการแก้ไข \n"
                        "[1] ลบข้อมูลนักศึกษา \n"
                        "[2] ลบข้อมูลโครงการ \n"
                        "[3] ออก \n"
                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการ: "
                    )
                    if not admin_action.isdigit() or int(admin_action) not in range(1, 4):
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
                        continue

                    elif admin_action == '1':
                        print("-"*40)
                        # admin1 = Database_manager()
                        # admin2 = Admin()
                        admin1.fetch_Students()
                        input_id3 = input("Select ID to Delete: ")
                        admin2.Delete_Student_data(input_id3)
                        admin1.fetch_Students()
                        print("-"*40)

                    elif admin_action == '2':
                        print("-"*40)
                        # admin1 = Database_manager()
                        # admin2 = Admin()
                        admin1.fetch_Projects()
                        input_id4 = input("Select ID to Delete: ")
                        delete_project_name = admin1.get_Projectinfo_by_id(input_id4)
                        # delete_project_name = project_info
                        admin2.Delete_Project_data(input_id4)
                        admin3.delete_project_folder(delete_project_name)
                        admin1.fetch_Projects()
                        print(f"ลบข้อมูลกับโฟลเดอร์ของโครงการ {delete_project_name} เรียบร้อยแล้ว")



                        print("-"*40)

                    elif admin_action == '3':
                        print("ออกจากโหมดแอดมิน")
                        break

                    # else:
                    #     print("Error: กรุณาเลือกรายการให้ถูกต้อง")
            else:
                print("รหัสผ่านไม่ถูกต้อง")
                continue

        elif action == '8':

            print("-"*40)
            print("จบการทำงาน")
            break

        # else:
        #     print("เกิดข้อผิดพลาด กรุณาลองใหม่")


if __name__ == "__main__":
    # test = Uploadfile()
    # test = Uploadfile.upload_file
    main()
    # ken1 = Student()
    # # ken1.New_Student(";kasmk",54543,"asdadsaad@gmail.com")
    # ken2 = Project()
    # ken2.New_Project("OsdaMG", "LOLLL2L", 20233)
    # test = Database_manager()
    # # test.fetch_Students()
    # test.fetch_Projects()

 