from flask import Blueprint, render_template, request
from flaskblog.models import BlogPost, current_year

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


@main.route("/contact")
def contact():
    return render_template("contact.html", year=current_year)
