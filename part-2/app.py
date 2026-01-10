"""
Part 2: Full CRUD Operations with HTML Forms
=============================================
Complete Create, Read, Update, Delete operations with user forms.

What You'll Learn:
- HTML forms with POST method
- request.form to get form data
- UPDATE and DELETE SQL commands
- redirect() and url_for() functions
- Flash messages for user feedback

Prerequisites: Complete part-1 first
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

DATABASE = 'part2-students.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# =============================================================================
# CREATE - Add new student
# =============================================================================

@app.route('/add', methods=['GET', 'POST'])  # Allow both GET and POST
def add_student():
    if request.method == 'POST':  # Form was submitted
        name = request.form['name']  # Get data from form field named 'name'
        email = request.form['email']
        course = request.form['course']

        conn = get_db_connection()
        existing_email = conn.execute("SELECT * FROM students WHERE email = ?",(email,)).fetchone()
        if existing_email:
            return render_template( 'add.html', error="Email already exists!",name=name,email=email,course=course)
        conn.execute(
            'INSERT INTO students (name, email, course) VALUES (?, ?, ?)',
            (name, email, course)
        )
        conn.commit()
        conn.close()

        flash('Student added successfully!', 'success')  # Show success message
        return redirect(url_for('index'))  # Go back to home page

    return render_template('add.html')  # GET request: show empty form


# =============================================================================
# READ - Display all students
# =============================================================================

@app.route('/', methods=['GET'])
def index():
    search = request.args.get('search')  # gets ?search=value from URL
    conn = get_db_connection()

    if search:
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ? ORDER BY id ASC",
            (f"%{search}%",)
        ).fetchall()
    else:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id ASC"
        ).fetchall()

    conn.close()
    return render_template('index.html', students=students)



# =============================================================================
# UPDATE - Edit existing student
# =============================================================================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()

    if request.method == 'POST':  # Form submitted with new data
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn.execute(
            'UPDATE students SET name = ?, email = ?, course = ? WHERE id = ?',
            (name, email, course, id)  # Update WHERE id matches
        )
        conn.commit()
        conn.close()

        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))

    # GET request: fetch current data and show in form
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit.html', student=student)


# =============================================================================
# DELETE - Remove student
# =============================================================================

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))  # Remove row
    conn.commit()
    conn.close()

    flash('Student deleted!', 'danger')  # Show delete message
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


#when i run the code 126-127-31-32-25-26-22-27-28-32-33to38-41-42-127-128
#when user vist home page 74-75-76-25to42-76-77-78-78
#when user clicks add student =true then 49-50-51-51-53-54-56-31-25-56to62-64-65 goes back to home page
#edit 86-87-88-31-25-88-91-92=93-95-96--97-99-100-102-103 goes to home page
#delete 115-116-117-31-25-117-118-119-120-122-123 - goes back to home page


# =============================================================================
# CRUD SUMMARY:
# =============================================================================
#
# Operation | HTTP Method | SQL Command | Route Example
# ----------|-------------|-------------|---------------
# Create    | POST        | INSERT INTO | /add
# Read      | GET         | SELECT      | / or /student/1
# Update    | POST        | UPDATE      | /edit/1
# Delete    | GET/POST    | DELETE      | /delete/1
#
# =============================================================================
# NEW CONCEPTS:
# =============================================================================
#
# 1. methods=['GET', 'POST']
#    - GET: Display the form (empty or with current data)
#    - POST: Process the submitted form
#
# 2. request.form['field_name']
#    - Gets the value from HTML form input with that name
#
# 3. redirect(url_for('function_name'))
#    - Sends user to another page after action completes
#
# 4. flash('message', 'category')
#    - Shows one-time message to user
#    - Categories: 'success', 'danger', 'warning', 'info'
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Add a "Search" feature to find students by name
# 2. Add validation to check if email already exists before adding
#
# =============================================================================
