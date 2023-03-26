import smtplib

from flask import Blueprint, render_template, request
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
        print(data["username"])
        print(data["email"])
        print(data["phone"])
        print(data["message"])

        # Sending mail notification
        send_email(name=data["username"],
                   email=data["email"],
                   phone=data["phone"],
                   message=data["message"])

        return render_template("contact.html", year=current_year, message=success_message)

    else:
        message = "Contact Me"
        return render_template("contact.html", year=current_year, message=message)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message!\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=Config.MAIL_USERNAME, password=Config.MAIL_PASSWORD)
        connection.sendmail(from_addr=Config.MAIL_USERNAME,
                            to_addrs="hanawvoker@gmail.com",
                            msg=email_message)
