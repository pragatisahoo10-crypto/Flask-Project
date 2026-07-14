from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


app = Flask(__name__)
app.secret_key = "secret123"

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Root',
        database='employee_management_db',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

#======= Login =======

@app.route("/", methods=["GET","POST"])
def login():

    if "admin" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = username
            flash("Login Successful!")
            return redirect(url_for("dashboard"))

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM login WHERE username=%s", (username,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            if check_password_hash(user["password"], password):
                session["admin"] = username
                flash("Login Successful!")
                return redirect(url_for("dashboard"))
            
        flash("Invalid Username or Password")

    return render_template("login.html")


#======== Logout =========

@app.route("/logout")
def logout():
    session.clear()

    flash("Logged out successfully!")

    return redirect(url_for("login"))

#========= Dashboard ==========

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM employee")
    
    total_employees = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM attendance WHERE attendance_date=%s AND status=%s",
                (str(datetime.now().date()), "Present"))
    present_today = cur.fetchone()

    cur.execute(
        "SELECT COUNT(*) FROM payroll WHERE status=%s",
        ("paid",)
    )
    paid_salary = cur.fetchone()

    cur.execute(" SELECT COUNT(*) FROM payroll WHERE status='Pending' ",)
    pending_salary = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("dashboard.html", total_employees=total_employees, present_today=present_today, paid_salary=paid_salary, pending_salary=pending_salary)

#========== Employee Details ===========

@app.route("/employees")
def employees():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM employee ORDER BY id DESC")
    
    employee_list = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("employees.html", employees=employee_list)

#========== Add ==========

@app.route("/add_employee", methods=["GET","POST"])
def add_employee():
    if "admin" not in session:
        return redirect(url_for("login"))
    
    conn = get_connection()
    cur = conn.cursor()
    
    if request.method == "POST":
        cur.execute("INSERT INTO employee ( emp_code, name, email, department, designation, joining_date, basic_salary ) VALUES (%s,%s,%s,%s,%s,%s,%s) ",
                    (request.form["emp_code"], request.form["name"], request.form["email"], request.form["department"], request.form["designation"], request.form["joining_date"], request.form["basic_salary"] ))

        conn.commit()
        cur.close()
        conn.close()

        flash("Employee added!")

        return redirect(url_for("employees"))
    
    return render_template("add_employee.html")

#=========== Edit ===========

@app.route("/edit_employee/<int:id>", methods=["GET","POST"])
def edit_employee(id):

    if "admin" not in session:
        return redirect(url_for("login"))
    
    conn = get_connection()
    cur = conn.cursor()
    
    if request.method == "POST":
        cur.execute("UPDATE employee SET emp_code=%s, name=%s, email=%s, department=%s, designation=%s, joining_date=%s, basic_salary=%s WHERE id=%s", 
                    (request.form["emp_code"], request.form["name"], request.form["email"], request.form["department"], request.form["designation"], request.form["joining_date"], request.form["basic_salary"], id ))

        conn.commit()
        cur.close()
        conn.close()

        flash("Employee Updated")

        return redirect(url_for("employees"))
    
    cur.execute("SELECT * FROM employee WHERE id=%s", (id,) ) 
    employee = cur.fetchone() 
    cur.close()
    conn.close()

    if employee is None:
        flash("Employee not found")
        return redirect(url_for("employees"))
    
    return render_template("edit_employee.html", employee=employee)

#=========== Delete ==========

@app.route("/delete_employee/<int:id>", methods=["GET","POST"])
def delete_employee(id):

    if "admin" not in session:
        return redirect(url_for("login"))
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM employee WHERE id=%s", (id,) )
    conn.commit()
    cur.close()
    conn.close()

    flash("Employee deleted.")

    return redirect(url_for("employees"))

#========= Attendance =========

@app.route("/attendance", methods=["GET","POST"])
def attendance():

    if "admin" not in session:
        return redirect(url_for("login"))
    
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        employee_id = request.form["employee_id"]
        status = request.form["status"]

        cur.execute("SELECT id FROM attendance WHERE employee_id=%s AND attendance_date=%s",
                    (employee_id, date.today()))
        
        existing = cur.fetchone()

        if existing:
            flash("Attendance already marked for today.")
        else:
            cur.execute("INSERT INTO attendance ( employee_id, attendance_date, status ) VALUES (%s,%s,%s) ", (employee_id, date.today(), status ))
        conn.commit()

        flash("Attendace saved.")

        return redirect(url_for("attendance"))
    
    cur.execute("SELECT * FROM employee") 
    employees = cur.fetchall()

    cur.execute("SELECT a.*, e.name FROM attendance a JOIN employee e ON a.employee_id=e.id ")

    attendance_records = cur.fetchall() 
    cur.close()
    conn.close()

    return render_template("attendance.html", employees=employees, attendance_records=attendance_records)

#========== Payroll ===========

@app.route("/payroll", methods=["GET","POST"])
def payroll():

    if "admin" not in session: 
        return redirect(url_for("login")) 
    
    conn = get_connection()
    cur = conn.cursor() 

    if request.method == "POST": 
        employee_id = int(request.form["employee_id"]) 

        cur.execute("SELECT basic_salary FROM employee WHERE id=%s", (employee_id,) ) 
        employee = cur.fetchone() 

        if employee is None:
            flash("Employee not found")

            cur.close()
            conn.close()

            return redirect(url_for("payroll"))
        
        basic_salary = float(employee["basic_salary"]) 
        bonus = float(request.form["bonus"]) 
        deduction = float(request.form["deduction"]) 

        net_salary = basic_salary + bonus - deduction 

        cur.execute("INSERT INTO payroll ( employee_id, pay_month, bonus, deduction, net_salary, status ) VALUES (%s,%s,%s,%s,%s,%s) ",
                (employee_id, request.form["month"], bonus, deduction, net_salary, request.form["status"] )) 
        
        conn.commit() 

        flash("Payroll Generated", "success") 

        cur.close()
        conn.close()

        return redirect(url_for("payroll")) 
    
    cur.execute("SELECT * FROM employee ORDER BY name")

    employees = cur.fetchall() 

    cur.execute("SELECT p.*, e.name FROM payroll p JOIN employee e ON p.employee_id = e.id ORDER BY p.id DESC ") 

    payroll_records = cur.fetchall() 

    cur.close()
    conn.close()

    return render_template("payroll.html", payroll_records=payroll_records)



if __name__ == "__main__":
    app.run(debug=True)

     
