# auth.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import random # <-- 1. Thêm dòng này

auth = Blueprint('auth', __name__)

# 2. Tạo một danh sách các màu nền của Bootstrap
BG_COLORS = ["bg-primary", "bg-success", "bg-danger", "bg-info", "bg-warning", "bg-secondary"]

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ... (giữ nguyên logic xử lý POST) ...
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    # 3. Chọn một màu ngẫu nhiên
    random_color = random.choice(BG_COLORS)
    
    # 4. Truyền biến màu vào template
    return render_template("login.html", user=current_user, nav_color=random_color)


# ... (route logout giữ nguyên) ...


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # ... (giữ nguyên logic xử lý POST) ...
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    
    # 3. Chọn một màu ngẫu nhiên
    random_color = random.choice(BG_COLORS)
    
    # 4. Truyền biến màu vào template
    return render_template("sign_up.html", user=current_user, nav_color=random_color)

@auth.route('/logout')
@login_required # Đảm bảo chỉ người đã đăng nhập mới logout được
def logout():
    logout_user() # Xóa session của người dùng
    flash('You have been logged out.', category='success') # Thông báo (tùy chọn)
    return redirect(url_for('auth.login')) # Chuyển về trang đăng nhập