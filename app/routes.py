from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from app import db
from app.models import Workshop, Registration
from app.email_service import send_registration_email

main_bp = Blueprint('main', __name__)

@main_bp.route('/check_registration', methods=['POST'])
def check_registration():
    email = request.form.get('email', '').strip().lower()
    if not email:
        return jsonify({'exists': False})
    
    existing = Registration.query.filter_by(email=email).first()
    if not existing:
        return jsonify({'exists': False})
    
    workshop = Workshop.query.get(existing.workshop_id)
    return jsonify({
        'exists': True,
        'workshop_id': existing.workshop_id,
        'workshop_title': workshop.title_ar if session.get('lang') == 'ar' else workshop.title
    })

@main_bp.route('/register_ajax', methods=['POST'])
def register_ajax():
    lang = session.get('lang', 'en')
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    workshop_id = request.form.get('workshop_id')
    
    if not name or not email or not workshop_id:
        return jsonify({
            'success': False,
            'message': 'Please fill in all required fields.' if lang == 'en' else 'يرجى ملء جميع الحقول المطلوبة.'
        }), 400
        
    workshop = Workshop.query.get(workshop_id)
    if not workshop:
        return jsonify({
            'success': False,
            'message': 'Selected workshop does not exist.' if lang == 'en' else 'الورشة المحددة غير موجودة.'
        }), 404

    registered_email = session.get('registered_email')
    if registered_email and registered_email != email:
        return jsonify({
            'success': False,
            'message': 'You can only modify your own registration.' if lang == 'en' else 'يمكنك تعديل تسجيلك الخاص فقط.'
        }), 403

    existing_reg = Registration.query.filter_by(email=email).first()
    if existing_reg and registered_email != email:
        return jsonify({
            'success': False,
            'message': 'This email is already registered by another user.' if lang == 'en' else 'هذا البريد الإلكتروني مسجل بالفعل لمستخدم آخر.'
        }), 403
    
    def get_workshop_title(ws):
        if not ws:
            return 'Unknown Workshop' if lang == 'en' else 'ورشة غير معروفة'
        return ws.title if lang == 'en' else ws.title_ar

    is_update = False
    old_workshop_id = None
    old_workshop_title = None

    if existing_reg:
        old_workshop_id = existing_reg.workshop_id
        old_workshop = Workshop.query.get(old_workshop_id)
        old_workshop_title = get_workshop_title(old_workshop)

        if existing_reg.workshop_id == int(workshop_id):
            if existing_reg.name != name:
                existing_reg.name = name
                existing_reg.updated_at = datetime.utcnow()
                db.session.commit()
                send_registration_email(name, email, get_workshop_title(workshop), is_update=True)
                is_update = True
        else:
            existing_reg.name = name
            existing_reg.workshop_id = int(workshop_id)
            existing_reg.updated_at = datetime.utcnow()
            db.session.commit()
            send_registration_email(name, email, get_workshop_title(workshop), is_update=True)
            is_update = True
    else:
        reg = Registration(name=name, email=email, workshop_id=int(workshop_id))
        db.session.add(reg)
        db.session.commit()
        send_registration_email(name, email, get_workshop_title(workshop), is_update=False)

    # Calculate updated counts
    workshops = Workshop.query.all()
    updated_counts = {}
    for ws in workshops:
        updated_counts[ws.id] = Registration.query.filter_by(workshop_id=ws.id).count()
        
    total_registrations = Registration.query.count()
    
    # Format the updated_at or timestamp to show in registration board
    current_reg = Registration.query.filter_by(email=email).first()
    reg_time = current_reg.updated_at if current_reg.updated_at else current_reg.timestamp
    formatted_time = reg_time.strftime('%m/%d %H:%M')

    session['registered_email'] = email

    return jsonify({
        'success': True,
        'is_new': not is_update,
        'old_workshop_id': old_workshop_id if is_update and old_workshop_id != int(workshop_id) else None,
        'old_workshop_title': old_workshop_title if is_update and old_workshop_id != int(workshop_id) else None,
        'new_workshop_id': int(workshop_id),
        'new_workshop_title': get_workshop_title(workshop),
        'participant_name': name,
        'participant_email': email,
        'timestamp': formatted_time,
        'updated_counts': updated_counts,
        'total_registrations': total_registrations
    })

@main_bp.route('/cancel_registration', methods=['POST'])
def cancel_registration():
    lang = session.get('lang', 'en')
    email = request.form.get('email', '').strip().lower()
    if not email:
        return jsonify({
            'success': False,
            'message': 'Email is required.' if lang == 'en' else 'البريد الإلكتروني مطلوب.'
        }), 400
        
    reg = Registration.query.filter_by(email=email).first()
    if not reg:
        return jsonify({
            'success': False,
            'message': 'Registration not found.' if lang == 'en' else 'لم يتم العثور على التسجيل.'
        }), 404

    if session.get('registered_email') != email:
        return jsonify({
            'success': False,
            'message': 'You can only cancel your own registration.' if lang == 'en' else 'يمكنك إلغاء تسجيلك الخاص فقط.'
        }), 403
        
    workshop = Workshop.query.get(reg.workshop_id)
    workshop_title = workshop.title if lang == 'en' else workshop.title_ar
    
    db.session.delete(reg)
    db.session.commit()
    
    session['registered_email'] = None
    
    # Calculate updated counts
    workshops = Workshop.query.all()
    updated_counts = {}
    for ws in workshops:
        updated_counts[ws.id] = Registration.query.filter_by(workshop_id=ws.id).count()
        
    total_registrations = Registration.query.count()
    
    return jsonify({
        'success': True,
        'deleted_email': email,
        'deleted_workshop_id': workshop.id,
        'deleted_workshop_title': workshop_title,
        'updated_counts': updated_counts,
        'total_registrations': total_registrations
    })

@main_bp.route('/', methods=['GET', 'POST'])
def home():
    """Single page: Banner + Workshops list + Registration form."""
    workshops = Workshop.query.all()
    
    # Add participant count to each workshop
    for ws in workshops:
        ws.participant_count = Registration.query.filter_by(workshop_id=ws.id).count()
    
    total_registrations = Registration.query.count()
    
    # Language toggle
    lang = request.args.get('lang', session.get('lang', 'en'))
    session['lang'] = lang
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        workshop_id = request.form.get('workshop_id')
        
        if not name or not email or not workshop_id:
            flash(
                'Please fill in all required fields.' if lang == 'en' else 'يرجى ملء جميع الحقول المطلوبة.',
                'danger'
            )
            return redirect(url_for('main.home'))
        
        workshop = Workshop.query.get(workshop_id)
        if not workshop:
            flash(
                'Selected workshop does not exist.' if lang == 'en' else 'الورشة المحددة غير موجودة.',
                'danger'
            )
            return redirect(url_for('main.home'))

        registered_email = session.get('registered_email')
        if registered_email and registered_email != email:
            flash(
                'You can only modify your own registration.' if lang == 'en' else 'يمكنك تعديل تسجيلك الخاص فقط.',
                'danger'
            )
            return redirect(url_for('main.home'))
        
        existing_reg = Registration.query.filter_by(email=email).first()
        if existing_reg and registered_email != email:
            flash(
                'This email is already registered by another user.' if lang == 'en' else 'هذا البريد الإلكتروني مسجل بالفعل لمستخدم آخر.',
                'danger'
            )
            return redirect(url_for('main.home'))
        
        def get_workshop_title(ws):
            if not ws:
                return 'Unknown Workshop' if lang == 'en' else 'ورشة غير معروفة'
            return ws.title if lang == 'en' else ws.title_ar
        
        if existing_reg:
            if existing_reg.workshop_id == int(workshop_id):
                if existing_reg.name != name:
                    existing_reg.name = name
                    existing_reg.updated_at = datetime.utcnow()
                    db.session.commit()
                    send_registration_email(name, email, get_workshop_title(workshop), is_update=True)
                    flash(
                        f'Name updated to "{name}" for "{get_workshop_title(workshop)}".' if lang == 'en'
                        else f'تم تحديث الاسم إلى "{name}" في "{get_workshop_title(workshop)}".',
                        'info'
                    )
                else:
                    flash(
                        f'Already registered for "{get_workshop_title(workshop)}".' if lang == 'en'
                        else f'أنت مسجل بالفعل في "{get_workshop_title(workshop)}".',
                        'info'
                    )
                session['registered_email'] = email
                return redirect(url_for('main.home'))
            
            old_workshop = Workshop.query.get(existing_reg.workshop_id)
            old_title = get_workshop_title(old_workshop)
            
            existing_reg.name = name
            existing_reg.workshop_id = int(workshop_id)
            existing_reg.updated_at = datetime.utcnow()
            db.session.commit()
            
            send_registration_email(name, email, get_workshop_title(workshop), is_update=True)
            flash(
                f'Changed from "{old_title}" to "{get_workshop_title(workshop)}".' if lang == 'en'
                else f'تم التغيير من "{old_title}" إلى "{get_workshop_title(workshop)}".',
                'success'
            )
            session['registered_email'] = email
            return redirect(url_for('main.home'))
        
        else:
            reg = Registration(name=name, email=email, workshop_id=int(workshop_id))
            db.session.add(reg)
            db.session.commit()
            
            send_registration_email(name, email, get_workshop_title(workshop), is_update=False)
            flash(
                f'Successfully registered for "{get_workshop_title(workshop)}"!' if lang == 'en'
                else f'تم التسجيل بنجاح في "{get_workshop_title(workshop)}"!',
                'success'
            )
            session['registered_email'] = email
            return redirect(url_for('main.home'))
    
    registrations = Registration.query.order_by(Registration.timestamp.desc()).all()
    return render_template('home.html', 
                         workshops=workshops, 
                         total_registrations=total_registrations,
                         registrations=registrations,
                         lang=lang)

# -------------------------------------------------------------
#   ADMIN CONTROL PANEL ROUTES & DECORATORS
# -------------------------------------------------------------

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/admin/api'):
                return jsonify({'success': False, 'message': 'Admin login required.'}), 403
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    lang = session.get('lang', 'en')
    if session.get('is_admin'):
        return redirect(url_for('main.admin_dashboard'))
        
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password == current_app.config.get('ADMIN_PASSWORD', '123456'):
            session['is_admin'] = True
            flash('Logged in successfully as Admin.' if lang == 'en' else 'تم تسجيل الدخول كمشرف بنجاح.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Incorrect password.' if lang == 'en' else 'كلمة المرور غير صحيحة.', 'danger')
            
    return render_template('admin_login.html', lang=lang)

@main_bp.route('/admin/logout')
def admin_logout():
    lang = session.get('lang', 'en')
    session['is_admin'] = False
    flash('Logged out successfully.' if lang == 'en' else 'تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('main.home'))

@main_bp.route('/admin')
@main_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    lang = session.get('lang', 'en')
    workshops = Workshop.query.all()
    registrations = Registration.query.order_by(Registration.timestamp.desc()).all()
    
    total_regs = len(registrations)
    for ws in workshops:
        ws.participant_count = Registration.query.filter_by(workshop_id=ws.id).count()
        
    return render_template('admin_dashboard.html', 
                           workshops=workshops, 
                           registrations=registrations, 
                           total_registrations=total_regs, 
                           lang=lang)

@main_bp.route('/admin/api/add_participant', methods=['POST'])
@admin_required
def admin_add_participant():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    workshop_id = request.form.get('workshop_id')
    
    if not name or not email or not workshop_id:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
    workshop = Workshop.query.get(workshop_id)
    if not workshop:
        return jsonify({'success': False, 'message': 'Workshop does not exist.'}), 404
        
    existing = Registration.query.filter_by(email=email).first()
    if existing:
        return jsonify({'success': False, 'message': 'This email is already registered.'}), 400
        
    reg = Registration(name=name, email=email, workshop_id=int(workshop_id))
    db.session.add(reg)
    db.session.commit()
    
    reg_time = reg.updated_at if reg.updated_at else reg.timestamp
    formatted_time = reg_time.strftime('%m/%d %H:%M')
    
    workshops = Workshop.query.all()
    updated_counts = {ws.id: Registration.query.filter_by(workshop_id=ws.id).count() for ws in workshops}
    total_registrations = Registration.query.count()
    
    try:
        send_registration_email(name, email, workshop.title if session.get('lang') == 'en' else workshop.title_ar, is_update=False)
    except Exception:
        pass
        
    return jsonify({
        'success': True,
        'id': reg.id,
        'name': name,
        'email': email,
        'workshop_id': int(workshop_id),
        'workshop_title': workshop.title_ar if session.get('lang') == 'ar' else workshop.title,
        'timestamp': formatted_time,
        'updated_counts': updated_counts,
        'total_registrations': total_registrations
    })

@main_bp.route('/admin/api/edit_participant', methods=['POST'])
@admin_required
def admin_edit_participant():
    reg_id = request.form.get('id')
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    workshop_id = request.form.get('workshop_id')
    
    if not reg_id or not name or not email or not workshop_id:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
    reg = Registration.query.get(reg_id)
    if not reg:
        return jsonify({'success': False, 'message': 'Registration not found.'}), 404
        
    existing = Registration.query.filter(Registration.email == email, Registration.id != reg_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'This email is already registered by another user.'}), 400
        
    workshop = Workshop.query.get(workshop_id)
    if not workshop:
        return jsonify({'success': False, 'message': 'Workshop does not exist.'}), 404
        
    old_workshop_id = reg.workshop_id
    old_workshop = Workshop.query.get(old_workshop_id)
    old_workshop_title = old_workshop.title_ar if session.get('lang') == 'ar' else old_workshop.title
    
    is_workshop_changed = (old_workshop_id != int(workshop_id))
    
    reg.name = name
    reg.email = email
    reg.workshop_id = int(workshop_id)
    reg.updated_at = datetime.utcnow()
    db.session.commit()
    
    reg_time = reg.updated_at if reg.updated_at else reg.timestamp
    formatted_time = reg_time.strftime('%m/%d %H:%M')
    
    workshops = Workshop.query.all()
    updated_counts = {ws.id: Registration.query.filter_by(workshop_id=ws.id).count() for ws in workshops}
    total_registrations = Registration.query.count()
    
    try:
        send_registration_email(name, email, workshop.title if session.get('lang') == 'en' else workshop.title_ar, is_update=True)
    except Exception:
        pass
        
    return jsonify({
        'success': True,
        'id': reg.id,
        'name': name,
        'email': email,
        'old_workshop_id': old_workshop_id if is_workshop_changed else None,
        'old_workshop_title': old_workshop_title if is_workshop_changed else None,
        'workshop_id': int(workshop_id),
        'workshop_title': workshop.title_ar if session.get('lang') == 'ar' else workshop.title,
        'timestamp': formatted_time,
        'updated_counts': updated_counts,
        'total_registrations': total_registrations
    })

@main_bp.route('/admin/api/delete_participant', methods=['POST'])
@admin_required
def admin_delete_participant():
    reg_id = request.form.get('id')
    if not reg_id:
        return jsonify({'success': False, 'message': 'ID is required.'}), 400
        
    reg = Registration.query.get(reg_id)
    if not reg:
        return jsonify({'success': False, 'message': 'Registration not found.'}), 404
        
    workshop_id = reg.workshop_id
    db.session.delete(reg)
    db.session.commit()
    
    workshops = Workshop.query.all()
    updated_counts = {ws.id: Registration.query.filter_by(workshop_id=ws.id).count() for ws in workshops}
    total_registrations = Registration.query.count()
    
    return jsonify({
        'success': True,
        'deleted_id': int(reg_id),
        'deleted_workshop_id': workshop_id,
        'updated_counts': updated_counts,
        'total_registrations': total_registrations
    })

@main_bp.route('/admin/api/edit_workshop', methods=['POST'])
@admin_required
def admin_edit_workshop():
    ws_id = request.form.get('id')
    title = request.form.get('title', '').strip()
    title_ar = request.form.get('title_ar', '').strip()
    instructor = request.form.get('instructor', '').strip()
    description = request.form.get('description', '').strip()
    description_ar = request.form.get('description_ar', '').strip()
    tech_stack = request.form.get('tech_stack', '').strip()
    
    if not ws_id or not title or not title_ar or not instructor or not description or not description_ar:
        return jsonify({'success': False, 'message': 'All fields except tech stack are required.'}), 400
        
    ws = Workshop.query.get(ws_id)
    if not ws:
        return jsonify({'success': False, 'message': 'Workshop not found.'}), 404
        
    ws.title = title
    ws.title_ar = title_ar
    ws.instructor = instructor
    ws.description = description
    ws.description_ar = description_ar
    ws.tech_stack = tech_stack
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': ws.id,
        'title': title,
        'title_ar': title_ar,
        'instructor': instructor,
        'description': description,
        'description_ar': description_ar,
        'tech_stack': tech_stack
    })