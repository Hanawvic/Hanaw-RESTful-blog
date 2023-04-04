from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from flaskblog import db
from flask_mail import Message
from flaskblog import mail
from flaskblog.models import BlogPost, Comment, current_year, Notification
from flaskblog.posts.forms import CreatePostForm, CommentForm
from datetime import date

posts = Blueprint("posts", __name__)


@posts.context_processor
def inject_current_year():
    return {"year": current_year}


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            abort(403)  # raise 403 error if the user is not authenticated or not an admin
        return f(*args, **kwargs)

    return decorated_function


@posts.route("/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def show_post(post_id):
    requested_post = BlogPost.query.get_or_404(post_id)
    form = CommentForm()
    form.comment_text.render_kw = {"placeholder": "Enter your comment!"}
    if form.validate_on_submit():
        new_comment = Comment(text=form.comment_text.data, comment_author=current_user, parent_post=requested_post)
        db.session.add(new_comment)
        db.session.commit()
        flash(message=f"Your comment for: '{requested_post.title}' has been published!", category="success")
        # Create a new notification
        notification = Notification(message=f'{current_user} commented the post {requested_post.title}.')
        db.session.add(notification)
        db.session.commit()
        # Sending mail notification
        msg = Message("Blog Notification", recipients=[requested_post.author.email])
        # Only send notification if sm1 else has commented your post

        post_url = url_for('posts.show_post', post_id=requested_post.id, _external=True)
        if current_user.name != requested_post.author.name:
            msg.body = f"Subject:New notification!\n\n{current_user} commented your post {requested_post.title}.Here" \
                       f"'s the link to your post: {post_url}"
            mail.send(msg)
        return redirect(url_for("posts.show_post", post_id=post_id))
    # paginate comments
    page = request.args.get('page', 1, type=int)
    post_comments = Comment.query.filter_by(parent_post=requested_post).order_by(Comment.timestamp.desc()) \
        .paginate(page=page, per_page=3)

    return render_template("post.html", post=requested_post, form=form, post_comments=post_comments)


@posts.route("/new-post", methods=["GET", "POST"])
@login_required
def create_new_post():
    form = CreatePostForm()
    form.title.render_kw = {"placeholder": "Title of the post"}
    form.subtitle.render_kw = {"placeholder": "Choose a Subtitle"}
    form.body.render_kw = {"placeholder": "Description of the post"}
    form.img_url.render_kw = {"placeholder": "Link of the post image"}
    form.author.render_kw = {"placeholder": f"{current_user.name}"}

    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            post_date=date.today().strftime("%B %d, %Y"),
            author=current_user
        )

        try:
            db.session.add(new_post)
            db.session.commit()
            flash(message=f"A new blogpost: '{new_post.title}' added successfully!", category="success")
            # Create a new notification
            notification = Notification(message=f'{current_user} posted new post called {new_post.title}.')
            db.session.add(notification)
            db.session.commit()
            # Sending mail notification
            post_url = url_for('posts.show_post', post_id=new_post.id, _external=True)
            msg = Message("Blog Notification", recipients=[current_user.email])
            msg.body = f"Subject:New notification!\n\n Welcome to Hanaw's Blog! " \
                       f"You posted a new post called {new_post.title}. Here's the link to your post: {post_url}"
            mail.send(msg)

            return redirect(url_for("main.get_all_posts"))

        except IntegrityError:
            db.session.rollback()
            flash(message=f"The post '{new_post.title}' already exists!", category="danger")
            return redirect(url_for("main.get_all_posts"))

    return render_template("make-post.html", form=form)


@posts.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    requested_post = BlogPost.query.get_or_404(post_id)

    # auto-populate the fields in the WTForm with the blog post's data. This way the user doesn't have to type out
    # their blog post again
    edit_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        author=requested_post.author.name,  # author is the current_user
        img_url=requested_post.img_url,
        body=requested_post.body
    )
    if edit_form.validate_on_submit():
        requested_post.title = edit_form.title.data
        requested_post.subtitle = edit_form.subtitle.data
        requested_post.author.name = edit_form.author.data  # update the author name
        requested_post.img_url = edit_form.img_url.data
        requested_post.body = edit_form.body.data
        db.session.commit()
        flash(message=f"The blogpost has been successfully edited!", category="success")
        # Create a new notification
        notification = Notification(message=f'{current_user} edited the post {requested_post.title}.')
        db.session.add(notification)
        db.session.commit()
        return redirect(url_for("posts.show_post", post_id=requested_post.id))

    return render_template("make-post.html", is_edit=True, form=edit_form)


@posts.route("/delete/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_only  # apply the @admin_only decorator
def delete_post(post_id):
    post_to_delete = BlogPost.query.get_or_404(post_id)
    db.session.delete(post_to_delete)
    flash(message=f"{post_to_delete.title} has been deleted successfully!", category="warning")

    # Create a new notification
    notification = Notification(message=f'{current_user} deleted the post: {post_to_delete.title}.')
    db.session.add(notification)
    db.session.commit()
    return redirect(url_for("main.get_all_posts"))


@posts.route("/delete-comment/<int:comment_id>/<int:current_page>", methods=["GET", "POST"])
@login_required
def delete_comment(comment_id, current_page):
    comment_to_delete = Comment.query.options(joinedload('parent_post')).get(comment_id)
    db.session.delete(comment_to_delete)
    flash(message="Your comment has been deleted successfully!", category="warning")

    # # Query the remaining comments and update their ids
    # all_comments = Comment.query.filter_by(post_id=comment_to_delete.parent_post.id).order_by(Comment.id).all()
    # for i, comment in enumerate(all_comments, start=1):
    #     comment.id = i
    #     db.session.add(comment)

    db.session.commit()
    text = f'{current_user} deleted the comment: {comment_to_delete.id} ' \
           f'from the post:{comment_to_delete.parent_post.title}.'
    # Create a new notification
    notification = Notification(message=text)
    db.session.add(notification)
    db.session.commit()
    # Check if there are any comments left on the current page
    per_page = 3
    remaining_comments_count = Comment.query.filter_by(post_id=comment_to_delete.parent_post.id).count()
    remaining_pages_count = (remaining_comments_count - 1) // per_page + 1
    if current_page > remaining_pages_count:
        current_page = remaining_pages_count

    # Check if there are any comments left for the post
    if remaining_comments_count == 0:
        return redirect(url_for("main.get_all_posts"))

    return redirect(url_for("posts.show_post", post_id=comment_to_delete.parent_post.id, page=current_page))
