from flask import Flask
from flask.cli import load_dotenv
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flaskblog.config import Config

ckeditor = CKEditor()
bootstrap = Bootstrap5()
load_dotenv()
# create the extension
db = SQLAlchemy()
admin = Admin(name="MY BLOG", template_mode='bootstrap3')
mail = Mail()

# Create db migration
migrate = Migrate()

# login manager
login_manager = LoginManager()

gravatar = Gravatar(size=80, rating='g', default='robohash', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)


def create_app(config_class=Config):
    app = Flask(__name__)
    # config objects for app
    app.config.from_object(config_class)

    ckeditor.init_app(app)
    bootstrap.init_app(app)

    # initialize the app with the extension mail
    mail.init_app(app)
    # initialize the app with the extension db
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # init gravatar
    gravatar.init_app(app)

    #  wrap the code that is causing the error in a with app.app_context():
    with app.app_context():
        # create database tables
        db.create_all()
        # IMPORT ROUTES: Here it goes the routes after all the packages
        from flaskblog.models import User, BlogPost, Comment, Notification
        from flaskblog.users.routes import users
        from flaskblog.posts.routes import posts
        from flaskblog.main.routes import main
        from flaskblog.errors.handlers import errors
        from flaskblog.main.admin.adminview import NotificationView, MyAdminIndexView, UserView, BlogPostView, \
            CommentView, NotificationTable

        app.register_blueprint(users)
        app.register_blueprint(posts)
        app.register_blueprint(main)
        app.register_blueprint(errors)

        # initiating the admin app
        admin.init_app(app, index_view=MyAdminIndexView())
        # add items to admin navbar
        admin.add_link(MenuLink(name='Notifications', url='/admin/notifications'))
        admin.add_view(NotificationView(name='Notifications', endpoint='notifications', category='Tools'))
        admin.add_view(UserView(User, db.session))
        admin.add_view(BlogPostView(BlogPost, db.session))
        admin.add_view(CommentView(Comment, db.session))
        admin.add_view(NotificationTable(Notification, db.session))

    return app
