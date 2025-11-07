from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from storage import create_user, verify_user
from schemas import LoginUser

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.get("/register")
def register_form():
    return render_template("auth_register.html")

@bp.post("/register")
def register_post():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    if not email or not password:
        flash("E-mail et mot de passe requis.")
        return redirect(url_for("auth.register_form"))
    try:
        u = create_user(email, password)
    except ValueError:
        flash("E-mail déjà utilisé.")
        return redirect(url_for("auth.register_form"))
    login_user(LoginUser(u))
    return redirect(url_for("author.dashboard"))

@bp.get("/login")
def login_form():
    return render_template("auth_login.html")

@bp.post("/login")
def login_post():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    u = verify_user(email, password)
    if not u:
        flash("Identifiants invalides.")
        return redirect(url_for("auth.login_form"))
    login_user(LoginUser(u))
    return redirect(url_for("author.dashboard"))

@bp.post("/logout")
@login_required
def logout_post():
    logout_user()
    return redirect(url_for("auth.login_form"))
