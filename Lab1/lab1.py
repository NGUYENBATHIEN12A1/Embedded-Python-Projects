# ==========================================
# LAB 1 - EXERCISE 1
# STUDENT INFORMATION MANAGEMENT
# Procedural Programming
# ==========================================


# ------------------------------------------
# Hàm xếp loại sinh viên dựa vào GPA
# ------------------------------------------
def calculate_grade(gpa):
    if gpa >= 3.60:
        return "Excellent"
    elif gpa >= 3.20:
        return "Very Good"
    elif gpa >= 2.50:
        return "Good"
    elif gpa >= 2.00:
        return "Average"
    else:
        return "Poor"


# ------------------------------------------
# Hàm nhập thông tin cho một sinh viên
# ------------------------------------------
def input_student():

    student_id = input("Enter Student ID: ")
    name = input("Enter Full Name: ")

    age = int(input("Enter Age: "))

    major = input("Enter Major: ")

    gpa = float(input("Enter GPA: "))

    # Tạo dictionary chứa thông tin sinh viên
    student = {
        "id": student_id,
        "name": name,
        "age": age,
        "major": major,
        "gpa": gpa
    }

    return student


# ------------------------------------------
# Hàm hiển thị danh sách sinh viên
# ------------------------------------------
def display_students(students):

    print("\n" + "-" * 75)

    print(f"{'ID':<10}"
          f"{'Name':<20}"
          f"{'Age':<8}"
          f"{'Major':<12}"
          f"{'GPA':<8}"
          f"{'Classification':<15}")

    print("-" * 75)

    for student in students:

        grade = calculate_grade(student["gpa"])

        print(f"{student['id']:<10}"
              f"{student['name']:<20}"
              f"{student['age']:<8}"
              f"{student['major']:<12}"
              f"{student['gpa']:<8.2f}"
              f"{grade:<15}")

    print("-" * 75)


# ------------------------------------------
# Hàm hiển thị thống kê
# ------------------------------------------
def display_statistics(students):

    # Nếu chưa có sinh viên
    if len(students) == 0:
        print("No student data.")
        return

    total_students = len(students)

    total_gpa = 0

    highest_gpa = students[0]["gpa"]
    lowest_gpa = students[0]["gpa"]

    excellent_count = 0

    # Duyệt qua từng sinh viên
    for student in students:

        gpa = student["gpa"]

        # Cộng GPA
        total_gpa += gpa

        # Tìm GPA cao nhất
        if gpa > highest_gpa:
            highest_gpa = gpa

        # Tìm GPA thấp nhất
        if gpa < lowest_gpa:
            lowest_gpa = gpa

        # Đếm số sinh viên Excellent
        if calculate_grade(gpa) == "Excellent":
            excellent_count += 1

    # Tính GPA trung bình
    average_gpa = total_gpa / total_students

    # Hiển thị kết quả
    print("\n===== STATISTICS =====")

    print("Total Students:", total_students)
    print(f"Average GPA: {average_gpa:.2f}")
    print(f"Highest GPA: {highest_gpa:.2f}")
    print(f"Lowest GPA: {lowest_gpa:.2f}")
    print("Excellent Students:", excellent_count)


# ------------------------------------------
# Hàm tìm sinh viên theo Student ID
# ------------------------------------------
def search_student(students):

    search_id = input("\nEnter Student ID to search: ")

    # Duyệt từng sinh viên
    for student in students:

        # Kiểm tra ID
        if student["id"] == search_id:

            print("\nStudent Found!")

            print("ID:", student["id"])
            print("Name:", student["name"])
            print("Age:", student["age"])
            print("Major:", student["major"])
            print(f"GPA: {student['gpa']:.2f}")
            print("Classification:",
                  calculate_grade(student["gpa"]))

            return

    # Nếu duyệt hết mà không tìm thấy
    print("Student not found.")


# ==========================================
# MAIN PROGRAM
# ==========================================

# Tạo danh sách rỗng để lưu sinh viên
students = []


# Nhập số lượng sinh viên
number = int(input("Enter number of students: "))


# Vòng lặp nhập thông tin
for i in range(number):

    print(f"\n--- Enter information for student {i + 1} ---")

    student = input_student()

    # Thêm sinh viên vào danh sách
    students.append(student)


# Hiển thị danh sách sinh viên
display_students(students)


# Hiển thị thống kê
display_statistics(students)


# Tìm kiếm sinh viên
search_student(students)




























# ==========================================
# LAB 1 - EXERCISE 2
# STUDENT MANAGEMENT SYSTEM
# Object-Oriented Programming
# ==========================================

# ------------------------------------------
# Part 1 & Part 2: Create Student class and methods
# ------------------------------------------
class Student:
    def __init__(self, student_id, name, age, major, gpa):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.major = major
        self.gpa = gpa

    def calculate_grade(self):
        if self.gpa >= 3.60:
            return "Excellent"
        elif self.gpa >= 3.20:
            return "Very Good"
        elif self.gpa >= 2.50:
            return "Good"
        elif self.gpa >= 2.00:
            return "Average"
        else:
            return "Poor"

    def update_gpa(self, new_gpa):
        self.gpa = new_gpa

    def is_honor_student(self):
        return self.gpa >= 3.60

    def display_information(self):
        classification = self.calculate_grade()
        # Định dạng in ra màn hình. Sinh viên thường không có Research Topic nên để N/A
        print(f"{self.student_id:<10}{self.name:<20}{self.major:<12}{self.gpa:<8.2f}{classification:<15}{'N/A':<25}")


# ------------------------------------------
# Part 3: Create GraduateStudent class
# ------------------------------------------
class GraduateStudent(Student):
    def __init__(self, student_id, name, age, major, gpa, research_topic, advisor):
        # Kế thừa các thuộc tính cơ bản từ lớp cha (Student)
        super().__init__(student_id, name, age, major, gpa)
        self.research_topic = research_topic
        self.advisor = advisor

    def display_research_information(self):
        print(f"Research Topic: {self.research_topic} | Advisor: {self.advisor}")

    # Ghi đè (override) lại hàm display_information để hiển thị thêm cột Research Topic
    def display_information(self):
        classification = self.calculate_grade()
        print(f"{self.student_id:<10}{self.name:<20}{self.major:<12}{self.gpa:<8.2f}{classification:<15}{self.research_topic:<25}")

# ==========================================
# MAIN PROGRAM
# ==========================================
if __name__ == "__main__":
    
    # ------------------------------------------
    # Part 4: Create objects
    # ------------------------------------------
    # Khởi tạo 3 đối tượng Student
    s1 = Student("1001", "Alice", 20, "CE", 3.85)
    s2 = Student("1002", "Bob", 21, "EE", 2.75)
    s3 = Student("1003", "John", 20, "IT", 3.45)

    # Khởi tạo 2 đối tượng GraduateStudent
    gs1 = GraduateStudent("2001", "David", 24, "CE", 3.90, "IC Design", "Dr. Smith")
    gs2 = GraduateStudent("2002", "Eva", 23, "CS", 3.50, "AI in Healthcare", "Dr. Brown")

    # Lưu toàn bộ vào một list
    all_students = [s1, s2, s3, gs1, gs2]

    # ------------------------------------------
    # Part 5: Display Information
    # ------------------------------------------
    print("\n" + "-" * 90)
    print(f"{'ID':<10}{'Name':<20}{'Major':<12}{'GPA':<8}{'Classification':<15}{'Research Topic':<25}")
    print("-" * 90)

    # Duyệt qua list và in thông tin
    for student in all_students:
        student.display_information()
    
    print("-" * 90)
