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

conn = sqlite3.connect('Data.sqlite3') #สร้างตารางในsqlite3
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS Student (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_name TEXT UNIQUE,
        Student_id INTEGER UNIQUE,
        Email TEXT UNIQUE
    )
""")

c.execute("""
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

class Student: #ข้อมูลนักศึกษา
    def __init__(self,student_name = None,student_id = None,student_email = None):
        self.__student_name = student_name
        self.__student_id = student_id
        self.__student_email = student_email
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()

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

    
    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def check_email(self,__student_email):
        with self.conn:
            self.c.execute("SELECT 1 FROM Student WHERE Email = ?", (__student_email,))
            return self.c.fetchone() is not None
        
class Project(Student): #ข้อมูลโครงการ
    def __init__(self, project_name = None, description = None, year = None, **kwargs):
        super().__init__(project_name,description,year,**kwargs)
        self.__project_name = project_name
        self.description = description
        self.year = year
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()
            
    def New_Project(self, project_name, description, year, student_name, student_id):
        try:
            with self.conn:
                #เพิ่มข้อมูลโปรเจกต์ พร้อมเชื่อมกับ student_id และ owner
                command = '''
                    INSERT INTO Project (Project_name, Description, Year, Owner, Student_id) VALUES (?,?,?,?,?)
                '''
                self.c.execute(command, (project_name, description, year, student_name, student_id))

            self.conn.commit()
            print(f"สร้าง {project_name} เสร็จสิ้น")
        except sqlite3.IntegrityError as e:
            print("เกิดข้อผิดพลาด: ข้อมูลซ้ำหรือผิดพลาด ->", e)

    


class Database_manager(): #ติดต่อฐานข้อมูล

    def __init__(self):
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()

    def fetch_Students(self):   
        # ดึงข้อมูลนักศึกษาทั้งหมด
        self.c.execute("SELECT * FROM Student")
        print(self.c.fetchall())
        return self.c.fetchall()

    def fetch_Projects(self):
        # ดึงข้อมูลโปรเจกต์ทั้งหมด
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
                
        
    def fetch_student_projects(self):
        # ดึงข้อมูลโปรเจกต์ พร้อมข้อมูลต่างๆ
        self.c.execute("""
            SELECT Student.Student_name, Student.Email, Project.Project_name, Project.Year
            FROM Project
            JOIN Student ON Project.Student_id = Student.Student_id
        """)
        return self.c.fetchall()

    def search_project(self, Keyword): #ค้นหาข้อมูลโครงการ
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
            print("No projects found.")

    def create_project(self, project_name, parent_folder="Project_list"):
        if parent_folder:
            path = os.path.join(parent_folder, project_name)
        else:
            path = project_name
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"สร้าง '{project_name}' เสร็จสิ้น.")
        else:
            print(f"มี '{project_name}' อยู่แล้ว.")

    def open_project_file(self, project_name,parent_folder="Project_list"):
        if parent_folder:
            path = os.path.join(parent_folder, project_name)
        else:
            path = project_name
        if os.path.exists(path):
            os.startfile(path)
            print(f"Opened file '{project_name}'.")
        else:
            print(f"File '{project_name}' does not exist.")

class Admin(): #classของ adminไว้แก้ไขข้อมูลใน database
    def __init__(self,pin = "1111"):
        self.__pin = pin
        self.conn = sqlite3.connect('Data.sqlite3')
        self.c = self.conn.cursor()

    def check_pin(self,input_pin):
        if input_pin == self.__pin:
            print("รหัสถูก")
            return True

    def update_Project_Data(self,project_name,description,year,ID): #ฟังชัน อัปเดตข้อมูลในตาราง Project
        with self.conn:
            command = 'UPDATE Project SET Project_name = ?, Description = ?, Year = ? WHERE ID = ?'
            self.c.execute(command,(project_name,description,year,ID))
        self.conn.commit()

    def update_Student_Data(self,student_name,student_id,student_email,ID): #ฟังชัน อัปเดตข้อมูลในตาราง Student
        with self.conn:
            command = 'UPDATE Student SET Student_name = ?, Student_id = ?, Email = ? WHERE ID = ?'
            self.c.execute(command,(student_name,student_id,student_email,ID))
        self.conn.commit()

    def Delete_Project_data (self, ID):
        with self.conn:
            command = 'DELETE FROM Project WHERE ID=(?)'
            self.c.execute(command,([ID]))
        self.conn.commit()
        print("ลบข้อมูลโครงการเรียบร้อยแล้ว")

    def Delete_Student_data (self, ID):
        with self.conn:
            command = 'DELETE FROM Student WHERE ID=(?)'
            self.c.execute(command,([ID]))
        self.conn.commit()
        print("ลบข้อมูลนักศึกษาเรียบร้อยแล้ว")
class Uploadfile:
    def __init__(self,Project_name):
        self.root = tk.Tk()
        self.root.title("Upload File")
        self.root.geometry("350x200")

        self.label = ttk.Label(self.root, text="ยังไม่ได้เลือกไฟล์")
        self.label.pack(pady=10)
        self.btn_upload = ttk.Button(self.root, text="เลือกไฟล์", command=lambda : self.upload_file(Project_name))
        self.btn_upload.pack(pady=10)
        self.root.mainloop()


    # def upload_file(self,Project_name,parent_folder="Project_list"):
    #     # เปิด dialog ให้เลือกไฟล์
    #     file_path = filedialog.askopenfilename(
    #         title="asd",
    #         filetypes=(("All files", "*.*"),("Text files", "*.txt"))
    #     )
    #     if parent_folder:  # ถ้าเลือกไฟล์จริงๆ
    #         # โชว์ path บน label
    #         # self.label.config(text=f"เลือกไฟล์: {os.path.basename(file_path)}")
    #         path = os.path.join(parent_folder, Project_name)
    #     else:
    #         path = Project_name
    #         # สมมุติว่าอยาก copy ไฟล์ไปเก็บในโฟลเดอร์ uploads
    #     if  os.path.exists(path):
    #         self.label.config(text=f"เลือกไฟล์: {(file_path)}")
    #         # save_dir = parent_folder
    #         os.makedirs(path, exist_ok=True)
    #         shutil.copy(file_path, path)
    #         print(f"ไฟล์ {file_path} ถูกอัปโหลดไปที่ {path}")

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

        self.label.config(text=f"อัปโหลดไฟล์: {os.path.basename(file_path)}")
        print(f"ไฟล์ {file_path} ถูกอัปโหลดไปที่ {PATH}/{path}")

def main():

    while True:

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
                input_name = input("Enter Student Name: ")
                input_student_id = input("Enter Student ID: ")
                input_email = input("Enter Student Email: ")
                check = Student()
                if not check.is_valid_email(input_email):
                    print("รูปแบบอีเมลไม่ถูกต้อง")
                    continue
                if check.check_email(input_email):
                    print("Email นี้มีอยู่แล้ว")
                    continue
                NewStudent = Student()
                NewStudent.New_Student(input_name, input_student_id, input_email)

                input_project_name = input("Enter Project Name: ")
                input_description = input("Enter Project Description: ")
                input_year = input("Enter Academic Year: ")
                NewProject = Project()
                NewProject.New_Project(input_project_name, input_description, input_year, input_name, input_student_id)
                test = Database_manager()
                test.fetch_Students()
                test.fetch_Projects()

        elif action == '2':
            print("-"*40)
            
        elif action == '3':
            print("-"*40)
            show_Projects_info = Database_manager()
            show_Projects_info.fetch_Projects()
            in_put_Project_name = input("Enter Project Name to upload file: ")
            Uploadfile(in_put_Project_name)

        elif action == '4':
            print("-"*40)
            input_keyword = input("ใส่ชื่อโครงการ หรือ รหัสนักศึกษา  : ")
            Search = Database_manager()
            Search.search_project(input_keyword)

        elif action == '5':

            print("-"*40)

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

                    else:
                        print("Error: กรุณาเลือกรายการให้ถูกต้อง")
            else:
                print("รหัสผ่านไม่ถูกต้อง")
                continue

        elif action == '7':

            print("-"*40)
            print("จบการทำงาน")
            break

        else:
            print("เกิดข้อผิดพลาด กรุณาลองใหม่")


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

 