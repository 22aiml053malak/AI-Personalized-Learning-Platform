import os
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from ext import db
from models import User

# Configuration
UPLOAD_FOLDER = "static/profile_pics"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Create the Blueprint
upload_profile_bp = Blueprint("upload_profile", __name__)

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_profile_bp.route("/upload_profile_pic", methods=["POST"])
@login_required
def upload_profile_pic():
    if "profile_pic" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("home"))

    file = request.files["profile_pic"]

    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("home"))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Update the user profile pic in the database
        current_user.profile_pic = filename
        db.session.commit()

        flash("Profile picture updated successfully!", "success")
        return redirect(url_for("home"))

    flash("Invalid file format", "danger")
    return redirect(url_for("home"))


@upload_profile_bp.route("/delete_profile_pic", methods=["POST"])
@login_required
def delete_profile_pic():
    if current_user.profile_pic and current_user.profile_pic != "default_profile.jpg":
        # Remove the profile picture file
        file_path = os.path.join(UPLOAD_FOLDER, current_user.profile_pic)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Reset to default profile picture
        current_user.profile_pic = "default_profile.jpg"
        db.session.commit()
        flash("Profile picture deleted successfully!", "success")
    else:
        flash("No profile picture to delete.", "warning")

    return redirect(url_for("home"))
