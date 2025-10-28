import logging
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

from email_validator import EmailNotValidError, validate_email
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from app import db, limiter
from app.models import Match, Participant, Settings

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("main.admin_login"))
        return f(*args, **kwargs)

    return decorated_function


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if registration is locked (emails have been sent)
        any_emails_sent = Match.query.filter_by(email_sent=True).first()
        if any_emails_sent:
            flash("Registration is closed - emails have already been sent!", "error")
            return redirect(url_for("main.index"))

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        gift_preference = request.form.get("gift_preference", "").strip()

        # Validate name
        if not name:
            flash("Name is required!", "error")
            return render_template(
                "register.html", name=name, email=email, gift_preference=gift_preference
            )

        if len(name) > 100:
            flash("Name is too long (maximum 100 characters)!", "error")
            return render_template(
                "register.html", name=name, email=email, gift_preference=gift_preference
            )

        # Validate email
        if not email:
            flash("Email is required!", "error")
            return render_template(
                "register.html", name=name, email=email, gift_preference=gift_preference
            )

        try:
            valid_email = validate_email(email, check_deliverability=False)
            email = valid_email.normalized
        except EmailNotValidError as e:
            flash(f"Invalid email address: {str(e)}", "error")
            return render_template(
                "register.html", name=name, email=email, gift_preference=gift_preference
            )

        # Validate gift preference length
        if len(gift_preference) > 500:
            flash("Gift preferences are too long (maximum 500 characters)!", "error")
            return render_template(
                "register.html", name=name, email=email, gift_preference=gift_preference
            )

        # Check if email already exists
        existing = Participant.query.filter_by(email=email).first()
        if existing:
            flash("This email is already registered!", "error")
            return render_template(
                "register.html", name=name, email=email, gift_preference=gift_preference
            )

        # Create new participant
        participant = Participant(name=name, email=email, gift_preference=gift_preference)
        db.session.add(participant)
        db.session.commit()

        logger.info(f"New participant registered: {email}")
        flash(
            "Registration successful! You will receive an email with your Secret Santa match.",
            "success",
        )
        return redirect(url_for("main.index"))

    # Check if registration is locked for GET requests too
    any_emails_sent = Match.query.filter_by(email_sent=True).first()
    registration_locked = any_emails_sent is not None

    return render_template("register.html", registration_locked=registration_locked)


@main.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        password_hash = current_app.config["ADMIN_PASSWORD_HASH"]

        if not password_hash:
            flash(
                "Admin password not configured. Please set ADMIN_PASSWORD_HASH in .env",
                "error",
            )
            logger.error("Admin login attempted but ADMIN_PASSWORD_HASH not configured")
            return render_template("admin_login.html")

        if check_password_hash(password_hash, password):
            session["admin_authenticated"] = True
            session.permanent = True
            logger.info("Admin login successful")
            return redirect(url_for("main.admin_dashboard"))
        else:
            logger.warning(f"Failed admin login attempt from {request.remote_addr}")
            flash("Invalid password", "error")

    return render_template("admin_login.html")


@main.route("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    return redirect(url_for("main.index"))


@main.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    participants = Participant.query.all()
    matches = Match.query.all()
    matches_created = len(matches) > 0
    any_emails_sent = Match.query.filter_by(email_sent=True).first() is not None

    # Determine current phase
    if any_emails_sent:
        phase = "locked"
        phase_message = "Locked - Emails have been sent"
        phase_color = "red"
    elif matches_created:
        phase = "matching"
        phase_message = "Matching Phase - You can add participants and re-match"
        phase_color = "orange"
    else:
        phase = "registration"
        phase_message = "Registration Open"
        phase_color = "green"

    return render_template(
        "admin_dashboard.html",
        participants=participants,
        matches=matches,
        matches_created=matches_created,
        any_emails_sent=any_emails_sent,
        phase=phase,
        phase_message=phase_message,
        phase_color=phase_color,
    )


@main.route("/admin/create-matches", methods=["POST"])
@admin_required
def create_matches():
    # Check if emails have been sent (prevents re-matching after emails sent)
    any_emails_sent = Match.query.filter_by(email_sent=True).first()
    if any_emails_sent:
        flash("Cannot recreate matches - emails have already been sent!", "error")
        return redirect(url_for("main.admin_dashboard"))

    # Clear existing matches if any exist (allow re-matching before emails sent)
    existing_matches = Match.query.first()
    if existing_matches:
        Match.query.delete()
        db.session.commit()
        logger.info("Admin cleared previous matches to create new ones")
        flash("Previous matches cleared. Creating new matches...", "info")

    participants = Participant.query.all()

    if len(participants) < 2:
        flash("Need at least 2 participants to create matches!", "error")
        return redirect(url_for("main.admin_dashboard"))

    # Create Secret Santa matches using a single-cycle algorithm
    # This ensures everyone is in one connected chain, preventing small loops
    # (e.g., prevents A->B, B->A, C->D, D->C pattern)

    max_attempts = 100
    for _attempt in range(max_attempts):
        # Shuffle participants to get random order
        shuffled = participants.copy()
        random.shuffle(shuffled)

        # Create a single cycle: each person gives to the next, last gives to first
        # This guarantees one complete loop through all participants
        matches_list = []
        for i in range(len(shuffled)):
            giver = shuffled[i]
            receiver = shuffled[(i + 1) % len(shuffled)]  # Next person, wrapping around
            matches_list.append((giver.id, receiver.id))

        # Verify no one gives to themselves (should be impossible with 2+ people, but double-check)
        valid = all(giver_id != receiver_id for giver_id, receiver_id in matches_list)

        if valid:
            # Create match records
            for giver_id, receiver_id in matches_list:
                match = Match(giver_id=giver_id, receiver_id=receiver_id)
                db.session.add(match)
            break
    else:
        flash("Could not create valid matches. Try again!", "error")
        return redirect(url_for("main.admin_dashboard"))

    db.session.commit()
    flash(
        f"Successfully created {len(participants)} Secret Santa matches in one connected chain!",
        "success",
    )
    return redirect(url_for("main.admin_dashboard"))


@main.route("/admin/clear-matches", methods=["POST"])
@admin_required
def clear_matches():
    # Check if any emails have been sent
    any_emails_sent = Match.query.filter_by(email_sent=True).first()
    if any_emails_sent:
        flash("Cannot clear matches - emails have already been sent!", "error")
        return redirect(url_for("main.admin_dashboard"))

    # Delete all matches
    match_count = Match.query.count()
    Match.query.delete()
    db.session.commit()

    logger.info("Admin cleared all matches")
    flash(f"Cleared {match_count} matches. You can now create new matches.", "success")
    return redirect(url_for("main.admin_dashboard"))


@main.route("/admin/send-emails", methods=["POST"])
@admin_required
def send_emails():
    matches = Match.query.filter_by(email_sent=False).all()

    if not matches:
        flash("All emails have already been sent!", "info")
        return redirect(url_for("main.admin_dashboard"))

    sent_count = 0
    error_count = 0
    first_error = None

    for match in matches:
        try:
            giver = match.giver
            receiver = match.receiver

            # Sanitize names and preferences to prevent header injection
            # Remove newlines and other control characters
            giver_name = " ".join(giver.name.split())
            receiver_name = " ".join(receiver.name.split())
            gift_pref = " ".join((receiver.gift_preference or "No preference specified").split())

            # Create email
            msg = MIMEMultipart()
            msg["From"] = current_app.config["SMTP_USERNAME"]
            msg["To"] = giver.email
            msg["Subject"] = "Your Secret Santa Match!"

            body = f"""Hello {giver_name}!

You are the Secret Santa for: {receiver_name}

Their gift preference/suggestion: {gift_pref}

Happy gifting!

Best regards,
Secret Santa Bot
"""

            msg.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP(
                current_app.config["SMTP_SERVER"], current_app.config["SMTP_PORT"]
            ) as server:
                server.starttls()
                server.login(
                    current_app.config["SMTP_USERNAME"],
                    current_app.config["SMTP_PASSWORD"],
                )
                server.send_message(msg)

            # Mark as sent
            match.email_sent = True
            db.session.commit()
            sent_count += 1

        except smtplib.SMTPAuthenticationError as e:
            error_count += 1
            logger.error(f"SMTP authentication failed when sending to {giver.email}: {e}")
            if not first_error:
                first_error = (
                    "SMTP authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD in .env"
                )
        except smtplib.SMTPException as e:
            error_count += 1
            error_msg = str(e)
            logger.error(f"SMTP error sending email to {giver.email}: {error_msg}")
            if not first_error:
                if "Connection refused" in error_msg:
                    first_error = "Connection refused. Check SMTP_SERVER and SMTP_PORT in .env"
                elif "timed out" in error_msg:
                    first_error = "Connection timeout. Check network/firewall settings"
                else:
                    first_error = f"SMTP error: {error_msg}"
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            logger.error(f"Unexpected error sending email to {giver.email}: {error_msg}")
            if not first_error:
                if "Name or service not known" in error_msg:
                    first_error = "Cannot resolve SMTP server hostname. Check SMTP_SERVER in .env"
                else:
                    first_error = f"Error: {error_msg}"

    if sent_count > 0:
        flash(f"Successfully sent {sent_count} emails!", "success")
    if error_count > 0:
        flash(f"Failed to send {error_count} emails. {first_error}", "error")

    return redirect(url_for("main.admin_dashboard"))


@main.route("/reveal")
@admin_required
def reveal():
    matches = Match.query.all()
    match_list = []

    for match in matches:
        match_list.append(
            {
                "id": match.id,
                "giver": match.giver.name,
                "receiver": match.receiver.name,
                "revealed": match.revealed,
            }
        )

    return render_template("reveal.html", matches=match_list)


@main.route("/reveal/toggle/<int:match_id>", methods=["POST"])
@admin_required
def toggle_reveal(match_id):
    match = Match.query.get_or_404(match_id)
    was_revealed = match.revealed
    match.revealed = not match.revealed

    # If marking as revealed (and not already sent thank you email), send email to receiver
    if match.revealed and not was_revealed and not match.thank_you_email_sent:
        try:
            receiver = match.receiver
            giver = match.giver

            # Sanitize names to prevent header injection
            receiver_name = " ".join(receiver.name.split())
            giver_name = " ".join(giver.name.split())

            # Create thank you reminder email
            msg = MIMEMultipart()
            msg["From"] = current_app.config["SMTP_USERNAME"]
            msg["To"] = receiver.email
            msg["Subject"] = "Your Secret Santa is Revealed!"

            body = f"""Hello {receiver_name}!

The Secret Santa reveal has happened! Your Secret Santa was: {giver_name}

We hope you enjoyed your gift! Please take a moment to send a thank you message to {giver_name} at {giver.email}.

Happy Holidays!

Best regards,
Secret Santa Bot
"""

            msg.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP(
                current_app.config["SMTP_SERVER"], current_app.config["SMTP_PORT"]
            ) as server:
                server.starttls()
                server.login(
                    current_app.config["SMTP_USERNAME"],
                    current_app.config["SMTP_PASSWORD"],
                )
                server.send_message(msg)

            # Mark as sent
            match.thank_you_email_sent = True
            logger.info(f"Sent thank you reminder to {receiver.email} revealing {giver.email}")
            flash(
                f"Marked as revealed and sent thank you reminder to {receiver.name}!",
                "success",
            )

        except smtplib.SMTPException as e:
            logger.error(f"Failed to send thank you email to {receiver.email}: {e}")
            flash(
                f"Marked as revealed but failed to send email to {receiver.name}. Error: {str(e)}",
                "warning",
            )
        except Exception as e:
            logger.error(f"Unexpected error sending thank you email to {receiver.email}: {e}")
            flash(
                f"Marked as revealed but failed to send email to {receiver.name}.",
                "warning",
            )

    db.session.commit()
    return redirect(url_for("main.reveal"))


@main.route("/admin/delete-participant/<int:participant_id>", methods=["POST"])
@admin_required
def delete_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)

    # Check if emails have been sent
    any_emails_sent = Match.query.filter_by(email_sent=True).first()
    if any_emails_sent:
        flash("Cannot delete participants - emails have already been sent!", "error")
        return redirect(url_for("main.admin_dashboard"))

    # Clear any matches involving this participant
    Match.query.filter(
        (Match.giver_id == participant_id) | (Match.receiver_id == participant_id)
    ).delete()

    db.session.delete(participant)
    db.session.commit()

    logger.info(f"Admin deleted participant: {participant.email}")
    flash(
        f"Deleted participant: {participant.name}. Any matches involving this participant have been cleared.",
        "success",
    )
    return redirect(url_for("main.admin_dashboard"))


@main.route("/admin/reset-all", methods=["POST"])
@admin_required
def reset_all():
    # Delete all matches and participants
    Match.query.delete()
    Participant.query.delete()
    Settings.query.delete()
    db.session.commit()

    flash("All data has been reset!", "success")
    return redirect(url_for("main.admin_dashboard"))
