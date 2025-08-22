import os
import sqlite3
PATH = os.getcwd()
##########สร้างตาราง sqlite
class Student: #ข้อมูลนักศึกษา
    def __init__(self,student_id,student_name,student_email,**kwargs):
        super().__init__(**kwargs) #chain ต่อไปถ้ามี
        self.__student_id = student_id
        self.__student_name = student_name
        self.__student_email = student_email

    def input_data(self):
        self.name = input("กรอกชื่อนักศึกษา: ")
        self.age = int(input("กรอกอายุ: "))

    def show_data(self):
        print(f"ชื่อนักศึกษา: {self.name}")
        print(f"อายุ: {self.age}")

class Project(Student): #ข้อมูลโครงการ
    def __init__(self, project_name, description, year,**kwargs):
        super().__init__(**kwargs)
        self.__project_name = project_name
        self.description = description
        self.year = year

class Database_manager(Project): #ติดต่อฐานข้อมูล
##########สร้างMethod เพิ่มข้อมูลลงใน database

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.__projects_list = [] #####สร้างใหม่

    def show_project_info(self):
        for project in self.__projects_list:
            print(f"Project Name: {self.__project_name}")
            print(f"Description: {self.description}")
            print(f"Year: {project.year}")

    def search_project(self, project_name): ###ทำใหม่
        for project in self.__projects_list:
            if project.name == project_name:
                print(f"Project Name: {self.__project_name}")
                print(f"Description: {self.description}")
                print(f"Year: {self.year}")
                return
        print("Project not found.")

    def create_project(self, project_name, parent_folder="Project_list"):
        if parent_folder:
            path = os.path.join(parent_folder, project_name)
        else:
            path = project_name
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Project '{project_name}' has been created.")
        else:
            print(f"Project '{project_name}' already exists.")

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

class Project_Management_System: #ควบคุมการทำงานของระบบ
    def __init__(self):
        self.database_manager = Database_manager()

# ken = Student()
# ken.open_project_file("kenGod4")

