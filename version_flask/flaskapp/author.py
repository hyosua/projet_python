import json
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from storage import list_questions_by_owner, save_question, load_question, create_link
from schemas import Question

bp = Blueprint("author", __name__)

@bp.get("/dashboard")
@login_required
def dashboard():
    qs = list_questions_by_owner(current_user.email)
    return render_template("dashboard.html", questions=qs)

@bp.get("/questions/new")
@login_required
def new_question():
    return render_template("question_form.html")

@bp.post("/questions")
@login_required
def create_question():
    try:
        num = int(request.form["num"])
    except (KeyError, ValueError):
        abort(400, "Numéro invalide")
    q = Question(
        owner_email=current_user.email,
        num=num,
        title=request.form.get("title", "").strip(),
        statement=request.form.get("statement", "").strip(),
        expected_answer=request.form.get("expected_answer", "").strip(),
        required_points=json.loads(request.form.get("required_points_json", "[]") or "[]"),
        forbidden_points=json.loads(request.form.get("forbidden_points_json", "[]") or "[]"),
        attachments=json.loads(request.form.get("attachments_json", "[]") or "[]"),
    )
    save_question(q)
    return redirect(url_for("author.view_question", num=q.num))

@bp.get("/questions/<int:num>")
@login_required
def view_question(num: int):
    q = load_question(num)
    if not q or q.owner_email != current_user.email:
        abort(404)
    return render_template("question_view.html", q=q)

@bp.post("/questions/<int:num>/new-link")
@login_required
def new_link(num: int):
    q = load_question(num)
    if not q or q.owner_email != current_user.email:
        abort(404)
    create_link(num)
    # Pour l’instant on ne liste pas les liens ; on revient sur la page
    return redirect(url_for("author.view_question", num=num))
