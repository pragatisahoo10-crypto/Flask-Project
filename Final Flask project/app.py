from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import Config
import math
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "my_super_secret_key_123"
mysql = MySQL(app)

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ==================== Create Admin ======================== #
@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']


        cur = mysql.connection.cursor()

        # Check if admin already exists
        cur.execute("SELECT * FROM login WHERE username=%s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return render_template("create_admin.html",
                                   error="Admin already exists!")

        cur.execute("INSERT INTO login (username, password) VALUES (%s, %s)",
                    (username, password))
        mysql.connection.commit()

        return render_template("create_admin.html",
                               success="Admin created successfully!")

    return render_template("create_admin.html")

# ================= LOGIN REQUIRED DECORATOR ================= #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ================= LOGIN ================= #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM login WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()

        if user:
            session.permanent = True
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html",
                                   error="Invalid username or password")

    return render_template("login.html")

# ================= LOGOUT ================= #

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================= DASHBOARD ================= #

@app.route('/')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM students WHERE is_deleted=0")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM teachers WHERE is_deleted=0")
    total_teachers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM courses WHERE is_deleted=0")
    total_courses = cur.fetchone()[0]

    return render_template("dashboard.html",
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_courses=total_courses)

# ================= STUDENTS ================= #

@app.route('/students')
@login_required
def students():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM students WHERE is_deleted=0")
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT id, name, email, phone
        FROM students
        WHERE is_deleted=0
        LIMIT %s OFFSET %s
    """, (per_page, offset))

    data = cur.fetchall()
    total_pages = math.ceil(total / per_page)

    return render_template("students.html",
                           students=data,
                           page=page,
                           total_pages=total_pages)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO students(name,email,phone,is_deleted)
            VALUES(%s,%s,%s,0)
        """, (name, email, phone))
        mysql.connection.commit()
        return redirect(url_for('students'))

    return render_template("add_student.html")

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cur.execute("""
            UPDATE students
            SET name=%s,email=%s,phone=%s
            WHERE id=%s AND is_deleted=0
        """, (name, email, phone, id))

        mysql.connection.commit()
        return redirect(url_for('students'))

    cur.execute("""
        SELECT id,name,email,phone
        FROM students
        WHERE id=%s AND is_deleted=0
    """, (id,))
    student = cur.fetchone()

    return render_template("edit_student.html", student=student)

@app.route('/delete_student/<int:id>')
@login_required
def delete_student(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE students
        SET is_deleted=1
        WHERE id=%s
    """, (id,))
    mysql.connection.commit()
    return redirect(url_for('students'))

# ================= TEACHERS ================= #

@app.route('/teachers')
@login_required
def teachers():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM teachers WHERE is_deleted=0")
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT id,name,email,designation
        FROM teachers
        WHERE is_deleted=0
        LIMIT %s OFFSET %s
    """, (per_page, offset))

    data = cur.fetchall()
    total_pages = math.ceil(total / per_page)

    return render_template("teachers.html",
                           teachers=data,
                           page=page,
                           total_pages=total_pages)

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        designation = request.form['designation']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO teachers(name,email,designation,is_deleted)
            VALUES(%s,%s,%s,0)
        """, (name, email, designation))
        mysql.connection.commit()
        return redirect(url_for('teachers'))

    return render_template("add_teacher.html")

@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        designation = request.form['designation']

        cur.execute("""
            UPDATE teachers
            SET name=%s,email=%s,designation=%s
            WHERE id=%s AND is_deleted=0
        """, (name, email, designation, id))

        mysql.connection.commit()
        return redirect(url_for('teachers'))

    cur.execute("""
        SELECT id,name,email,designation
        FROM teachers
        WHERE id=%s AND is_deleted=0
    """, (id,))
    teacher = cur.fetchone()

    return render_template("edit_teacher.html", teacher=teacher)

@app.route('/delete_teacher/<int:id>')
@login_required
def delete_teacher(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE teachers
        SET is_deleted=1
        WHERE id=%s
    """, (id,))
    mysql.connection.commit()
    return redirect(url_for('teachers'))

# ================= COURSES ================= #

@app.route('/courses')
@login_required
def courses():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM courses WHERE is_deleted=0")
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT id,course_name,duration
        FROM courses
        WHERE is_deleted=0
        LIMIT %s OFFSET %s
    """, (per_page, offset))

    data = cur.fetchall()
    total_pages = math.ceil(total / per_page)

    return render_template("courses.html",
                           courses=data,
                           page=page,
                           total_pages=total_pages)

@app.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        duration = request.form['duration']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO courses(course_name,duration,is_deleted)
            VALUES(%s,%s,0)
        """, (course_name, duration))
        mysql.connection.commit()
        return redirect(url_for('courses'))

    return render_template("add_course.html")

@app.route('/edit_course/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        course_name = request.form['course_name']
        duration = request.form['duration']

        cur.execute("""
            UPDATE courses
            SET course_name=%s,duration=%s
            WHERE id=%s AND is_deleted=0
        """, (course_name, duration, id))

        mysql.connection.commit()
        return redirect(url_for('courses'))

    cur.execute("""
        SELECT id,course_name,duration
        FROM courses
        WHERE id=%s AND is_deleted=0
    """, (id,))
    course = cur.fetchone()

    return render_template("edit_course.html", course=course)

@app.route('/delete_course/<int:id>')
@login_required
def delete_course(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE courses
        SET is_deleted=1
        WHERE id=%s
    """, (id,))
    mysql.connection.commit()
    return redirect(url_for('courses'))

# ---------------- TEACHER COURSE ---------------- #

@app.route('/teacher_course', methods=['GET', 'POST'])
@login_required
def teacher_course():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        course_id = request.form['course_id']

        cur.execute("INSERT INTO teacher_course(teacher_id,course_id) VALUES(%s,%s)",
                    (teacher_id, course_id))
        mysql.connection.commit()

    cur.execute("SELECT * FROM teachers")
    teachers = cur.fetchall()

    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()

    cur.execute("""
        SELECT tc.id, t.name, t.designation, c.course_name
        FROM teacher_course tc
        JOIN teachers t ON tc.teacher_id = t.id
        JOIN courses c ON tc.course_id = c.id
    """)
    mappings = cur.fetchall()

    return render_template("teacher_course.html",
                           teachers=teachers,
                           courses=courses,
                           mappings=mappings)

@app.route('/delete_teacher_course/<int:id>')
@login_required
def delete_teacher_course(id):

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM teacher_course
        WHERE id=%s
    """, (id,))

    mysql.connection.commit()

    return redirect(url_for('teacher_course'))

# ---------------- STUDENT COURSE ---------------- #

@app.route('/student_course', methods=['GET', 'POST'])
@login_required
def student_course():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']

        cur.execute("INSERT INTO student_course(student_id,course_id) VALUES(%s,%s)",
                    (student_id, course_id))
        mysql.connection.commit()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()

    cur.execute("""
        SELECT sc.id, s.name, c.course_name
        FROM student_course sc
        JOIN students s ON sc.student_id = s.id
        JOIN courses c ON sc.course_id = c.id
    """)
    mappings = cur.fetchall()

    return render_template("student_course.html",
                           students=students,
                           courses=courses,
                           mappings=mappings)

@app.route('/delete_student_course/<int:id>')
@login_required
def delete_student_course(id):

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM student_course
        WHERE id=%s
    """, (id,))

    mysql.connection.commit()

    return redirect(url_for('student_course'))

# ================= RUN ================= #

if __name__ == "__main__":
    app.run(debug=True)



