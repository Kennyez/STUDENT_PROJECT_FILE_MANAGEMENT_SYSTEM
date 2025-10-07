# Student Project File Management System

A Python-based system to manage students, projects, and file uploads for each project.  
Supports creating students, creating projects linked to students, uploading files to project folders, searching, editing, and deleting, with GUI support using Tkinter.

---

## 📂 Features

- Create / update / delete **Student** records  
- Create / update / delete **Project** records linked to students  
- Upload files to specific project folders  
- Browse, delete, and open project files  
- Search projects by name or student ID  
- GUI interface (Tkinter) for uploading files  
- Safety features such as confirmation before deletion  

---

## 🛠️ Requirements

- Python 3.x  
- Standard Python libraries: `sqlite3`, `os`, `shutil`, `tkinter`, `ctypes`  
- (Optional) For recycle bin deletion on Windows: using `ctypes` / `shell32` as shown in code  

---

## 🚀 Setup & Run

1. Clone the repository  
   ```bash
   git clone https://github.com/Kennyez/STUDENT_PROJECT_FILE_MANAGEMENT_SYSTEM.git
   cd STUDENT_PROJECT_FILE_MANAGEMENT_SYSTEM
2. (Optional) Create a virtual environment

  - `python -m venv venv`
  - `source venv/bin/activate`   # Linux / macOS
  - `venv\Scripts\activate`      # Windows


3. Run the application
  - `python main_oop.py`
4. Use the menu to add students, projects, manage files, search, etc.

---

## 📁 Project Structure
   ```bash
   ├── main_oop.py                # The main entry point of the application
   ├── oop.py                      # Core classes (Database, Student, Project, Admin, FileManager)
   ├── background.jpg              # GUI background image
   ├── fupload.ico                 # Icon for upload GUI
   └── (other files, README, etc.)
  ```

---
## 🧾 Usage Examples
-Add a Student

- Choose menu “เพิ่มข้อมูลนักศึกษา (option 1)”

- Enter name, student ID (13 digits) and email

- Add a Project

- Choose project menu

- Enter student ID (either full 13 digits or last 4 digits)

- Enter project name, description, year

- Upload a File

- Choose menu to manage files

- Select a project name

- Use file dialog to choose file → file will be copied into folder structure

- Use list / delete methods to manage existing files

---

## ⚠️ Notes & Tips

-Be careful when deleting students — this also deletes all their project folders and files

-On Windows, file deletion uses Windows Shell API to move files to Recycle Bin

-If student ID is input as 4 last digits, system will search matching students

-Always check return values / confirmations before destructive actions

---

## 🔐 License & Author

- Author: Kennyez

- License: (you can specify your preferred license, e.g. MIT License)

--- 

## 🧩 Improvements You Could Add

- Better GUI for the full application (not just file upload)

- Validation of project name uniqueness

- File upload size or extension restrictions

- Multi-platform support (macOS/Linux) for recycle bin

- Export / import of database backup

- Unit tests for key functionalities
- 
