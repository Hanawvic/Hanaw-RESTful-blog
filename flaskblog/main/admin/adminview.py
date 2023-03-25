from flask import render_template
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.template import macro
from flask_login import current_user
from flaskblog.models import Notification


# Add views to the admin interface here

class NotificationView(BaseView):
    @expose('/')
    def index(self):
        notifications = Notification.query.order_by(Notification.timestamp.desc()).limit(20).all()
        return self.render('admin/notifications.html', notifications=notifications, macro=macro)


# only an admin can access the admin panel
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if user doesn't have access
        return render_template("errors/403.html"), 403


# Add administrative views here
class UserView(ModelView):
    column_list = ('name', 'email', 'password', 'confirmed', 'posts')
    form_columns = ('name', 'email', 'password', 'confirmed')
    column_filters = ['name', 'email']


class BlogPostView(ModelView):
    column_list = ('title', 'subtitle', 'date', 'body', 'img_url', 'author')
    form_columns = ('title', 'subtitle', 'date', 'body', 'img_url', 'author')
    column_filters = ['title', 'subtitle', 'date']


class CommentView(ModelView):
    column_list = ('text', 'comment_author', 'parent_post', 'timestamp')
    form_columns = ('text', 'comment_author', 'parent_post')
    column_filters = ['text', 'parent_post.title', 'comment_author.name']


class NotificationTable(ModelView):
    column_list = ('id', 'message', 'timestamp')
    form_columns = ('id', 'message', 'timestamp')
    column_filters = ['id', 'message', 'timestamp']


