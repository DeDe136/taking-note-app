from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from flask import jsonify
import time

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')
            # Redirect sau khi tạo note thành công để tránh lỗi refresh
            return redirect(url_for('views.home'))

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@views.route('/heavy')
@login_required # Yêu cầu đăng nhập để tránh lạm dụng
def heavy_task():
    """
    Route tạm thời để mô phỏng tác vụ tốn CPU cho việc test Auto Scaling.
    """
    start_time = time.time()
    count = 0
    # Chạy vòng lặp trong khoảng 1.0 giây (có thể điều chỉnh)
    while (time.time() - start_time) < 1.0: 
        count += 1
        # Thực hiện phép tính đơn giản lặp đi lặp lại
        # result = count * count / (count + 1) # Có thể thêm nếu cần nặng hơn

    print(f"Heavy task completed {count} iterations.") # In ra log để biết nó chạy
    return jsonify({"message": f"Heavy task completed after {count} iterations."}), 200