from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, ttk
import shutil
import os
import sqlite3
from datetime import datetime
from matplotlib.pylab import delete
import re
# PATH = os.getcwd()
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('Data.sqlite3') #สร้างฐานข้อมูล
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.c = self.conn.cursor()

        #สร้างตาราง Student ในฐานข้อมูล
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
                    Year INTEGER,
                    FOREIGN KEY(Student_id) REFERENCES Student(Student_id)
                )
        """)
 #เก็บข้อมูลนักศึกษาและส่งไปบันทึกในฐานข้อมูล
class Student: 
    # def __init__(self,student_name = None,student_id = None,student_email = None):
    def __init__(self):
        # self.__student_name = student_name
        # self.__student_id = student_id
        # self.__student_email = student_email
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()

    #Method รับข้อมูลนักศึกษาและบันทึกลงฐานข้อมูล
    def New_Student(self,student_name,student_id,student_email):
        try:
            with self.conn:
                #  เพิ่มข้อมูลนักศึกษาในตาราง Student
                command1 = '''
                    INSERT INTO Student (Student_name, Student_id, Email) VALUES (?,?,?)
                '''
                self.c.execute(command1, (student_name, student_id, student_email))
            self.conn.commit()
            print(f"สร้างเพิ่มข้อมูลนักศึกษาของ {student_name} เสร็จสิ้น")

        except sqlite3.IntegrityError as e:
            print("เกิดข้อผิดพลาด: ข้อมูลซ้ำหรือผิดพลาด ->", e)

    #ตรวจสอบรูปแบบอีเมล
    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    #เช็คอีเมลซ้ำหรือไม่
    def check_email(self,student_email):
        with self.conn:
            self.c.execute("SELECT 1 FROM Student WHERE Email = ?", (student_email,))
            return self.c.fetchone() is not None


 #เก็บข้อมูลโครงการและส่งไปบันทึกในฐานข้อมูล
class Project(Student): 
    # def __init__(self, project_name = None, description = None, year = None, **kwargs):
    def __init__(self):
        # super().__init__(project_name,description,year,**kwargs)
        # self.__project_name = project_name
        # self.description = description
        # self.year = year
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()

    #Method รับข้อมูลโครงการและบันทึกลงฐานข้อมูล
    def New_Project(self, project_name, description, year, student_name, student_id):
        try:
            with self.conn:
                #เพิ่มข้อมูลโปรเจกต์ พร้อมเชื่อมกับ student_id และ owner
                command = '''
                    INSERT INTO Project (Project_name, Description, Year, Owner, Student_id) VALUES (?,?,?,?,?)
                '''
                self.c.execute(command, (project_name, description, year, student_name, student_id))

            self.conn.commit()
            print(f"สร้างโครงการ {project_name} เสร็จสิ้น")
        except sqlite3.IntegrityError as e:
            print("เกิดข้อผิดพลาด: ข้อมูลซ้ำหรือผิดพลาด ->", e)

    def check_Project_name(self, project_name):
        with self.conn:
            self.c.execute("SELECT 1 FROM Project WHERE Project_name = ?", (project_name,))
            return self.c.fetchone() is not None

    #สร้างโฟลเดอร์ของโครงการหลังสร้างโครงการใหม่
    def create_project(self, project_name, parent_folder="Project_list"):
        if parent_folder:
            path = os.path.join(parent_folder, project_name)
        else:
            path = project_name
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"สร้างโฟลเดอร์สำหรับ {project_name} เสร็จสิ้น.")
        else:
            print(f"มี '{project_name}' อยู่แล้ว.")

    

#ติดต่อฐานข้อมูล
class Database_manager(): 
    def __init__(self):
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()
    # ดึงข้อมูลนักศึกษาทั้งหมด
    def fetch_Students(self):   
        self.c.execute("SELECT * FROM Student")
        print(self.c.fetchall())
        return self.c.fetchall()
    
    # ดึงข้อมูลโปรเจกต์ทั้งหมด
    def fetch_Projects(self):
        # self.c.execute("SELECT * FROM Project")
        self.c.execute("""SELECT Student.Student_name, Student.Student_id, Student.Email, Project.Project_name, Project.Year
            FROM Project
            JOIN Student ON Project.Student_id = Student.Student_id
        """)
        # print(self.c.fetchall())
        # return self.c.fetchall()
        results = self.c.fetchall()
        if results:
            for student_name, student_id, email, project_name, year in results:
                print("-" * 100)
                print(f"ชื่อโครงการ: {project_name}, เจ้าของโครงการ: {student_name}, รหัสนักศึกษา: {student_id}, Email: {email}, ปี: {year}")
                
        
    # def fetch_student_projects(self):
    #     # ดึงข้อมูลโปรเจกต์ พร้อมข้อมูลต่างๆ
    #     self.c.execute("""
    #         SELECT Student.Student_name, Student.Email, Project.Project_name, Project.Year
    #         FROM Project
    #         JOIN Student ON Project.Student_id = Student.Student_id
    #     """)
    #     return self.c.fetchall()

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

#classของ adminไว้แก้ไขข้อมูลใน database
class Admin(): 
    def __init__(self,pin = "1111"): #กำหนด pin คือ 1111
        self.__pin = pin
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()

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
    def update_Student_Data(self,student_name,student_id,student_email,ID): #ฟังชัน อัปเดตข้อมูลในตาราง Student
        with self.conn:
            command = 'UPDATE Student SET Student_name = ?, Student_id = ?, Email = ? WHERE ID = ?'
            self.c.execute(command,(student_name,student_id,student_email,ID))
        self.conn.commit()

    #ลบข้อมูลโครงการออกจากฐานข้อมูล
    def Delete_Project_data (self, ID):
        with self.conn:
            command = 'DELETE FROM Project WHERE ID=(?)'
            self.c.execute(command,([ID]))
        self.conn.commit()
        print("ลบข้อมูลโครงการเรียบร้อยแล้ว")

    #ลบข้อมูลนักศึกษาออกจากฐานข้อมูล
    def Delete_Student_data (self, ID):
        with self.conn:
            command = 'DELETE FROM Student WHERE ID=(?)'
            self.c.execute(command,([ID]))
        self.conn.commit()
        print("ลบข้อมูลนักศึกษาเรียบร้อยแล้ว")
    
#ไว้อัพโหลดไฟล์ต่างๆ
class Uploadfile:
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

#เรียกใช้งาน
def main():

    while True:
        Database() #สร้างฐานข้อมูล
        action = input(
            "---------------------------------------- \n"
            "ระบบจัดเก็บไฟล์โครงการของนักศึกษา \n"            
            "[1] เพิ่มโครงการใหม่ (ชื่อ เลขประจำตัว ) \n"   #(ชื่อ รหัสนักศึกษา )
            "[2] ใส่ข้อมูลในโครงการ \n"                  #( [ ลงในที่สร้างจาก 1 ] ใส่แค่ชื่อโปคเจค รายะเอียด ปี)
            "[3] เพิ่มไฟล์ \n"                          #( [ ลงในที่สร้างจาก 1 ] รูป เอกสาร)
            "[4] ค้นหาข้อมูลโครงการ \n"            #(แสดงชื่อโครงการ ชื่อเจ้าของโครงการ รหัสนักศึกษา Email ปี)
            "[5] เรียกดูไฟล์โครงการ\n"
            "[6] ตัวเลือกแอดมิน \n"
            "[7] ยกเลิก \n"
            "---------------------------------------- \n"
            "เลือกรายการที่ต้องการ: "
            )

        if not action.isdigit() or int(action) not in range(1, 8):
            print("Error: กรุณาเลือกรายการให้ถูกต้อง")
            continue
            
        if action == '1':
            while True:
                print("-"*40)
                NewStudent = Student()
                NewProject = Project()

                input_name = input("Enter Student Name: ")
                input_student_id = input("Enter Student ID: ")
                input_email = input("Enter Student Email: ")
                if not NewStudent.is_valid_email(input_email):
                    print("รูปแบบอีเมลไม่ถูกต้อง")
                    continue
                if NewStudent.check_email(input_email):
                    print("Email นี้มีอยู่แล้ว")
                    continue

                input_project_name = input("Enter Project Name: ")

                if NewProject.check_Project_name(input_project_name):
                    print("Project นี้มีอยู่แล้ว")
                    continue

                input_description = input("Enter Project Description: ")
                input_year = input("Enter Academic Year: ")

                NewStudent.New_Student(input_name, input_student_id, input_email)
                NewProject.New_Project(input_project_name, input_description, input_year, input_name, input_student_id)
                NewProject.create_project(input_project_name)
                test = Database_manager()
                test.fetch_Students()
                test.fetch_Projects()
                break

        elif action == '2':
            print("-"*40)
            
        elif action == '3':
            show_Projects_info = Database_manager()
            CheckProject = Project()
            show_Projects_info.fetch_Projects()
            input_upload_Project_name = input("Enter Project Name to upload file: ")
            if not CheckProject.check_Project_name(input_upload_Project_name):
                print(f"ไม่พบโครงการ {input_upload_Project_name} ในระบบ")
                continue
            Uploadfile(input_upload_Project_name)

        elif action == '4':
            print("-"*40)
            input_keyword = input("ใส่ชื่อโครงการ หรือ รหัสนักศึกษา  : ")
            Search = Database_manager()
            Search.search_project(input_keyword)

        elif action == '5':
            print("-"*40)
            Search = Database_manager()
            Search.fetch_Projects()
            input_open_Project_name = input("ใส่ชื่อโครงการที่ต้องการดูไฟล์: ")
            Search.open_project_file(input_open_Project_name)

        elif action == '6':
            input_PIN = input("Enter Admin PIN: ")
            admin = Admin()
            if admin.check_pin(input_PIN):
                while True:
                    
                    admin_action = input(
                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการแก้ไข \n"
                        "[1] แก้ไขข้อมูลนักศึกษา \n"
                        "[2] แก้ไขข้อมูลโครงการ \n"
                        "[3] ลบข้อมูลนักศึกษา \n"
                        "[4] ลบข้อมูลโครงการ \n"
                        "[5] ออก \n"

                        "---------------------------------------- \n"
                        "เลือกรายการที่ต้องการ: "
                    )
                    if not admin_action.isdigit() or int(admin_action) not in range(1, 6):
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
                        continue

                    if admin_action == '1':
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

                    elif admin_action == '2':
                        print("-"*40)
                        admin1 = Database_manager()
                        admin2 = Admin()
                        admin1.fetch_Projects()
                        input_id2 = input("Enter Project ID to update: ")
                        new_project_name = input("Enter new Project Name: ")
                        new_description = input("Enter new Description: ")
                        new_year = input("Enter new Year: ")
                        admin2.update_Project_Data(new_project_name, new_description, new_year, input_id2)
                        admin1.fetch_Projects()
                        print("อัปเดตข้อมูลโครงการเรียบร้อยแล้ว")
                        print("-"*40)

                    elif admin_action == '3':
                        print("-"*40)
                        admin1 = Database_manager()
                        admin2 = Admin()
                        admin1.fetch_Students()
                        input_id3 = input("Select ID to Delete: ")
                        admin2.Delete_Student_data(input_id3)
                        admin1.fetch_Students()
                        print("ลบข้อมูลนักศึกษาเรียบร้อยแล้ว")
                        print("-"*40)

                    elif admin_action == '4':
                        print("-"*40)
                        admin1 = Database_manager()
                        admin2 = Admin()
                        admin1.fetch_Projects()
                        input_id4 = input("Select ID to Delete: ")
                        admin2.Delete_Project_data(input_id4)
                        admin1.fetch_Projects()
                        print("ลบข้อมูลโครงการเรียบร้อยแล้ว")
                        print("-"*40)

                    elif admin_action == '5':
                        print("ออกจากโหมดแอดมิน")
                        break

                    # else:
                    #     print("Error: กรุณาเลือกรายการให้ถูกต้อง")
            else:
                print("รหัสผ่านไม่ถูกต้อง")
                continue

        elif action == '7':

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

 