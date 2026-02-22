import os
import uuid
from utils import extract_id_info
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from db import get_db_connection, get_lost_ids, get_found_ids
from auth import admin_required

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

            date_reported_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO lost_ids (user_id, student_name, reg_number, department, image_path, date_reported)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (current_user.id, student_name, reg_number, department, image_path, date_reported_str))
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

            print(f"Processing image for OCR: {image_path}")
            ai_data = extract_id_info(image_path)
            
            extracted_name = None
            extracted_reg = None
            extracted_dept = None
            extracted_phone = None
            
            if ai_data:
                extracted_name = ai_data.get('student_name') 
                extracted_reg = ai_data.get('reg_number')
                extracted_dept = ai_data.get('department')
                extracted_phone = ai_data.get('phone_number')
                print(f"AI Results: {ai_data}")

            date_found = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            finder_id = current_user.id if current_user.is_authenticated else None

            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO found_ids (
                    user_id, location_found, image_path, date_reported, status,
                    extracted_name, extracted_reg_number, extracted_department, extracted_phone
                )
                VALUES (?, ?, ?, ?, 'Unclaimed', ?, ?, ?, ?)
            ''', (finder_id, location, image_path, date_found, 
                  extracted_name, extracted_reg, extracted_dept, extracted_phone))
            
            conn.commit()
            conn.close()

            flash('Found ID reported successfully!', 'success')
            return redirect('/')
        else:
            flash('Invalid file type! Please upload an image (JPG, JPEG, PNG).', 'error')
            return redirect(request.url)
        
    conn = get_db_connection()
    found_items = conn.execute('''
        SELECT * FROM found_ids 
        WHERE status = 'Unclaimed' 
        ORDER BY date_reported DESC
    ''').fetchall()
    conn.close()

    return render_template('found.html', found_items=found_items)

@main_bp.route('/all-found')
def all_found():
    items = get_found_ids(limit=100, offset=0)

    return render_template('view_all.html', items=items, title="All Found Student IDs", type="Found")

@main_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    
    my_lost_items = conn.execute('''
        SELECT * FROM lost_ids 
        WHERE user_id = ? 
        ORDER BY date_reported DESC
    ''', (current_user.id,)).fetchall()
    
    my_claims = conn.execute('''
        SELECT 
            claims.id as claim_id,
            claims.status as claim_status,
            claims.date_claimed,
            found_ids.image_path,
            found_ids.location_found
        FROM claims
        JOIN found_ids ON claims.found_id = found_ids.id
        WHERE claims.user_id = ?
        ORDER BY claims.date_claimed DESC
    ''', (current_user.id,)).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         my_lost_items=my_lost_items, 
                         my_claims=my_claims)

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

# --- ADMIN Routes ---
@main_bp.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    total_lost = conn.execute('SELECT COUNT(*) FROM lost_ids').fetchone()[0]
    total_found = conn.execute('SELECT COUNT(*) FROM found_ids').fetchone()[0]
    pending_claims = conn.execute('SELECT COUNT(*) FROM claims WHERE status = "Pending"').fetchone()[0]

    recent_claims = conn.execute('''
        SELECT 
            claims.id as claim_id,
            users.name as student_name,
            found_ids.image_path,
            claims.date_claimed
        FROM claims
        JOIN users ON claims.user_id = users.id
        JOIN found_ids ON claims.found_id = found_ids.id
        WHERE claims.status = 'Pending'
        ORDER BY claims.date_claimed DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                           total_lost=total_lost, 
                           total_found=total_found, 
                           pending_claims=pending_claims,
                           recent_claims=recent_claims)

# --- ADMIN CLAIMS MANAGEMENT ---
@main_bp.route('/admin/claims')
@admin_required
def admin_claims():
    conn = get_db_connection()
    
    claims = conn.execute('''
        SELECT 
            claims.id as claim_id,
            claims.status as claim_status,
            claims.date_claimed,
            users.name as student_name,
            users.reg_number,
            users.phone,
            users.department,
            found_ids.image_path,
            found_ids.location_found
        FROM claims
        JOIN users ON claims.user_id = users.id
        JOIN found_ids ON claims.found_id = found_ids.id
        ORDER BY 
            CASE WHEN claims.status = 'Pending' THEN 0 ELSE 1 END,
            claims.date_claimed DESC
    ''').fetchall()

    pending_claims = conn.execute('SELECT COUNT(*) FROM claims WHERE status = "Pending"').fetchone()[0]
    
    conn.close()
    return render_template('admin/claims.html', claims=claims, pending_claims=pending_claims)

@main_bp.route('/admin/claim/approve/<int:claim_id>', methods=['POST'])
@admin_required
def approve_claim(claim_id):
    conn = get_db_connection()
    
    claim = conn.execute('SELECT found_id, user_id FROM claims WHERE id = ?', (claim_id,)).fetchone()
    
    found_id = claim['found_id']
    user_id = claim['user_id']  

    conn.execute('UPDATE claims SET status = "Approved" WHERE id = ?', (claim_id,))
    
    conn.execute('''
        UPDATE found_ids 
        SET status = "Returned", claimed_by_user_id = ? 
        WHERE id = ?
    ''', (user_id, found_id))

    conn.execute('UPDATE lost_ids SET status = "Found" WHERE user_id = ?', (user_id,))
    
    conn.execute('UPDATE claims SET status = "Rejected" WHERE found_id = ? AND id != ?', (found_id, claim_id))
    
    conn.commit()
    conn.close()
    
    flash('Claim approved! Item returned and user\'s lost report closed.', 'success')
    return redirect(url_for('main.admin_claims'))

@main_bp.route('/admin/claim/reject/<int:claim_id>', methods=['POST'])
@admin_required
def reject_claim(claim_id):
    conn = get_db_connection()
    conn.execute('UPDATE claims SET status = "Rejected" WHERE id = ?', (claim_id,))
    conn.commit()
    conn.close()
    flash('Claim rejected.', 'error')
    return redirect(url_for('main.admin_claims'))

# --- MANAGE ITEMS ---
@main_bp.route('/admin/items')
@admin_required
def admin_items():
    conn = get_db_connection()
    
    lost_items = conn.execute('SELECT *, "Lost" as type FROM lost_ids ORDER BY date_reported DESC').fetchall()
    
    found_items = conn.execute('SELECT *, "Found" as type FROM found_ids ORDER BY date_reported DESC').fetchall()

    pending_claims = conn.execute('SELECT COUNT(*) FROM claims WHERE status = "Pending"').fetchone()[0]
    
    conn.close()
    
    return render_template('admin/items.html', lost_items=lost_items, found_items=found_items, pending_claims=pending_claims)

@main_bp.route('/admin/items/delete/<string:item_type>/<int:item_id>', methods=['POST'])
@admin_required
def delete_item(item_type, item_id):
    conn = get_db_connection()
    
    if item_type == 'Lost':
        conn.execute('DELETE FROM lost_ids WHERE id = ?', (item_id,))
    elif item_type == 'Found':

        conn.execute('DELETE FROM claims WHERE found_id = ?', (item_id,))
        conn.execute('DELETE FROM found_ids WHERE id = ?', (item_id,))
        
    conn.commit()
    conn.close()
    
    flash('Item deleted successfully.', 'success')

    return redirect(url_for('main.admin_items'))

# --- MANAGE USERS ---
@main_bp.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()

    users = conn.execute('SELECT * FROM users WHERE role != "admin" ORDER BY is_deleted ASC, name ASC').fetchall()

    pending_claims = conn.execute('SELECT COUNT(*) FROM claims WHERE status = "Pending"').fetchone()[0]

    conn.close()

    return render_template('admin/users.html', users=users, pending_claims=pending_claims)

@main_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        conn.execute('UPDATE users SET is_deleted = 1 WHERE id = ?', (user_id,))
        conn.commit()
        
        flash(f'User "{user["name"]}" has been deactivated.', 'success')
    else:
        flash('User not found.', 'error')
        
    conn.close()
    return redirect(url_for('main.admin_users'))

@main_bp.route('/admin/users/restore/<int:user_id>', methods=['POST'])
@admin_required
def restore_user(user_id):
    conn = get_db_connection()
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        conn.execute('UPDATE users SET is_deleted = 0 WHERE id = ?', (user_id,))
        conn.commit()
        flash(f'User "{user["name"]}" has been restored.', 'success')
    else:
        flash('User not found.', 'error')
        
    conn.close()
    return redirect(url_for('main.admin_users'))

# --- ERROR HANDLERS ---
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
