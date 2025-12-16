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

def get_lost_ids():
    conn = sqlite3.connect('lostfound.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_name, reg_number, department, image_path, date_reported
        FROM lost_ids
        ORDER BY date_reported DESC
    """)

    records = cursor.fetchall()
    conn.close()
    return records


def get_found_ids():
    conn = sqlite3.connect('lostfound.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT location_found, image_path, date_reported
        FROM found_ids
        ORDER BY date_reported DESC
    """)

    records = cursor.fetchall()
    conn.close()
    return records


@app.route('/')
def home():
    lost_items = get_lost_ids()
    found_items = get_found_ids()
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



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
