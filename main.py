from flask import Flask, render_template, redirect, url_for, request, flash, abort
from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, URLField, IntegerField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditorField, CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, LoginManager, login_required, UserMixin
from flask_login import AnonymousUserMixin
from functools import wraps
import smtplib
import random

# app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = "Haniarol9071@gmail"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)
SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

my_email = "upcomingfearure@gmail.com"
password = "smcg mylb oadq rqer"


# Flask Forms
class QuoteForm(FlaskForm):
    quote = CKEditorField("Quote", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    submit = SubmitField("Add")


class Register(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class SkillForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    image = URLField("Image Url")
    submit = SubmitField("ADD")


class ResetPasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ResetForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    send_code = SubmitField("Send reset code")


class VerifyForm(FlaskForm):
    code = StringField("Enter Code", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ProfileForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    image = URLField("Image Url", validators=[DataRequired()])
    add = SubmitField("ADD")


class BackgroundImgForm(FlaskForm):
    background_image = URLField("Background Image", validators=[DataRequired()])
    main_image = URLField("Main Image", validators=[DataRequired()])
    cloud = URLField("Cloud")
    title = StringField("Title", validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])
    submit = SubmitField("ADD")


# ----------------------------- DataBase ------------------------------#
Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    quote = relationship("Quotes", backref="user")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"{self.name} {self.email} {self.password}"


class Quotes(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True)
    quote = Column(String, nullable=False)
    author = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String, nullable=False)

    # user = Column(String, ForeignKey("users.name"))

    def __init__(self, quote, author, user_id, user_name):
        self.quote = quote
        self.author = author
        self.user_id = user_id
        self.user_name = user_name

    def __repr__(self):
        return f"Inspirational:{self.quote}"


class ProfileDatabase(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=False)

    def __init__(self, title, content, image_url):
        self.title = title
        self.content = content
        self.image_url = image_url

    def __repr__(self):
        return f"{self.title} {self.content} {self.image_url}"


class SkillDatabase(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=False)

    def __init__(self, title, content, image_url):
        self.title = title
        self.content = content
        self.image_url = image_url

    def __repr__(self):
        return f"{self.title} {self.content} {self.image_url}"


class BackgroundImgFormDatabase(Base):
    __tablename__ = "background Image"
    id = Column(Integer, primary_key=True)
    background_image = Column(String)
    main_image = Column(String)
    cloud = Column(String)
    main_title = Column(String, nullable=False)
    main_description = Column(String, nullable=False)

    def __init__(self, background_image, main_image, cloud, main_title, main_description):
        self.background_image = background_image
        self.main_image = main_image
        self.cloud = cloud
        self.main_title = main_title
        self.main_description = main_description

    def __repr__(self):
        return f"{self.main_title} {self.main_description} {self.background_image} {self.main_image} {self.cloud}"


engin = create_engine("sqlite:///users.db", echo=True)
Base.metadata.create_all(bind=engin)
Session = sessionmaker(bind=engin)
session = Session()


# authentication work
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 2:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.name = 'Guest'


def password_generator():
    return random.randint(500000, 10000000)


# ------------------------ Routes --------------------------------------#

@app.route("/")
def home():
    datas = session.query(ProfileDatabase).all()
    skills = session.query(SkillDatabase).all()
    main = session.query(BackgroundImgFormDatabase).first()
    return render_template("index.html", year=date.today().year, user=current_user, datas=datas, skills=skills,
                           main=main)


@app.route("/quotes")
def quotes():
    all_quotes = session.query(Quotes).all()
    all_quotes.reverse()
    return render_template("quotes.html", quotes=all_quotes, year=date.today().year, user=current_user)


@app.route("/add_quotes", methods=["POST", "GET"])
def add_quotes():
    form = QuoteForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            quote = session.query(Quotes).filter_by(quote=form.quote.data).first()
            if not quote:
                new_quote = Quotes(quote=form.quote.data,
                                   author=form.author.data,
                                   user_id=current_user.id,
                                   user_name=current_user.name)
                session.add(new_quote)
                session.commit()
                return redirect(url_for("quotes"))
            else:
                flash("Sorry! This is quote is already exist")
                flash("Please try another one!")
                return redirect(url_for("add_quotes"))

        else:
            flash("If you want to add quote you have register first!")
        return redirect(url_for("register"))
    return render_template("add.html", form=form, year=date.today().year, user=current_user)


@app.route("/delete")
def delete():
    to_delete_quote = session.query(Quotes).get(request.args.get("i"))
    session.delete(to_delete_quote)
    session.commit()
    return redirect(url_for("quotes"))


@app.route("/edit", methods=["POST", "GET"])
def edit():
    quote = session.query(Quotes).get(request.args.get("i"))
    edit_quote = QuoteForm(
        quote=quote.quote,
        author=quote.author
    )
    if edit_quote.validate_on_submit():
        quote.quote = edit_quote.quote.data
        quote.author = edit_quote.author.data
        session.commit()
        return redirect(url_for("quotes"))
    return render_template("edit.html", form=edit_quote, user=current_user)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = Register()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()
        user_name = session.query(User).filter_by(name=form.name.data).first()
        if user:
            flash("There is an account with this email address!")
            return redirect(url_for("register"))
        elif user_name:
            flash("This username is already taken! please choose another")
            return redirect(url_for("register"))
        else:
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data, method="pbkdf2", salt_length=8)
            )
            session.add(new_user)
            session.commit()
            login_user(new_user)
            load_user(new_user.id)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, year=date.today().year, user=current_user)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        requested_user = session.query(User).filter_by(email=form.email.data).first()
        if not requested_user:
            flash("There is no such account")
            return redirect(url_for("login"))
        elif not check_password_hash(requested_user.password, password):
            flash("The password is incorrect please try again!")
            return redirect(url_for("login"))
        else:
            login_user(requested_user)
            load_user(requested_user.id)
            return redirect(url_for("home"))
    return render_template("login.html", form=form, year=date.today().year, user=current_user)


@app.route("/change", methods=["POST", "GET"])
def reset_password():
    form = ResetPasswordForm()
    user = session.query(User).get(current_user.id)
    if form.validate_on_submit():
        if check_password_hash(user.password, form.old_password.data):
            user.password = generate_password_hash(form.new_password.data, method="pbkdf2", salt_length=8)
            session.commit()
            return redirect(url_for("home"))
        flash("The old password is incorrect")

    return render_template("reset_password.html", form=form, user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home", user=current_user))


@app.route("/reset", methods=["POST", "GET"])
def forget_password():
    form = ResetForm()
    if form.validate_on_submit():
        email = form.email.data
        user = session.query(User).filter_by(email=email).first()
        id = user.id
        if user:
            new_password = password_generator()
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email, to_addrs=user.email,
                                    msg=f"subject:Reset Code \n\n {new_password}")
            return redirect(url_for("verify", id=id))
        else:
            flash("Incorrect email please enter a valid email address!")
            return redirect(url_for("forget_password"))
    return render_template("reset.html", form=form, user=current_user)


@app.route("/verify", methods=["POST", "GET"])
def verify():
    form = VerifyForm()
    id = request.args.get("id")
    print("email", id)
    if form.validate_on_submit():
        user = session.query(User).get(id)
        print("user", user)
        if form.code.data:
            user.password = generate_password_hash(form.code.data, method="pbkdf2", salt_length=8)
            session.commit()
            flash("Please change your password!\n Your current password is received code!")
            return redirect(url_for("login"))
        else:
            flash("The code is incorrect")
            return redirect(url_for("verify"))

    return render_template("verify.html", user=current_user, form=form)


# control profile and skill on main page
@app.route("/pro", methods=["POST", "GET"])
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        profile = ProfileDatabase(
            title=form.title.data,
            content=form.content.data,
            image_url=form.image.data
        )
        session.add(profile)
        session.commit()
        return redirect(url_for("home"))
    return render_template("profile.html", form=form, user=current_user)


@app.route("/pro_edit", methods=["POST", "GET"])
@admin_only
def profile_edit():
    id = request.args.get("id")
    data = session.query(ProfileDatabase).get(id)
    edit_pro = ProfileForm(
        title=data.title,
        content=data.content,
        image=data.image_url
    )
    if edit_pro.validate_on_submit():
        data.title = edit_pro.title.data
        data.content = edit_pro.content.data
        data.image_url = edit_pro.image.data
        session.commit()
        return redirect(url_for("home"))
    return render_template("profile_edit.html", form=edit_pro, user=current_user)


@app.route("/delete-pro", methods=["POST", "GET"])
def delete_pro():
    id = request.args.get("id")
    to_delete_pro = session.query(ProfileDatabase).get(id)
    session.delete(to_delete_pro)
    session.commit()
    return redirect(url_for("home"))


@app.route("/skills", methods=["POST", "GET"])
@admin_only
def add_skill():
    form = SkillForm()
    if form.validate_on_submit():
        new_skill = SkillDatabase(
            title=form.title.data,
            content=form.content.data,
            image_url=form.image.data
        )
        session.add(new_skill)
        session.commit()
        return redirect(url_for("home"))
    return render_template("skills.html", form=form, user=current_user)


@app.route("/edit_skill", methods=["POST", "GET"])
@admin_only
def edit_skill():
    id = request.args.get("id")
    skill = session.query(SkillDatabase).get(id)
    skill_edit_form = SkillForm(
        title=skill.title,
        content=skill.content,
        image=skill.image_url
    )
    if skill_edit_form.validate_on_submit():
        skill.title = skill_edit_form.title.data
        skill.content = skill_edit_form.content.data
        skill.image_url = skill_edit_form.image.data
        session.commit()
        return redirect(url_for("home"))
    return render_template("skill_edit.html", user=current_user, form=skill_edit_form)


@app.route("/delete_skill")
@admin_only
def delete_skill():
    id = request.args.get("id")
    skill = session.query(SkillDatabase).get(id)
    session.delete(skill)
    session.commit()
    return redirect(url_for("home"))


@app.route("/description")
def skill_description():
    id = request.args.get("id")
    skill = session.query(SkillDatabase).get(id)
    return render_template("description.html", user=current_user, skill=skill)


@app.route("/pro_description")
def pro_description():
    id = request.args.get("id")
    Profile = session.query(ProfileDatabase).get(id)
    return render_template("profile_descriptio.html", user=current_user, skill=Profile)


# landing page edit and update
@app.route("/main_page", methods=["POST", "GET"])
@admin_only
def main_page():
    form = BackgroundImgForm()
    if form.validate_on_submit():
        new_background = BackgroundImgFormDatabase(
            background_image=form.background_image.data,
            main_image=form.main_image.data,
            cloud=form.cloud.data,
            main_title=form.title.data,
            main_description=form.description.data
        )
        session.add(new_background)
        session.commit()
        return redirect(url_for("home"))
    return render_template("main_page.html", user=current_user, form=form)


@app.route("/main_page_edit", methods=["POST", "GET"])
@admin_only
def main_edit():
    id = request.args.get("id")
    main = session.query(BackgroundImgFormDatabase).get(id)
    main_form = BackgroundImgForm(
        background_image=main.background_image,
        main_image=main.main_image,
        cloud=main.cloud,
        title=main.main_title,
        description=main.main_description
    )
    if main_form.validate_on_submit():
        main.background_image = main_form.background_image.data
        main.main_image = main_form.main_image.data
        main.cloud = main_form.cloud.data
        main.main_title = main_form.title.data
        main.main_description = main_form.description.data
        session.commit()
        return redirect(url_for("home"))

    return render_template("main_edit.html", user=current_user, form=main_form)


@app.route("/main_delete")
@admin_only
def main_delete():
    id = request.args.get("id")
    main_pro = session.query(BackgroundImgFormDatabase).get(id)
    session.delete(main_pro)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
