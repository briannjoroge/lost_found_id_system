import os
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('lostfound.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            reg_number TEXT NOT NULL,
            department TEXT NOT NULL,
            image_path TEXT NOT NULL,
            date_reported TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS found_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_found TEXT NOT NULL,
            image_path TEXT NOT NULL,
            date_reported TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('lostfound.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_lost_ids(limit=8, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_name, reg_number, department, image_path, date_reported 
        FROM lost_ids 
        ORDER BY date_reported DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    records = cursor.fetchall()
    conn.close()

    return [dict(row) for row in records]

def get_found_ids(limit=8, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT location_found, image_path, date_reported 
        FROM found_ids 
        ORDER BY date_reported DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]

@app.route('/')
def home():
    lost_items = get_lost_ids(limit=4, offset=0)
    found_items = get_found_ids(limit=4, offset=0)
    return render_template(
        'index.html',
        lost_items=lost_items,
        found_items=found_items
    )

@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        student_name = request.form['student_name']
        reg_number = request.form['reg_number']
        department = request.form['department']
        image = request.files['id_image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            image.save(image_path)

            conn = sqlite3.connect('lostfound.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO lost_ids (student_name, reg_number, department, image_path, date_reported)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_name, reg_number, department, image_path, datetime.now()))
            conn.commit()
            conn.close()

        return redirect('/')

    return render_template('lost.html')

@app.route('/all-lost')
def all_lost():
    # grab the top 100 - will work on pagination later
    items = get_lost_ids(limit=100, offset=0)
    return render_template('view_all.html', items=items, title="All Lost Student IDs", type="Lost")

@app.route('/found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        location = request.form['location']
        image = request.files['id_image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            image.save(image_path)

            conn = sqlite3.connect('lostfound.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO found_ids (location_found, image_path, date_reported)
                VALUES (?, ?, ?)
            ''', (location, image_path, datetime.now()))
            conn.commit()
            conn.close()

        return redirect('/')

    return render_template('found.html')

@app.route('/all-found')
def all_found():
    items = get_found_ids(limit=100, offset=0)
    return render_template('view_all.html', items=items, title="All Found Student IDs", type="Found")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
