from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, logout_user
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature, URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from flaskblog import db, mail, login_manager
from flaskblog.models import User, current_year, BlogPost, Notification
from flaskblog.users.forms import LoginForm, RegisterForm, PasswordResetRequestForm, PasswordResetForm

users = Blueprint("users", __name__)

# Serializer for token generation
with current_app.app_context():
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Require confirmed email address for login
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash(message="Please login or register and confirm your email address to access this page.", category="danger")
    return redirect(url_for('users.login'))


@users.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # validate email
        try:
            # validate and get the normalized email address
            email = validate_email(form.email.data).email
        except EmailNotValidError as e:
            # email is not valid, display an error message to the user
            flash(message=f"Invalid email address: {e}", category="danger")
            return redirect(url_for('users.register'))

        # hash and salt password
        hash_and_salted_password = generate_password_hash(password=form.password.data, method="pbkdf2:sha256",
                                                          salt_length=8)

        user_name = form.name.data
        print(hash_and_salted_password)

        new_user = User(name=user_name, email=email, password=hash_and_salted_password, confirmed=False)
        try:
            db.session.add(new_user)
            db.session.commit()

            # Generate token for email confirmation link
            token = serializer.dumps(new_user.email, salt='email-confirm')

            # Send email confirmation to user
            confirmation_url = url_for('users.confirm_email', token=token, _external=True)
            # If you have set MAIL_DEFAULT_SENDER you don’t need to set the message sender explicity, as it will use
            # this configuration value by default:"
            msg = Message("Confirm Your Email Address", recipients=[new_user.email])
            msg.body = f"Hello {new_user.name},\n\nThank you for registering on our website! Please click the link " \
                       f"below to confirm your email address and complete your regist" \
                       f"ration:\n\n{confirmation_url}\n\nBest regards,\nYour Website Team"
            mail.send(msg)

            flash(message=f"A confirmation email has been sent to {new_user.email}", category="success")
            # create notification after registering new user
            notification = Notification(message=f'A new user {new_user.name} registered.')
            db.session.add(notification)
            db.session.commit()
            return redirect(url_for('users.login'))
        except IntegrityError:
            db.session.rollback()
            flash(message=f"{email} is already registered. Please login instead.", category="danger")
            return redirect(url_for('users.login'))

    return render_template('register.html', form=form, year=current_year)


@users.route('/confirm_email/<token>')
def confirm_email(token):
    """Returns the url that take the user to the login page to confirm his registration and update user confirm to
    True"""
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.confirmed = True
            db.session.commit()
            flash(message="Your email address has been confirmed. Thank you for registering!", category="success")
            # Create a new notification
            notification = Notification(message=f'The user {user.name} has confirmed his mail address')
            db.session.add(notification)
            db.session.commit()
        else:
            flash(message="There was an error confirming your email address. Please try again.", category="danger")
    except SignatureExpired:
        flash(message="The confirmation link has expired. Please request a new confirmation email.", category="danger")
    except BadSignature:
        flash(message="The confirmation link is invalid. Please request a new confirmation email.", category="danger")
    except Exception as e:
        flash(message="An error occurred while confirming your email address. Please try again later.",
              category="danger")
        print(e)  # print the error message for debugging purposes
    return redirect(url_for('users.login'))


@users.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_input = form.email.data
        password_input = form.password.data
        # Find user by email entered.
        user = User.query.filter_by(email=email_input).first()
        if not user:
            flash(message=f"That email does not exist, please try again.")
            return redirect(url_for('users.login'))
        # Email exists and password correct
        elif user.confirmed:
            if check_password_hash(pwhash=user.password, password=password_input):
                login_user(user=user)
                # create notification
                notification = Notification(message=f"{user.name} is logged in")
                db.session.add(notification)
                db.session.commit()
                flash(message=f"You have been Successfully Logged in!", category="success")
                return redirect(url_for("main.get_all_posts"))
            # Password incorrect
            else:
                flash(message=f"You have entered a wrong password! Please try again!", category="danger")
                return redirect(url_for('users.login'))
        # Check if the mail is not confirmed
        else:
            flash(message=f"Please confirm your email to log in!", category="danger")

    return render_template("login.html", form=form, year=current_year)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash(message="You have been logged out!", category="warning")
    # # create notification
    # notification = Notification(message=f"{user.name} is logged out")
    # db.session.add(notification)
    # db.session.commit()
    return redirect(url_for('main.get_all_posts'))


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(name=username).first_or_404()
    posts = BlogPost.query.filter_by(author=user) \
        .order_by(BlogPost.date.desc()) \
        .paginate(page=page, per_page=2)
    return render_template('user-posts.html', posts=posts, user=user, num_posts=user.num_posts(), year=current_year)


# Route for password reset request
@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        # validate email
        try:
            # validate and get the normalized email address
            email = validate_email(form.email.data).email
        except EmailNotValidError as e:
            # email is not valid, display an error message to the user
            flash(message=f"Invalid email address: {e}", category="danger")

        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(user.email, salt='password-reset')
            reset_url = url_for('users.reset_password_confirm', token=token, _external=True)
            msg = Message('Password Reset Request', recipients=[user.email])
            msg.body = f"Hello {user.name},\n\nYou have requested a password reset for your account on our website." \
                       f"Please click the link below to reset your password:\n\n{reset_url}\n\nIf you didn't request" \
                       f"this password reset, please ignore this email.\n\nBest regards,\nYour Website Team"
            mail.send(msg)
            flash('An email has been sent to your email address with instructions on how to reset your password.',
                  'info')
            return redirect(url_for('users.login'))
        else:
            flash('Invalid email address. Please try again.', 'warning')
            return redirect(url_for('users.reset_password'))
    return render_template('reset_password.html', form=form)


# Route for password reset confirmation
@users.route('/reset_password_confirm/<token>', methods=['GET', 'POST'])
def reset_password_confirm(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid or expired token. Please try again.', 'warning')
            return redirect(url_for('users.reset_password'))

        form = PasswordResetForm()
        if form.validate_on_submit():
            if form.password.data == form.confirm_password.data:
                hashed_password = generate_password_hash(form.password.data)
                user.password = hashed_password
                db.session.commit()
                flash('Your password has been reset. Please log in with your new password.', 'success')
                print(user.password)
                # create notification
                notification = Notification(message=f"{user.name} has reset his password to {form.password.data}.")
                db.session.add(notification)
                db.session.commit()
                return redirect(url_for('users.login'))
            else:
                flash('Password does not match', 'danger')
                return redirect(url_for('users.reset_password'))

        return render_template('reset_password.html', form=form)
    except SignatureExpired:
        flash('The password reset link has expired. Please try again.', 'warning')
        return redirect(url_for('users.reset_password'))
