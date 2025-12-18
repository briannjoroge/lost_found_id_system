from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role

def load_user(user_id):
    conn = get_db_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = curr.fetchone()
    conn.close()
    if user:
        return User(id=user['id'], name=user['name'], email=user['email'], role=user['role'])
    return None

# --- Routes ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        reg_number = request.form['reg_number'] 
        department = request.form['department']
        password = request.form['password']
        
        conn = get_db_connection()
        
        existing_user = conn.execute(
            'SELECT * FROM users WHERE email = ? OR reg_number = ?', 
            (email, reg_number)
        ).fetchone()
        
        if existing_user:
            if existing_user['email'] == email:
                flash('That email is already registered. Please log in.', 'error')
            elif existing_user['reg_number'] == reg_number:
                flash('That Registration Number is already in use.', 'error')
            conn.close()
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password, method='scrypt')
        
        conn.execute(
            'INSERT INTO users (name, email, phone, reg_number, department, password_hash) VALUES (?, ?, ?, ?, ?, ?)',
            (name, email, phone, reg_number, department, hashed_password)
        )
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('action') 

        # --- ACTION 1: UPDATE INFO ---
        if action == 'update_info':
            new_name = request.form['name']
            new_phone = request.form['phone']
            
            conn.execute('UPDATE users SET name = ?, phone = ? WHERE id = ?', 
                         (new_name, new_phone, current_user.id))
            conn.commit()
            
            current_user.name = new_name
            flash('Profile details updated successfully!', 'success')

            conn.close()
            return redirect(url_for('main.home'))
        
        # --- ACTION 2: CHANGE PASSWORD ---
        elif action == 'change_password':
            old_pass = request.form['old_password']
            new_pass = request.form['new_password']
            confirm_pass = request.form['confirm_password']
            
            user_data = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
            
            if not check_password_hash(user_data['password_hash'], old_pass):
                flash('Incorrect old password.', 'error')
            elif new_pass != confirm_pass:
                flash('New passwords do not match.', 'error')
            else:
                new_hash = generate_password_hash(new_pass, method='scrypt')
                conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                             (new_hash, current_user.id))
                conn.commit()
                flash('Password changed successfully!', 'success')

                conn.close()
                return redirect(url_for('main.home'))

    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    conn.close()
    
    return render_template('profile.html', user=user_data)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):            
            user_obj = User(id=user['id'], name=user['name'], email=user['email'], role=user['role'])
            login_user(user_obj)
            
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Login failed. Check your email and password.', 'error')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required 
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))