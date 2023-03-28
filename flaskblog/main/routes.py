from flask import Blueprint, render_template, request
from flask_mail import Message
from flaskblog import mail
from flaskblog.models import BlogPost, current_year
from flaskblog.config import Config
main = Blueprint("main", __name__)


@main.route('/')
def get_all_posts():
    page = request.args.get('page', default=1, type=int)
    # sort posts by id in descending order and then paginate the results to display up to 5 posts per page.
    posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=5)
    print(posts)
    return render_template("index.html", all_posts=posts, year=current_year)


@main.route("/about")
def about():
    return render_template("about.html", year=current_year)


@main.route('/contact/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        success_message = "Successfully sent your message"
        data = request.form
        user_name = data["username"]
        user_email = data["email"]
        user_phone = data["phone"]
        user_message = data["message"]

        # Sending mail notification
        msg = Message("Contact message", recipients=[Config.MAIL_USERNAME])
        msg.body = f"Subject:New Message!\n\nName: {user_name}\nEmail: {user_email}\nPhone: {user_phone}\nMessage: {user_message}"
        mail.send(msg)

        return render_template("contact.html", year=current_year, message=success_message)

    else:
        message = "Contact Me"
        return render_template("contact.html", year=current_year, message=message)
