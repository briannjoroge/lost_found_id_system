import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from db import get_db_connection, get_lost_ids, get_found_ids

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def home():
    lost_items = get_lost_ids(limit=4, offset=0)
    found_items = get_found_ids(limit=4, offset=0)
    return render_template(
        'index.html',
        lost_items=lost_items,
        found_items=found_items
    )

@main_bp.route('/lost', methods=['GET', 'POST'])
@login_required
def lost():
    if request.method == 'POST':
        student_name = request.form['student_name']
        reg_number = request.form['reg_number']
        department = request.form['department']
        
        if 'id_image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        image = request.files['id_image']

        if image.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            image.save(image_path)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO lost_ids (student_name, reg_number, department, image_path, date_reported)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_name, reg_number, department, image_path, datetime.now()))
            conn.commit()
            conn.close()

            flash('Report submitted successfully!', 'success')
            return redirect('/')
        else:
            flash('Invalid file type! Please upload an image (JPG, JPEG, PNG).', 'error')
            return redirect(request.url)

    return render_template('lost.html')

@main_bp.route('/all-lost')
def all_lost():
    items = get_lost_ids(limit=100, offset=0)
    return render_template('view_all.html', items=items, title="All Lost Student IDs", type="Lost")

@main_bp.route('/found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        location = request.form['location']
        
        if 'id_image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        image = request.files['id_image']
        
        if image.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            image.save(image_path)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO found_ids (location_found, image_path, date_reported)
                VALUES (?, ?, ?)
            ''', (location, image_path, datetime.now()))
            conn.commit()
            conn.close()

            flash('Found ID reported successfully!', 'success')
            return redirect('/')
        else:
            flash('Invalid file type! Please upload an image (JPG, JPEG, PNG).', 'error')
            return redirect(request.url)

    return render_template('found.html')

@main_bp.route('/all-found')
def all_found():
    items = get_found_ids(limit=100, offset=0)
    return render_template('view_all.html', items=items, title="All Found Student IDs", type="Found")

@main_bp.route('/claim/<int:item_id>', methods=['POST'])
@login_required
def claim_item(item_id):
    conn = get_db_connection()
    
    item = conn.execute('SELECT * FROM found_ids WHERE id = ?', (item_id,)).fetchone()
    
    if not item:
        flash('Item not found.', 'error')
        conn.close()
        return redirect(url_for('main.all_found'))

    existing_claim = conn.execute(
        'SELECT * FROM claims WHERE found_id = ? AND user_id = ?',
        (item_id, current_user.id)
    ).fetchone()

    if existing_claim:
        flash('You have already submitted a claim for this item.', 'info')
        conn.close()
        return redirect(url_for('main.all_found'))

    conn.execute(
        'INSERT INTO claims (found_id, user_id, status) VALUES (?, ?, ?)',
        (item_id, current_user.id, 'Pending')
    )
    conn.commit()
    conn.close()

    flash('Claim submitted! Visit the admin office for verification.', 'success')
    return redirect(url_for('main.all_found'))