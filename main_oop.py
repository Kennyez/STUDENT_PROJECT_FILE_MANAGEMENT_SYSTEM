from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, ttk, Tk
import shutil
import os
import sqlite3
import re
from send2trash import send2trash # py -m pip install send2trash
from PIL import Image, ImageTk # py -m pip install Pillow
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
                Student_name TEXT ,
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
                    Year INTEGER,
                    FOREIGN KEY(Student_id) REFERENCES Student(Student_id) ON UPDATE CASCADE
                )
        """)
        self.conn.commit()

 #เก็บข้อมูลนักศึกษาและส่งไปบันทึกในฐานข้อมูล
class Student: 
    def __init__(self,db, student_name, student_id, student_email):
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
            self.db.c.execute("SELECT 1 FROM Student WHERE Student_id LIKE ?", (self.student_id,))
            return self.db.c.fetchone() is not None


 #เก็บข้อมูลโครงการและส่งไปบันทึกในฐานข้อมูล
class Project(Student): 
    def __init__(self,db, project_name, description, year,student: Student): #composition
        self.db = db
        self.project_name = project_name
        self.description = description
        self.year = year
        self.student = student

    #Method รับข้อมูลโครงการและบันทึกลงฐานข้อมูล
    def New_Project(self):
        try:
            with self.db.conn:
                #เพิ่มข้อมูลโปรเจกต์ พร้อมเชื่อมกับ student_id และ owner
                command = '''
                    INSERT INTO Project (Project_name, Description, Year, Owner, Student_id) VALUES (?,?,?,?,?)
                '''
                self.db.c.execute(command, (self.project_name, self.description, self.year, self.student.student_name, self.student.student_id))

            self.db.conn.commit()
            print(f"สร้างโครงการ {self.project_name} เสร็จสิ้น")
        except sqlite3.IntegrityError as e:
            print("เกิดข้อผิดพลาด: ", e)

    def check_Project_name(self):
        with self.db.conn:
            self.db.c.execute("SELECT 1 FROM Project WHERE Project_name = ?", (self.project_name,))
            return self.db.c.fetchone() is not None

    def create_project(self, parent_folder="Project_list"):
        """สร้างโฟลเดอร์โปรเจคแยกตามรหัสนักศึกษา"""
        if parent_folder:
            # สร้างโครงสร้าง: Project_list/Student_ID/Project_name
            student_folder = os.path.join(parent_folder, str(self.student.student_id))
            project_path = os.path.join(student_folder, self.project_name)
        else:
            student_folder = str(self.student.student_id)
            project_path = os.path.join(student_folder, self.project_name)
        
        # สร้างโฟลเดอร์รหัสนักศึกษาก่อนถ้ายังไม่มี
        if not os.path.exists(student_folder):
            os.makedirs(student_folder)
            print(f"สร้างโฟลเดอร์สำหรับนักศึกษา {self.student.student_id} แล้ว")
        
        # สร้างโฟลเดอร์โปรเจค
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            print(f"สร้างโฟลเดอร์โปรเจค '{self.project_name}' ในโฟลเดอร์ของนักศึกษา {self.student.student_id} แล้ว")
        else:
            print(f"มีโฟลเดอร์โปรเจค '{self.project_name}' อยู่แล้ว")

#ติดต่อฐานข้อมูล
class Database_manager(Database): 
    def __init__(self):
        super().__init__()

    def fetch_AllStudents(self):
        self.c.execute("""SELECT Student.Student_name, Student.Student_id, Student.Email, Student.ID
            FROM Student
        """)
        results = self.c.fetchall()
        if results:
            for student_name, student_id, email ,ID in results:
                print("-" * 100)
                print(f"ID: {ID}, ชื่อ: {student_name}, รหัสนักศึกษา: {student_id}, Email: {email}")

    def fetch_OneStudent(self, student_id):
        self.c.execute("""SELECT Student.Student_name, Student.Student_id, Student.Email
            FROM Student WHERE Student.Student_id LIKE ?
        """, ('%' +student_id,))
        result = self.c.fetchall()
        if result:
            print("-" * 40)
            print(f"ชื่อ: {result[0][0]}, รหัสนักศึกษา: {result[0][1]}, Email: {result[0][2]}")
            
    # ดึงข้อมูลโปรเจกต์ทั้งหมด
    def fetch_AllProjects(self):
        self.c.execute("""SELECT Student.Student_name, Student.Student_id, Student.Email, Project.Project_name, Project.Year, Project.ID, Project.Description
            FROM Project
            JOIN Student ON Project.Student_id = Student.Student_id
        """)

        results = self.c.fetchall()
        if results:
            for student_name, student_id, email, project_name, year, ID , description in results:
                print("-" * 100)
                print(f"ID: {ID}, ชื่อโครงการ: {project_name}, รายละเอียด: {description}, เจ้าของโครงการ: {student_name}, รหัสนักศึกษา: {student_id}, Email: {email}, ปีการศึกษา: {year}")

    #ค้นหาข้อมูลโครงการ
    def search_project(self, Keyword): 
        self.c.execute(
            """
            SELECT Student.Student_name, Student.Student_id, Student.Email, Project.Project_name, Project.Year, Project.Description
            FROM Project
            LEFT JOIN Student ON Project.Student_id = Student.Student_id
            WHERE Project.Project_name LIKE ? OR Student.Student_id LIKE ?
            """,
            ('%' + Keyword + '%', '%' + Keyword + '%')
        )
        results = self.c.fetchall()
        if results:
            for student_name, student_id, email, project_name, year, description in results:
                print("-" * 40)
                print(f"ชื่อโครงการ: {project_name}")
                print(f"รายละเอียด: {description}")
                print(f"เจ้าของโครงการ: {student_name}")
                print(f"รหัสนักศึกษา: {student_id}")
                print(f"Email: {email}")
                print(f"ปีการศึกษา: {year}")
        else:
            print(f"ไม่พบข้อมูลของโครงการ {Keyword}")

    #เรียกดูไฟล์ของโครงการที่ต้องการ
    def open_project_file(self, project_name, student_id, parent_folder="Project_list"):
        """เปิดไฟล์โปรเจค (รองรับโครงสร้างใหม่)"""
        path = os.path.join(parent_folder, str(student_id), project_name)
        
        if os.path.exists(path):
            os.startfile(path)
            print(f"เปิดไฟล์ของโปรเจค {project_name}")
        else:
            print(f"ไม่พบไฟล์ของโปรเจค {project_name} ของนักศึกษา {student_id}")
        
    def get_studentname_by_id(self, student_id):
        self.c.execute("SELECT Student_name FROM Student WHERE Student_id=?", (student_id,))
        result = self.c.fetchall()  # คืนค่า Student_name หรือ None ถ้าไม่เจอ
        if result:  
            return result[0][0] # เอาแค่แถวแรก, คอลัมน์แรก
        
    def get_Projectinfo_by_id(self, project_id):
        self.c.execute("SELECT Project_name FROM Project WHERE ID=?", (project_id,))
        result = self.c.fetchall()  # คืนค่า Project_name หรือ None ถ้าไม่เจอ
        if result:  
            return result[0][0]
        
    def get_all_Project_by_sid(self, student_id):
        self.c.execute(
            """
            SELECT Project.Project_name
            FROM Project
            LEFT JOIN Student ON Project.Student_id = Student.Student_id
            WHERE Student.Student_id LIKE ?
            """,
            ('%' + student_id + '%',)
        )
        list_pf = self.c.fetchall()
    
    # เช็คว่ามีข้อมูลไหม
        if not list_pf:
            print(f"ไม่พบข้อมูลของโครงการ {student_id}")
            return None
        
        # แสดงรายการ
        for i, pj_name in enumerate(list_pf, start=1): #ได้ทั้ง index และ value ใน loop เดียว
            print(f"[{i}]โครงการ: {pj_name[0]}")
        while True:
            #เลือกโปรที่ต้องการ
            try:
                choice = int(input("เลือกหมายเลขโครงการที่ต้องอัปโหลด: "))
                if choice < 1:
                    print("หมายเลขต้องไม่น้อยกว่า 1")
                    continue
                
                if choice > len(list_pf):
                    print(f"หมายเลขต้องไม่เกิน {len(list_pf)}")
                    continue
                
                # ถ้าผ่านทุกเงื่อนไข
                selected_project = list_pf[choice - 1][0]
                return selected_project
            except ValueError:
                print("กรุณาใส่ตัวเลขเท่านั้น")
                return None
    
    def check_last_4_ID(self,Keyword):
        self.c.execute("SELECT Student_id FROM Student WHERE Student.Student_id LIKE ?",('%' + Keyword ,))
        return  self.c.fetchall()
    
    #ดึง student_id จากชื่อโปรเจค
    def get_student_id_by_project_name(self, project_name):
        self.c.execute("SELECT Student_id FROM Project WHERE Project_name = ?", (project_name,))
        result = self.c.fetchone()
        if result:
            return result[0]
        return None

class Admin(): 
    def __init__(self, db, pin = "1111",**kwargs): #กำหนด pin คือ 1111
        super().__init__(**kwargs)
        self.db = db
        self.__pin = pin

    #ตรวจสอบpin 
    def check_pin(self,input_pin):
        if input_pin == self.__pin:
            print("รหัสถูก")
            return True
        
    #อัพเดตข้อมูลโครงการในฐานข้อมูล
    def update_Project_Data(self,project_name,description,year,pjname): 
        with self.db.conn:
            command = 'UPDATE Project SET Project_name = ?, Description = ?, Year = ? WHERE Project_name = ?'
            self.db.c.execute(command,(project_name,description,year,pjname))
        self.db.conn.commit()

    #อัพเดตข้อมูลนักศึกษาในฐานข้อมูล
    def update_Student_Data(self,new_student_name,new_student_id,new_student_email, old_student_id):
        with self.db.conn:
            command = ('UPDATE Student SET Student_name = ?, Student_id = ?, Email = ? WHERE Student_id LIKE ?')
            cursor = self.db.c.execute(command,(new_student_name, new_student_id, new_student_email, old_student_id))
        self.db.conn.commit()
        if cursor.rowcount == 0:
            print(f"ไม่พบรหัสนักศึกษา {old_student_id} ที่ต้องการอัปเดต")
        else:
            print(f"อัปเดตข้อมูลนักศึกษา {new_student_name} เรียบร้อย")

    #ลบข้อมูลโครงการออกจากฐานข้อมูล
    def Delete_Project_data (self, ID):
        with self.db.conn:
            command = 'DELETE FROM Project WHERE ID=(?)'
            self.db.c.execute(command,([ID]))
        self.db.conn.commit()

    #ลบข้อมูลนักศึกษาออกจากฐานข้อมูล
    def Delete_Student_data (self, ID):
        with self.db.conn:
            command = 'DELETE FROM Student WHERE ID=(?)'
            self.db.c.execute(command,([ID]))
        self.db.conn.commit()
        print("ลบข้อมูลนักศึกษาเรียบร้อยแล้ว")
    
class UploadFile:
    def __init__(self, project_name, student_id, parent_folder="Project_list"):
        self.project_name = project_name
        self.student_id = student_id
        self.parent_folder = parent_folder
        self.root = tk.Tk()
        self.root.title("Upload File")
        self.root.geometry("350x200")
        try:
            PATH = os.getcwd()  # หรือเส้นทางที่คุณใช้
            icon_path = os.path.join(PATH, 'fupload.ico')
            self.root.iconbitmap(icon_path)
        except:
            pass
        try:
            PATH = os.getcwd()
            bg_path = os.path.join(PATH, 'background.jpg')  # หรือ .png
            bg_image = Image.open(bg_path)
            bg_image = bg_image.resize((350, 200))  # ปรับขนาดให้เท่ากับหน้าต่าง
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            # สร้าง Canvas สำหรับพื้นหลัง
            self.canvas = tk.Canvas(self.root, width=350, height=200)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            
            # ใส่ widget บน canvas
            self.label = tk.Label(self.canvas, text="ยังไม่ได้เลือกไฟล์", 
                                bg="lightblue", font=("Arial", 10))
            self.canvas.create_window(175, 70, window=self.label)  # ตรงกลาง
            
            self.btn_upload = tk.Button(self.canvas, text="เลือกไฟล์", 
                                      command=self.upload_file,
                                      bg="lightblue", font=("Arial", 10))
            self.canvas.create_window(175, 130, window=self.btn_upload)
            
        except Exception as e:
                print(f"ไม่สามารถโหลดพื้นหลังได้: {e}")
                # ใช้ GUI ธรรมดาแทน
                self.label = ttk.Label(self.root, text="ยังไม่ได้เลือกไฟล์")
                self.label.pack(pady=20)
                self.btn_upload = ttk.Button(self.root, text="เลือกไฟล์", command=self.upload_file)
                self.btn_upload.pack(pady=20)
        # self.label = ttk.Label(self.root, text="ยังไม่ได้เลือกไฟล์")
        # self.label.pack(pady=20)
        # self.btn_upload = ttk.Button(self.root, text="เลือกไฟล์", command=self.upload_file)
        # self.btn_upload.pack(pady=20)
        self.root.mainloop()
        


    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์",
            filetypes=(("All files", "*.*"), ("Text files", "*.txt"))
        )
        if not file_path:
            return
        
        path = os.path.join(os.getcwd(), self.parent_folder, str(self.student_id), self.project_name)
        os.makedirs(path, exist_ok=True)
        shutil.copy(file_path, path)
        self.label.config(text=f"อัปโหลดไฟล์: {os.path.basename(file_path)} เสร็จสิ้น")
        print(f"ไฟล์ {os.path.basename(file_path)} ถูกอัปโหลดไปที่ {path}")

#จัดการไฟล์
class ProjectFileManager:
    def __init__(self, project_name, student_id, file_name=None, parent_folder="Project_list"):
        self.project_name = project_name
        self.student_id = student_id
        self.file_name = file_name
        self.parent_folder = parent_folder

    def delete_project_folder(self):
        """ลบโฟลเดอร์โปรเจค (รองรับโครงสร้างใหม่)"""
        path = os.path.join(self.parent_folder, str(self.student_id), self.project_name)
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
            print(f"ลบโฟลเดอร์โปรเจค {self.project_name} ของนักศึกษา {self.student_id} เรียบร้อยแล้ว")
        else:
            print(f"ไม่พบโฟลเดอร์ของโปรเจค {self.project_name}")

    def delete_file_in_project(self):
        files = self.list_files_in_project()
        if not files:
            return

        try:
            choice = int(input("เลือกหมายเลขไฟล์ที่ต้องการลบ: "))
            if 1 <= choice <= len(files):
                selected_file = files[choice - 1]
                file_path = os.path.join(self.parent_folder, str(self.student_id), self.project_name, selected_file)
                send2trash(file_path)
                print(f"ลบไฟล์ {selected_file} ในโครงการ {self.project_name} เรียบร้อยแล้ว")
            else:
                print("หมายเลขไฟล์ไม่ถูกต้อง")
        except ValueError:
            print("กรุณาใส่ตัวเลขเท่านั้น")

    def list_files_in_project(self):
        folder_path = os.path.join(self.parent_folder, str(self.student_id), self.project_name)
        
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            files = os.listdir(folder_path)
            if files:
                print(f"ไฟล์ทั้งหมดในโปรเจค {self.project_name}:")
                for i, f in enumerate(files, start=1):
                    print(f"[{i}] {f}")
                return files
            else:
                print(f"โครงการ {self.project_name} ยังไม่มีไฟล์")
                return []
        else:
            print(f"ไม่พบโฟลเดอร์ของโครงการ {self.project_name}")
            return None
    
    def rename_project_folder(self,new_folder_name):
        """เปลี่ยนชื่อโฟลเดอร์โปรเจค (รองรับโครงสร้างใหม่)"""
        current_path = os.path.join(self.parent_folder, str(self.student_id), self.project_name)
        
        # เช็ควว่าโฟลเดอร์มีอยู่จริงหรือไม่
        if not os.path.exists(current_path) or not os.path.isdir(current_path):
            print(f"ไม่พบโฟลเดอร์ของโปรเจค '{self.project_name}' ของนักศึกษา {self.student_id}")
            return False
        
        print(f"ชื่อโฟลเดอร์ปัจจุบัน: {self.project_name}")
        
        # เช็คชื่อที่ไม่ถูกต้อง
        invalid_chars = '<>:"/\\|?*'
        if any(char in new_folder_name for char in invalid_chars):
            print(f"ชื่อโฟลเดอร์ไม่ควรมีตัวอักษรพิเศษ: {invalid_chars}")
            return False
        
        new_path = os.path.join(self.parent_folder, str(self.student_id), new_folder_name)
        
        # เช็ควว่าชื่อโฟลเดอร์ใหม่ซ้ำหรือไม่
        if os.path.exists(new_path):
            print(f"มีโฟลเดอร์ชื่อ '{new_folder_name}' อยู่แล้วในโฟลเดอร์ของนักศึกษา {self.student_id}")
            return False
        
        try:
            # เปลี่ยนชื่อโฟลเดอร์
            os.rename(current_path, new_path)
            print(f"เปลี่ยนชื่อโฟลเดอร์จาก '{self.project_name}' เป็น '{new_folder_name}' เรียบร้อยแล้ว")
            
            # อัปเดตชื่อใน object
            self.project_name = new_folder_name
            return True
            
        except OSError as e:
            print(f"ไม่สามารถเปลี่ยนชื่อโฟลเดอร์ได้: {e}")
            return False

#เรียกใช้งาน
def main():
    #สร้างฐานข้อมูล
    db = Database()
    dbm = Database_manager()
    while True:
        action = input(
            "---------------------------------------- \n"
            "ระบบจัดเก็บไฟล์โครงการของนักศึกษา \n"            
            "[1] เพิ่มข้อมูลนักศึกษา \n"   
            "[2] เพิ่มโครงการใหม่ \n"                  
            "[3] จัดการไฟล์ \n"                                    
            "[4] แก้ไขข้อมูล \n"                          
            "[5] ค้นหาข้อมูลโครงการ \n"            
            "[6] เรียกดูไฟล์โครงการ\n"
            "[7] ตัวเลือกแอดมิน \n"
            "[8] ยกเลิก \n"
            "---------------------------------------- \n"
            "เลือกรายการที่ต้องการ: "
            ).strip()

        if not action.isdigit() or int(action) not in range(1, 9):
            print("เกิดข้อผิดพลาด: กรุณาเลือกรายการให้ถูกต้อง")
            continue

        if action == '1':
            while True:
                print("-"*40)
                input_name = input("ใส่ชื่อ-นามสกุล: ").strip()
                if input_name == "":
                    print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                    continue

                input_student_id = input("ใส่รหัสนักศึกษา 13 หลัก: ").strip()
                if input_student_id == "":
                    print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                    continue

                if not input_student_id.isdigit() or not len(input_student_id) == 13:
                    print("กรุณาใส่รหัสนักศึกษาให้ครบ 13 หลัก")
                    continue

                input_email = input("ใส่อีเมล: ").strip()
                if input_email == "":
                    print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                    continue

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
                dbm.fetch_AllStudents()
                break

        elif action == '2':
            while True:
                print("-"*40)

                input_student_id2 = input("ใส่รหัสนักศึกษา 13 หลัก หรือ 4 ตัวท้าย: ").strip()
                if input_student_id2 == "":
                    print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                    continue

                if not input_student_id2.isdigit():
                    print("กรุณาใส่รหัสนักศึกษาเป็นตัวเลข")
                    continue

                # เช็คความยาว 4 หลัก หรือ 13 หลัก
                if len(input_student_id2) not in [4, 13]:
                    print("กรุณาใส่รหัสนักศึกษา 13 หลัก หรือ 4 ตัวท้าย")
                    continue

                e = dbm.check_last_4_ID(input_student_id2)
                if e:
                    student_id = e[0][0]
                    get_student_name = dbm.get_studentname_by_id(student_id)
                else:
                    print("ไม่พบนักศึกษาที่มีรหัสนี้")
                    continue

                check_student = Student(db,None,student_id,None)

                if not check_student.check_student_id():
                    print("ไม่พบรหัสนักศึกษานี้ในระบบ กรุณาเพิ่มข้อมูลนักศึกษาก่อน")
                    continue

                input_student_name = get_student_name
                input_project_name = input("ใส่ชื่อโครงการ: ").strip()
                if input_project_name == "":
                    print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                    continue 

                check_project = Project(db,input_project_name,None,None,None )
                check_project.check_Project_name()
                if check_project.check_Project_name(): 
                    print(f"โครงการ {input_project_name} มีอยู่แล้ว")
                    continue

                input_description = input("ใส่รายละเอียดโครงการ: ").strip()
                if input_description == "":
                    print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                    continue 

                input_year = input("ใส่ปีการศึกษา: ").strip()
                if input_year == "":
                    print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                    continue

                student = Student(db, input_student_name, student_id, None) 
                NewProject = Project(db,input_project_name, input_description, input_year, student)
                NewProject.New_Project()
                NewProject.create_project()
                dbm.fetch_AllProjects()
                break

        elif action == '3':
            while True:
                managefile_action = input(
                    "---------------------------------------- \n"
                    "เลือกรายการที่ต้องการ \n"
                    "[1] อัปโหลดไฟล์ \n"
                    "[2] ลบไฟล์ในโฟลเดอร์ \n"
                    "[3] ออก \n"
                    "---------------------------------------- \n"
                    "เลือกรายการที่ต้องการ: "
                ).strip()
                if not managefile_action.isdigit() or int(managefile_action) not in range(1, 4):
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
                        continue
                
                if managefile_action == '1': 
                    input_id_student1 = input("ใส่รหัสนักศึกษา 13 หลัก หรือ 4 ตัวท้าย: ").strip()
                    if input_id_student1 == "":
                        print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                        continue
                    if not input_id_student1.isdigit():
                        print("กรุณาใส่รหัสนักศึกษาเป็นตัวเลข")
                        continue

                    # เช็คความยาว 4 หลัก หรือ 13 หลัก
                    if len(input_id_student1) not in [4, 13]:
                        print("กรุณาใส่รหัสนักศึกษาให้ครบ 13 หลัก หรือ 4 ตัวท้าย")
                        continue
                    pj_namee = dbm.get_all_Project_by_sid(input_id_student1)
                    student_id = dbm.get_student_id_by_project_name(pj_namee)  # ดึง student_id
                    
                    check = Project(db, pj_namee, None, None, None)
                    if not check.check_Project_name():
                        print(f"ไม่พบโปรเจค {pj_namee} ในระบบ")
                        continue
                    
                    UploadFile(pj_namee, student_id)

                elif managefile_action == '2':
                    input_id_student2 = input("กรุณาใส่รหัสนักศึกษา 13 หลัก หรือ 4 ตัวท้าย: ").strip()
                    if input_id_student2 == "":
                        print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                        continue
                    if not input_id_student2.isdigit():
                        print("กรุณาใส่รหัสนักศึกษาเป็นตัวเลข")
                        continue

                    # เช็คความยาว 4 หลัก หรือ 13 หลัก
                    if len(input_id_student2) not in [4, 13]:
                        print("กรุณาใส่รหัสนักศึกษา 13 หลัก หรือ 4 ตัวท้าย")
                        continue
                    pj_namee = dbm.get_all_Project_by_sid(input_id_student2)
                    student_id = dbm.get_student_id_by_project_name(pj_namee)  # ดึง student_id
                    
                    delete = ProjectFileManager(pj_namee, student_id)
                    delete.delete_file_in_project()

                elif managefile_action == '3':
                        print("ออกจาก [ จัดการไฟล์ ]")
                        break

        elif action == '4':
            while True:
                    admin = Admin(db)
                    edit_action = input(
                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการแก้ไข \n"
                        "[1] แก้ไขข้อมูลนักศึกษา \n"
                        "[2] แก้ไขข้อมูลโครงการ \n"
                        "[3] ออก \n"

                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการ: "
                    ).strip()
                    if not edit_action.isdigit() or int(edit_action) not in range(1, 5):
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
                        continue

                    if edit_action == '1':
                        print("-"*40)
                        sid = input("ใส่รหัสนักศึกษา 13 หลัก: ").strip()
                        if sid == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue
                        if not sid.isdigit():
                            print("กรุณาใส่รหัสนักศึกษาเป็นตัวเลข")
                            continue

                        # เช็คความยาว 13 หลัก
                        if len(sid) != 13:
                            print("กรุณาใส่รหัสนักศึกษาให้ครบ 13 หลัก")
                            continue
                        check_sid = Student(db,None,sid,None)

                        if not check_sid.check_student_id() and not dbm.check_last_4_ID(sid):
                            print("ไม่พบรหัสนักศึกษานี้ในระบบ")
                            continue

                        dbm.fetch_OneStudent(sid)
                        new_name = input("ใส่ชื่อ-นามสกุลใหม่: ").strip()
                        if new_name == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue

                        new_id = input("ใส่รหัสนักศึกษาใหม่: ").strip()
                        if new_id == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue

                        new_email = input("ใส่อีเมลนักศึกษาใหม่: ").strip()
                        if new_email == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue

                        new = Student(db,new_name,new_id,new_email)


                        if new.check_student_id():
                            print("รหัสนักศึกษานี้มีอยู่แล้ว")
                            continue
                        if not new.is_valid_email():
                            print("รูปแบบอีเมลไม่ถูกต้อง")
                            continue
                        if new.check_email():
                            print("Email นี้มีอยู่แล้ว")
                            continue

                        admin.update_Student_Data(new_name, new_id, new_email, sid)
                        if admin.update_Student_Data:
                            print("อัปเดตข้อมูลนักศึกษาเรียบร้อยแล้ว")

                    elif edit_action == '2':
                        print("-"*40)
                        sid = input("ใส่รหัสนักศึกษา 13 หลัก หรือ 4 ตัวท้าย: ").strip()
                        if sid == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue
                        if not sid.isdigit():
                            print("กรุณาใส่รหัสนักศึกษาเป็นตัวเลข")
                            continue

                        # เช็คความยาว 4 หลัก หรือ 13 หลัก
                        if len(sid) not in [4, 13]:
                            print("กรุณาใส่รหัสนักศึกษาให้ครบ")
                            continue
                        check_sid = Student(db,None,sid,None)

                        if not check_sid.check_student_id() and not dbm.check_last_4_ID(sid):
                            print("ไม่พบรหัสนักศึกษานี้ในระบบ")
                            continue
                        pj_namee = dbm.get_all_Project_by_sid(sid)
                        student_id = dbm.get_student_id_by_project_name(pj_namee)
                        
                        dbm.search_project(pj_namee)
                        input_new_project_name = input("ใส่ชื่อโครงการใหม่: ").strip()
                        if input_new_project_name == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue

                        input_new_description = input("ใส่รายละเอียดโครงการใหม่: ").strip()
                        if input_new_description == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue

                        input_new_year = input("ใส่ปีการศึกษาใหม่: ").strip()
                        if input_new_year == "":
                            print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                            continue
                        
                        # อัปเดต database
                        admin.update_Project_Data(input_new_project_name, input_new_description, input_new_year, pj_namee)
                        
                        # เปลี่ยนชื่อโฟลเดอร์ด้วย
                        rename = ProjectFileManager(pj_namee, student_id)  # ส่ง student_id ด้วย
                        rename.rename_project_folder(input_new_project_name)
                        
                    elif edit_action == '3':
                        print("ออกจากโหมดแอดมิน")
                        break

        elif action == '5':
            print("-"*40)
            input_keyword = input("ใส่ชื่อโครงการ หรือ รหัสนักศึกษา(13 หลัก หรือ 4 ตัวท้าย)  : ").strip()
            if input_keyword == "":
                print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                continue
            dbm.search_project(input_keyword)

        elif action == '6':
            print("-"*40)
            sid = input("ใส่รหัสนักศึกษา 13 หลัก หรือ 4 ตัวท้าย: ").strip()
            if sid == "":
                print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                continue
            if not sid.isdigit():
                print("กรุณาใส่รหัสนักศึกษาเป็นตัวเลข")
                continue

            # เช็คความยาว 4 หลัก หรือ 13 หลัก
            if len(sid) not in [4, 13]:
                print("กรุณาใส่รหัสนักศึกษาให้ครบ")
                continue
            check_sid = Student(db,None,sid,None)

            if not check_sid.check_student_id() and not dbm.check_last_4_ID(sid):
                print("ไม่พบรหัสนักศึกษานี้ในระบบ")
                continue
            pj_namee = dbm.get_all_Project_by_sid(sid)
            student_id = dbm.get_student_id_by_project_name(pj_namee)
            
            dbm.open_project_file(pj_namee, student_id)

        elif action == '7':
            input_PIN = input("Enter Admin PIN: ").strip()
            if input_PIN == "":
                print("กรุณาใส่ข้อมูล ห้ามเว้นว่าง")
                continue

            admin = Admin(db)
            if admin.check_pin(input_PIN):
                while True:
                    admin_action = input(
                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการแก้ไข \n"
                        "[1] ลบข้อมูลนักศึกษา \n"
                        "[2] ลบข้อมูลโครงการ \n"
                        "[3] ออก \n"
                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการ: "
                    ).strip()
                    if not admin_action.isdigit() or int(admin_action) not in range(1, 4):
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
                        continue

                    elif admin_action == '1':
                        print("-"*40)
                        dbm.fetch_AllStudents()
                        input_id3 = input("Select ID to Delete: ").strip()
                        admin.Delete_Student_data(input_id3)
                        dbm.fetch_AllStudents()
                        print("-"*40)

                    elif admin_action == '2':
                        print("-"*40)
                        dbm.fetch_AllProjects()
                        input_id4 = input("Select ID to Delete: ").strip()
                        delete_project_name = dbm.get_Projectinfo_by_id(input_id4)
                        admin.Delete_Project_data(input_id4)
                        dbm.fetch_AllProjects()
                        print(f"ลบข้อมูลกับโฟลเดอร์ของโครงการ {delete_project_name} เรียบร้อยแล้ว")
                    elif admin_action == '3':
                        print("-"*40)
                        print("ออกจากโหมดแอดมิน")
                        break

            else:
                print("รหัสผ่านไม่ถูกต้อง")
                continue

        elif action == '8':
            print("-"*40)
            print("จบการทำงาน")
            break

if __name__ == "__main__":
    main()