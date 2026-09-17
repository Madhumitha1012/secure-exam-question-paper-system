import os
import random
import smtplib
from dotenv import load_dotenv
load_dotenv(override=True)
from flask import Flask, render_template, request, redirect, session, url_for
from users import users
from email.message import EmailMessage
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from encryption import encrypt_file, decrypt_file
from datetime import datetime, timedelta
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = "secure-exam-system-key"

# =========================================================
# SUPABASE CLOUD STORAGE
# =========================================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_BUCKET = "question-papers"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception(
        "SUPABASE_URL or SUPABASE_KEY is not configured. "
        "Set both environment variables and restart CMD."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Local folder is kept only for compatibility.
# Question papers are NOT stored here anymore.
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf"}


# =========================================================
# AUDIT LOG
# =========================================================
def add_log(action, email=None):
    if email is None:
        email = session.get("email", "System")

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs.txt", "a", encoding="utf-8") as file:
        file.write(f"{time} | {email} | {action}\n")


# =========================================================
# OTP
# =========================================================
def send_otp_email(receiver_email, otp):
    sender_email = os.environ.get("OTP_EMAIL")
    sender_password = os.environ.get("OTP_PASSWORD")

    if not sender_email or not sender_password:
        raise Exception("OTP email settings are not configured.")

    message = EmailMessage()
    message["Subject"] = "Secure Exam System - OTP"
    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content(
        f"""Hello,

Your OTP for the Secure Exam System is:

{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

Thank you,
Secure Exam System"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)


def generate_otp():
    return str(random.randint(100000, 999999))


# =========================================================
# STATUS
# =========================================================
def save_status(filename, status):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("status.txt", "a", encoding="utf-8") as file:
        file.write(f"{time} | {filename} | {status}\n")


def get_latest_status(filename):
    latest_status = None

    if not os.path.exists("status.txt"):
        return None

    with open("status.txt", "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(" | ")

            if len(parts) == 3 and parts[1] == filename:
                latest_status = parts[2]

    return latest_status


def get_all_statuses():
    result = {}

    if not os.path.exists("status.txt"):
        return result

    with open("status.txt", "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(" | ")

            if len(parts) == 3:
                result[parts[1]] = {
                    "time": parts[0],
                    "status": parts[2]
                }

    return result


# =========================================================
# SCHEDULE
# =========================================================
def save_schedule(
    filename,
    exam_name,
    exam_date,
    release_date,
    release_time
):
    with open("schedule.txt", "a", encoding="utf-8") as file:
        file.write(
            f"{filename} | {exam_name} | {exam_date} | "
            f"{release_date} | {release_time}\n"
        )


def get_schedule(filename):
    schedule = None

    if not os.path.exists("schedule.txt"):
        return None

    with open("schedule.txt", "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(" | ")

            if len(parts) == 5 and parts[0] == filename:
                schedule = {
                    "exam_name": parts[1],
                    "exam_date": parts[2],
                    "release_date": parts[3],
                    "release_time": parts[4]
                }

    return schedule


# =========================================================
# SUPABASE STORAGE HELPERS
# =========================================================
def upload_encrypted_file(filename, encrypted_data):
    """
    Upload encrypted question paper to the private Supabase bucket.
    The original PDF is never uploaded to Supabase.
    """
    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename,
            encrypted_data,
            {
                "content-type": "application/pdf",
                "upsert": False
            }
        )
        return True

    except Exception as error:
        print("Supabase upload error:", error)
        return False


def download_encrypted_file(filename):
    """
    Download an encrypted question paper from the private bucket.
    """
    try:
        return supabase.storage.from_(SUPABASE_BUCKET).download(
            filename
        )

    except Exception as error:
        print("Supabase download error:", error)
        return None


def delete_cloud_file(filename):
    """
    Delete an encrypted question paper from Supabase if needed.
    """
    try:
        supabase.storage.from_(SUPABASE_BUCKET).remove(
            [filename]
        )
        return True

    except Exception as error:
        print("Supabase delete error:", error)
        return False


# =========================================================
# ACCESS CONTROL
# =========================================================
def protected(role=None):
    if "email" not in session:
        return False

    if role and session.get("role") != role:
        return False

    return True


@app.context_processor
def inject_user():
    return {
        "current_email": session.get("email"),
        "current_role": session.get("role")
    }


# =========================================================
# HOME
# =========================================================
@app.route("/")
def home():
    return render_template("home.html")


# =========================================================
# LOGIN
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if email in users and check_password_hash(
            users[email]["password"],
            password
        ):
            otp = generate_otp()

            session["otp"] = otp
            session["otp_email"] = email
            session["otp_expiry"] = (
                datetime.now() + timedelta(minutes=5)
            ).timestamp()

            try:
                send_otp_email(email, otp)
            except Exception:
                session.pop("otp", None)
                session.pop("otp_email", None)
                session.pop("otp_expiry", None)

                return render_template(
                    "login.html",
                    error=(
                        "Unable to send OTP. "
                        "Please check the email settings."
                    )
                )

            # Record the actual email for this automatic event.
            add_log(
                "Password verified. OTP sent.",
                email=email
            )

            return redirect(url_for("verify_otp"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# =========================================================
# OTP VERIFICATION
# =========================================================
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "otp_email" not in session:
        return redirect(url_for("login"))

    email = session.get("otp_email")

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        saved_otp = session.get("otp")
        expiry_time = session.get("otp_expiry")

        if (
            not expiry_time
            or datetime.now().timestamp() > expiry_time
        ):
            session.pop("otp", None)
            session.pop("otp_email", None)
            session.pop("otp_expiry", None)

            add_log(
                "OTP expired.",
                email=email
            )

            return render_template(
                "otp.html",
                error="OTP expired. Please login again."
            )

        if entered_otp == saved_otp:
            session["email"] = email
            session["role"] = users[email]["role"]

            session.pop("otp", None)
            session.pop("otp_email", None)
            session.pop("otp_expiry", None)

            add_log(
                "OTP verification successful. User logged in.",
                email=email
            )

            return redirect(url_for("dashboard"))

        add_log(
            "OTP verification failed.",
            email=email
        )

        return render_template(
            "otp.html",
            error="Invalid OTP."
        )

    return render_template("otp.html")


# =========================================================
# DASHBOARD
# =========================================================
@app.route("/dashboard")
def dashboard():
    if not protected():
        return redirect(url_for("login"))

    statuses = get_all_statuses()

    total = len(statuses)

    approved = sum(
        1
        for x in statuses.values()
        if x["status"] == "Approved"
    )

    released = sum(
        1
        for x in statuses.values()
        if x["status"] == "Released"
    )

    pending = sum(
        1
        for x in statuses.values()
        if x["status"] == "Pending Review"
    )

    rejected = sum(
        1
        for x in statuses.values()
        if x["status"] == "Rejected"
    )

    return render_template(
        "dashboard.html",
        total=total,
        approved=approved,
        released=released,
        pending=pending,
        rejected=rejected
    )


# =========================================================
# LOGOUT
# =========================================================
@app.route("/logout")
def logout():
    if "email" in session:
        add_log("User logged out.")

    session.clear()

    return redirect(url_for("home"))


# =========================================================
# UPLOAD QUESTION PAPERS
# =========================================================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not protected("Question Setter"):
        return redirect(url_for("login"))

    if request.method == "POST":
        exam_name = request.form.get(
            "exam_name",
            ""
        ).strip()

        exam_date = request.form.get(
            "exam_date",
            ""
        )

        release_date = request.form.get(
            "release_date",
            ""
        )

        release_time = request.form.get(
            "release_time",
            ""
        )

        try:
            number_of_papers = int(
                request.form.get(
                    "number_of_papers",
                    "0"
                )
            )
        except ValueError:
            number_of_papers = 0

        if not exam_name:
            return render_template(
                "upload.html",
                error="Exam name is required."
            )

        if not 1 <= number_of_papers <= 5:
            return render_template(
                "upload.html",
                error="Upload 1 to 5 question papers."
            )

        try:
            exam_datetime = datetime.strptime(
                exam_date,
                "%Y-%m-%d"
            )

            release_datetime = datetime.strptime(
                f"{release_date} {release_time}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:
            return render_template(
                "upload.html",
                error="Please enter valid dates and time."
            )

        if release_datetime > exam_datetime.replace(
            hour=23,
            minute=59
        ):
            return render_template(
                "upload.html",
                error=(
                    "Release date/time cannot be "
                    "after the exam date."
                )
            )

        uploaded_files = []

        for i in range(
            1,
            number_of_papers + 1
        ):
            file = request.files.get(
                f"question_paper_{i}"
            )

            if not file or not file.filename:
                return render_template(
                    "upload.html",
                    error=(
                        f"Please select Question Paper {i}."
                    )
                )

            if not file.filename.lower().endswith(
                ".pdf"
            ):
                return render_template(
                    "upload.html",
                    error=(
                        f"Question Paper {i} "
                        "must be a PDF file."
                    )
                )

            uploaded_files.append(file)

        successful_uploads = []

        for file in uploaded_files:
            original_filename = secure_filename(
                file.filename
            )

            if not original_filename:
                return render_template(
                    "upload.html",
                    error="Invalid file name."
                )

            unique_name = (
                datetime.now().strftime(
                    "%Y%m%d%H%M%S%f"
                )
                + "_"
                + original_filename
            )

            encrypted_filename = (
                unique_name + ".enc"
            )

            file_data = file.read()

            if not file_data:
                return render_template(
                    "upload.html",
                    error=(
                        f"{original_filename} is empty."
                    )
                )

            # Encrypt the PDF before cloud storage.
            encrypted_data = encrypt_file(
                file_data
            )

            # Upload only encrypted data to Supabase.
            cloud_uploaded = upload_encrypted_file(
                encrypted_filename,
                encrypted_data
            )

            if not cloud_uploaded:
                return render_template(
                    "upload.html",
                    error=(
                        f"Unable to store "
                        f"{original_filename} in Supabase. "
                        "Please check the Supabase settings."
                    )
                )

            save_status(
                encrypted_filename,
                "Pending Review"
            )

            save_schedule(
                encrypted_filename,
                exam_name,
                exam_date,
                release_date,
                release_time
            )

            add_log(
                "Question paper uploaded to secure cloud "
                f"storage: {original_filename} for {exam_name}"
            )

            successful_uploads.append(
                original_filename
            )

        return render_template(
            "upload.html",
            success=(
                f"{len(successful_uploads)} question papers "
                f"for {exam_name} were encrypted and stored "
                "in Supabase successfully."
            )
        )

    return render_template("upload.html")


# =========================================================
# REVIEWER
# =========================================================
@app.route("/review", methods=["GET", "POST"])
def review():
    if not protected("Reviewer"):
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")

        filename = os.path.basename(
            request.form.get(
                "filename",
                ""
            )
        )

        current_status = get_latest_status(
            filename
        )

        if current_status != "Pending Review":
            return render_template(
                "review.html",
                files=build_file_list(),
                error=(
                    "This question paper cannot be "
                    "approved or rejected now."
                )
            )

        if action == "approve":
            save_status(
                filename,
                "Approved"
            )

            add_log(
                f"Question paper approved: {filename}"
            )

            return redirect(
                url_for("review")
            )

        if action == "reject":
            save_status(
                filename,
                "Rejected"
            )

            add_log(
                f"Question paper rejected: {filename}"
            )

            return redirect(
                url_for("review")
            )

    return render_template(
        "review.html",
        files=build_file_list()
    )


def build_file_list():
    items = []

    for filename, info in get_all_statuses().items():
        schedule = get_schedule(filename)

        if schedule:
            items.append({
                "filename": filename,
                "status": info["status"],
                "schedule": schedule
            })

    items.sort(
        key=lambda x: (
            x.get("schedule", {}).get(
                "exam_name",
                ""
            )
        ),
        reverse=True
    )

    return items


# =========================================================
# REVIEWER VIEW PAPER
# =========================================================
@app.route("/review-paper/<path:filename>")
def review_paper(filename):
    if not protected("Reviewer"):
        return redirect(url_for("login"))

    safe_filename = os.path.basename(
        filename
    )

    if get_latest_status(
        safe_filename
    ) not in [
        "Pending Review",
        "Approved",
        "Rejected"
    ]:
        return "Question paper not found.", 404

    encrypted_data = download_encrypted_file(
        safe_filename
    )

    if encrypted_data is None:
        return (
            "Question paper not found in Supabase.",
            404
        )

    try:
        decrypted_data = decrypt_file(
            encrypted_data
        )
    except Exception:
        return (
            "Unable to decrypt question paper.",
            500
        )

    add_log(
        f"Reviewer viewed question paper: {safe_filename}"
    )

    return decrypted_data, 200, {
        "Content-Type": "application/pdf",
        "Content-Disposition": "inline"
    }


# =========================================================
# ADMIN STATUS
# =========================================================
@app.route("/status")
def status():
    if not protected("Admin"):
        return redirect(url_for("login"))

    statuses = get_all_statuses()
    rows = []

    for filename, info in statuses.items():
        schedule = get_schedule(filename)

        rows.append({
            "filename": filename,
            "time": info["time"],
            "status": info["status"],
            "schedule": schedule,
            "exists": True
        })

    rows.sort(
        key=lambda x: x["time"],
        reverse=True
    )

    return render_template(
        "status.html",
        rows=rows
    )


# =========================================================
# ADMIN RELEASE
# =========================================================
@app.route("/release", methods=["GET", "POST"])
def release():
    if not protected("Admin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        filename = os.path.basename(
            request.form.get(
                "filename",
                ""
            )
        )

        current_status = get_latest_status(
            filename
        )

        if current_status != "Approved":
            return render_template(
                "release.html",
                rows=build_release_rows(),
                error=(
                    "Only an approved question paper "
                    "can be released."
                )
            )

        schedule = get_schedule(
            filename
        )

        if not schedule:
            return render_template(
                "release.html",
                rows=build_release_rows(),
                error=(
                    "Release schedule not found "
                    "for this question paper."
                )
            )

        try:
            release_datetime = datetime.strptime(
                f"{schedule['release_date']} "
                f"{schedule['release_time']}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:
            return render_template(
                "release.html",
                rows=build_release_rows(),
                error=(
                    "Invalid release date or time."
                )
            )

        if datetime.now() < release_datetime:
            display = release_datetime.strftime(
                "%d-%m-%Y %I:%M %p"
            )

            return render_template(
                "release.html",
                rows=build_release_rows(),
                error=(
                    f"Question paper cannot be released "
                    f"before {display}."
                )
            )

        exam_name = schedule["exam_name"]

        # Only one paper can be released for each exam.
        for saved_filename, info in (
            get_all_statuses().items()
        ):
            saved_schedule = get_schedule(
                saved_filename
            )

            if (
                saved_schedule
                and saved_schedule[
                    "exam_name"
                ].strip().lower()
                == exam_name.strip().lower()
                and info["status"] == "Released"
            ):
                return render_template(
                    "release.html",
                    rows=build_release_rows(),
                    error=(
                        f"A question paper for "
                        f"{exam_name} has already "
                        "been released."
                    )
                )

        save_status(
            filename,
            "Released"
        )

        add_log(
            f"Question paper released: "
            f"{filename} for {exam_name}"
        )

        return redirect(
            url_for("release")
        )

    return render_template(
        "release.html",
        rows=build_release_rows()
    )


def build_release_rows():
    rows = []

    for filename, info in get_all_statuses().items():
        schedule = get_schedule(
            filename
        )

        if schedule:
            rows.append({
                "filename": filename,
                "time": info["time"],
                "status": info["status"],
                "schedule": schedule,
                "exists": True
            })

    rows.sort(
        key=lambda x: x["time"],
        reverse=True
    )

    return rows


# =========================================================
# ADMIN AUDIT LOGS
# =========================================================
@app.route("/logs")
def logs():
    if not protected("Admin"):
        return redirect(url_for("login"))

    log_rows = []

    if os.path.exists("logs.txt"):
        with open(
            "logs.txt",
            "r",
            encoding="utf-8"
        ) as file:
            for line in file:
                parts = line.strip().split(
                    " | ",
                    2
                )

                if len(parts) == 3:
                    log_rows.append({
                        "time": parts[0],
                        "email": parts[1],
                        "action": parts[2]
                    })

    log_rows.reverse()

    return render_template(
        "logs.html",
        logs=log_rows
    )


# =========================================================
# EXAM CENTRE
# =========================================================
@app.route("/centre-papers")
def centre_papers():
    if not protected("Exam Centre"):
        return redirect(url_for("login"))

    papers = []

    for filename, info in get_all_statuses().items():
        if info["status"] != "Released":
            continue

        # Confirm that the encrypted file exists in Supabase.
        encrypted_data = download_encrypted_file(
            os.path.basename(filename)
        )

        if encrypted_data is None:
            continue

        papers.append({
            "filename": filename,
            "schedule": get_schedule(filename),
            "time": info["time"]
        })

    papers.sort(
        key=lambda x: x["time"],
        reverse=True
    )

    return render_template(
        "centre_papers.html",
        papers=papers
    )


# =========================================================
# ACCESS RELEASED PAPER
# =========================================================
@app.route("/access-paper/<path:filename>")
def access_paper(filename):
    if (
        not protected()
        or session.get("role")
        not in ["Admin", "Exam Centre"]
    ):
        return redirect(
            url_for("login")
        )

    safe_filename = os.path.basename(
        filename
    )

    if get_latest_status(
        safe_filename
    ) != "Released":
        return (
            "Question paper is not released yet.",
            403
        )

    encrypted_data = download_encrypted_file(
        safe_filename
    )

    if encrypted_data is None:
        return (
            "Question paper not found in Supabase.",
            404
        )

    try:
        decrypted_data = decrypt_file(
            encrypted_data
        )
    except Exception:
        return (
            "Unable to decrypt question paper.",
            500
        )

    add_log(
        f"Released question paper accessed: "
        f"{safe_filename}"
    )

    return decrypted_data, 200, {
        "Content-Type": "application/pdf",
        "Content-Disposition": "inline"
    }


# =========================================================
# START APPLICATION
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
