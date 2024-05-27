from datetime import datetime
from flask import Flask, flash, render_template, redirect, url_for, request
from forms import LoginForm, RegForm
from flask_login import LoginManager, UserMixin, logout_user, login_user,  current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess-password-really-dont-try'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:catman@localhost:5433/postgres' 
login = LoginManager(app)
db = SQLAlchemy(app=app)

followers = db.Table('followers',
db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), index=True)
    second_name = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(255))
    followed = db.relationship( 'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.login)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(
            followers.c.follower_id == self.id
        ).join(
            User, (User.id == Post.user_id)
        ).add_columns(
            User.login.label('author_login'),
            Post.body,
            Post.timestamp
        ).order_by(
            Post.timestamp.desc()
        ).all()

        own_posts = Post.query.filter_by(
            user_id=self.id
        ).join(
            User, (User.id == Post.user_id)
        ).add_columns(
            User.login.label('author_login'),
            Post.body,
            Post.timestamp
        ).order_by(
            Post.timestamp.desc()
        ).all()

        return followed + own_posts
    
    def count_followers(self):
        return self.followers.count()

    def count_followed(self):
        return self.followed.count()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


with app.app_context():
    db.create_all()

@app.route('/') 
@app.route('/index')
def index(): 
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user:
            redirect(url_for('cabinet', login=user.login))
    return render_template('base.html') 


@app.route('/signin', methods=['GET', 'POST']) 
def signin(): 
    form = LoginForm() 
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user:
            return redirect(url_for('cabinet', login=user.login))
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return redirect('signin')
        login_user(user, remember=form.remember_me.data) 
        return redirect(url_for('cabinet', login=user.login))
    return render_template('signin.html',  form=form) 


@app.route('/signup', methods=['GET', 'POST']) 
def signup(): 
    form = RegForm()
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user:
            return redirect(url_for('cabinet', login=user.login))
    if form.validate_on_submit():
        if not (User.query.filter_by(login=form.login.data).first() is not None):
            user = User()
            user.login = form.login.data
            user.name = form.name.data
            user.second_name = form.second_name.data
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Вы успешно зарегистированы!')
            return redirect('index')
        else:
            flash('Пользователь с таким логином уже существует')
    return render_template('signup.html',  form=form) 

@app.route('/cab/<login>')
@login_required
def cabinet(login):
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        if user.login == login:
            return render_template('cab.html',
                                    user=user,
                                    is_auth=True)
        else:
            user_page = User.query.filter_by(login=login).first_or_404()
            is_followed = current_user.is_following(user_page)
            return render_template('cab.html',
                                    user=user_page,
                                    is_followed=is_followed,
                                    is_auth=False)
    flash('Пользователь не аутентифицирован')
    return redirect(url_for('index'))

@app.route('/cab')
@login_required
def owncabinet():
    return redirect(url_for('cabinet', login=current_user.login))

@app.route('/publish_post', methods=['POST'])
@login_required
def publish_post():
    post_content = request.form.get('post_content')
    if not post_content:
        flash('Пост не может быть пустым', 'error')
        return redirect(url_for('cabinet', login=current_user.login))
    new_post = Post(body=post_content, user_id = current_user.id)
    db.session.add(new_post)
    db.session.commit()
    flash('Пост успешно опубликован', 'success')
    return redirect(url_for('cabinet', login=current_user.login))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/follow/<login>')
@login_required
def follow(login):
    user = User.query.filter_by(login=login).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(login))
        redirect(url_for('cabinet', login=current_user.login))
    if user == current_user:
        flash('Вы не можете подписаться на себя')
        return redirect(url_for('cabinet', login=login))
    current_user.follow(user)
    db.session.commit()
    flash('Вы подписались на {}!'.format(login))
    return redirect(url_for('cabinet', login=login))

@app.route('/unfollow/<login>')
@login_required
def unfollow(login):
    user = User.query.filter_by(login=login).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(login))
        redirect(url_for('cabinet', login=current_user.login))
    if user == current_user:
        flash('Вы не можете отписаться от себя')
        return redirect(url_for('cabinet', login=login))
    current_user.unfollow(user)
    db.session.commit()
    flash('Вы отписались от {}.'.format(login))
    return redirect(url_for('cabinet', login=login))

@app.route('/users')
@login_required
def users():
    logins = User.query.with_entities(User.login).all()
    logins = [login[0] for login in logins]
    return render_template('users.html', users_logins=logins)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect('index')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
    