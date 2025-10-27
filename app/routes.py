import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app import db
from app.models import Participant, Match, Settings

main = Blueprint('main', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        gift_preference = request.form.get('gift_preference')

        # Check if email already exists
        existing = Participant.query.filter_by(email=email).first()
        if existing:
            flash('This email is already registered!', 'error')
            return redirect(url_for('main.register'))

        # Create new participant
        participant = Participant(
            name=name,
            email=email,
            gift_preference=gift_preference
        )
        db.session.add(participant)
        db.session.commit()

        flash('Registration successful! You will receive an email with your Secret Santa match.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')


@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == current_app.config['ADMIN_PASSWORD']:
            session['admin_authenticated'] = True
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid password', 'error')

    return render_template('admin_login.html')


@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('main.index'))


@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    participants = Participant.query.all()
    matches = Match.query.all()
    matches_created = len(matches) > 0

    return render_template('admin_dashboard.html',
                         participants=participants,
                         matches=matches,
                         matches_created=matches_created)


@main.route('/admin/create-matches', methods=['POST'])
@admin_required
def create_matches():
    # Check if matches already exist
    existing_matches = Match.query.first()
    if existing_matches:
        flash('Matches have already been created!', 'error')
        return redirect(url_for('main.admin_dashboard'))

    participants = Participant.query.all()

    if len(participants) < 2:
        flash('Need at least 2 participants to create matches!', 'error')
        return redirect(url_for('main.admin_dashboard'))

    # Create Secret Santa matches
    givers = participants.copy()
    receivers = participants.copy()

    # Shuffle until no one gets themselves
    max_attempts = 100
    for attempt in range(max_attempts):
        random.shuffle(receivers)

        # Check if valid (no one gets themselves)
        valid = all(givers[i].id != receivers[i].id for i in range(len(givers)))

        if valid:
            break
    else:
        flash('Could not create valid matches. Try again!', 'error')
        return redirect(url_for('main.admin_dashboard'))

    # Create match records
    for i in range(len(givers)):
        match = Match(
            giver_id=givers[i].id,
            receiver_id=receivers[i].id
        )
        db.session.add(match)

    db.session.commit()
    flash(f'Successfully created {len(givers)} Secret Santa matches!', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/send-emails', methods=['POST'])
@admin_required
def send_emails():
    matches = Match.query.filter_by(email_sent=False).all()

    if not matches:
        flash('All emails have already been sent!', 'info')
        return redirect(url_for('main.admin_dashboard'))

    sent_count = 0
    error_count = 0
    first_error = None

    for match in matches:
        try:
            giver = match.giver
            receiver = match.receiver

            # Create email
            msg = MIMEMultipart()
            msg['From'] = current_app.config['FROM_EMAIL']
            msg['To'] = giver.email
            msg['Subject'] = 'Your Secret Santa Match!'

            body = f"""
Hello {giver.name}!

You are the Secret Santa for: {receiver.name}

Their gift preference/suggestion: {receiver.gift_preference or 'No preference specified'}

Happy gifting!

Best regards,
Secret Santa Bot
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(current_app.config['SMTP_SERVER'], current_app.config['SMTP_PORT']) as server:
                server.starttls()
                server.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])
                server.send_message(msg)

            # Mark as sent
            match.email_sent = True
            db.session.commit()
            sent_count += 1

        except Exception as e:
            error_count += 1
            error_msg = str(e)
            print(f"Error sending email to {giver.email}: {error_msg}")

            # Store first error for user feedback
            if not first_error:
                if 'Name or service not known' in error_msg:
                    first_error = f"Cannot resolve SMTP server hostname. Check SMTP_SERVER in .env"
                elif 'Authentication failed' in error_msg or 'Invalid credentials' in error_msg:
                    first_error = f"SMTP authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD in .env"
                elif 'Connection refused' in error_msg:
                    first_error = f"Connection refused. Check SMTP_SERVER and SMTP_PORT in .env"
                elif 'timed out' in error_msg:
                    first_error = f"Connection timeout. Check network/firewall settings"
                else:
                    first_error = f"Error: {error_msg}"

    if sent_count > 0:
        flash(f'Successfully sent {sent_count} emails!', 'success')
    if error_count > 0:
        flash(f'Failed to send {error_count} emails. {first_error}', 'error')

    return redirect(url_for('main.admin_dashboard'))


@main.route('/reveal')
@admin_required
def reveal():
    matches = Match.query.all()
    match_list = []

    for match in matches:
        match_list.append({
            'id': match.id,
            'giver': match.giver.name,
            'receiver': match.receiver.name,
            'revealed': match.revealed
        })

    return render_template('reveal.html', matches=match_list)


@main.route('/reveal/toggle/<int:match_id>', methods=['POST'])
@admin_required
def toggle_reveal(match_id):
    match = Match.query.get_or_404(match_id)
    match.revealed = not match.revealed
    db.session.commit()
    return redirect(url_for('main.reveal'))


@main.route('/admin/delete-participant/<int:participant_id>', methods=['POST'])
@admin_required
def delete_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)

    # Check if matches exist
    if Match.query.first():
        flash('Cannot delete participants after matches have been created!', 'error')
        return redirect(url_for('main.admin_dashboard'))

    db.session.delete(participant)
    db.session.commit()
    flash(f'Deleted participant: {participant.name}', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/reset-all', methods=['POST'])
@admin_required
def reset_all():
    # Delete all matches and participants
    Match.query.delete()
    Participant.query.delete()
    Settings.query.delete()
    db.session.commit()

    flash('All data has been reset!', 'success')
    return redirect(url_for('main.admin_dashboard'))
