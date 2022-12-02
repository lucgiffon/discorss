from flask import Blueprint, abort  # it means this file contains a bunch of routes
from flask import render_template, request, flash, redirect, url_for
import re

from discorss_models.base import db_session
from discorss_models.models import User


def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

    return {
        'password_ok': password_ok,
        'length_error': length_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
    }


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    abort(404)
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        wrong_pass_message = "Couple user/password not recognized."
        if user:
            if user.verify_password(password):
                flash("Logged in successfully!", category='success')
                return redirect(url_for('views.home'))
            else:
                flash(wrong_pass_message, category='danger')
        else:
            flash(wrong_pass_message, category='danger')

    return render_template("login.html", boolean=False)


@auth_blueprint.route("/logout")
def logout():
    abort(404)
    return "<p>Logout</p>"



@auth_blueprint.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    abort(404)
    if request.method == "POST":
        # Make a regular expression
        # for validating an Email
        regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        pass_check = password_check(password1)

        user = User.query.filter_by(email=email).first()
        if user:
            flash("L'utilisateur existe déjà.", category="danger")
        elif not re.fullmatch(regex_email, email):
            flash("Adresse e-mail invalide.", category="danger")
        elif not password1 == password2:
            flash("Les mots de passe sont différents.", category="danger")
        elif not pass_check["password_ok"]:
            str_password = "Le mot de passe n'est pas assez fort. Raisons: " + \
                           str([key for key, is_true in pass_check.items() if is_true])
            flash(str_password, category="danger")
        else:
            new_user = User(email=email, password=password1)
            # new_user.verify_password("yNhT5U+8Ku_U%9_7")

            db_session.add(new_user)
            db_session.commit()
            flash("Compte créé avec succès.", category="success")
            return redirect(url_for('views.home'))

    return render_template("signup.html")
