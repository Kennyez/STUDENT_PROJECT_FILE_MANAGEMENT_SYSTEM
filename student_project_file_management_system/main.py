# filepath: student_project_file_management_system/main.py

class Student:
    def __init__(self, student_id, name, email):
        self.student_id = student_id
        self.name = name
        self.email = email

    def get_student_info(self):
        return {
            "Student ID": self.student_id,
            "Name": self.name,
            "Email": self.email
        }


class Project:
    def __init__(self, project_name, description, academic_year, related_files):
        self.project_name = project_name
        self.description = description
        self.academic_year = academic_year
        self.related_files = related_files

    def get_project_info(self):
        return {
            "Project Name": self.project_name,
            "Description": self.description,
            "Academic Year": self.academic_year,
            "Related Files": self.related_files
        }


class DatabaseManager:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.projects = []

    def connect(self):
        # Simulate a database connection
        print("Connected to the database.")

    def upload_file(self, project):
        self.projects.append(project)
        print(f"Uploaded project: {project.project_name}")

    def search_projects(self, search_term):
        return [project for project in self.projects if search_term.lower() in project.project_name.lower()]

    def display_projects(self):
        for project in self.projects:
            print(project.get_project_info())


def main():
    db_manager = DatabaseManager("sqlite:///student_projects.db")
    db_manager.connect()

    while True:
        action = input("Choose an action: [1] Add Project [2] Search Projects [3] Display Projects [4] Exit: ")

        if action == '1':
            student_id = input("Enter Student ID: ")
            name = input("Enter Student Name: ")
            email = input("Enter Student Email: ")
            student = Student(student_id, name, email)

            project_name = input("Enter Project Name: ")
            description = input("Enter Project Description: ")
            academic_year = input("Enter Academic Year: ")
            related_files = input("Enter Related Files (comma-separated): ").split(',')

            project = Project(project_name, description, academic_year, related_files)
            db_manager.upload_file(project)

        elif action == '2':
            search_term = input("Enter search term for projects: ")
            results = db_manager.search_projects(search_term)
            if results:
                for project in results:
                    print(project.get_project_info())
            else:
                print("No projects found.")

        elif action == '3':
            db_manager.display_projects()

        elif action == '4':
            print("Exiting the system.")
            break

        else:
            print("Invalid action. Please try again.")


if __name__ == "__main__":
    main()