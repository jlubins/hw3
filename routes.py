# import libraries

from flask import Flask, flash, render_template, request, url_for, redirect, session
from models import db, User, Follows, Post
from forms import LoginForm, SignupForm, NewpostForm
from passlib.hash import sha256_crypt

from flask_heroku import Heroku

app = Flask(__name__)
heroku = Heroku(app)

db.init_app(app)


# routes

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        session_user = User.query.filter_by(username=session['username']).first()

        # followers

        users_followed = Follows.query.filter_by(follower=session_user.uid).all()
        uids_followed = [f.following for f in users_followed] + [session_user.uid]
        followed_posts = Post.query.filter(Post.author.in_(uids_followed)).all()

        return render_template('index.html', title='Home', posts=followed_posts, session_username=session_user.username)
    else:
        all_posts = Post.query.all()
        return render_template('index.html', title='Home', posts=all_posts)




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('The username already exists. Please pick another one.')
            return redirect(url_for('signup'))

        else:
            user = User(username=username, password=sha256_crypt.hash(password))
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))

    else:
        return render_template('signup.html', title='Signup', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user is None or not sha256_crypt.verify(password, user.password):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        else:
            session['username'] = username
            return redirect(url_for('index'))
    else:
        return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    form = NewpostForm()

    if request.method == 'POST':
        session_user = User.query.filter_by(username=session['username']).first()
        content = request.form['content']
        new_post = Post(author=session_user.uid, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('newpost.html', title='Newpost', form=form)


@app.route('/profile/<username>', methods=['GET'])
def profile(username):
    profile_user = User.query.filter_by(
    username=username).first()
    profile_user_posts = Post.query.filter_by(author=profile_user.uid).all()

    if "username" in session:
        session_user = User.query.filter_by(username=session['username']).first()
        if Follows.query.filter_by(follower=session_user.uid, following=profile_user.uid).first():
            followed = True
        else:
            followed = False
        return render_template('profile.html', user=profile_user, posts=profile_user_posts, followed=followed)

@app.route('/search', methods=['POST'])
def search():
    user_to_query = request.form['search_box']
    return redirect(url_for('profile', username=user_to_query))

@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    session_user = User.query.filter_by(username=session['username']).first()
    user_to_follow = User.query.filter_by(username=username).first()
    new_follow =  Follows(follower=session_user.uid,following=user_to_follow.uid)

    db.session.add(new_follow)
    db.session.commit()
    return redirect(url_for('profile', username=username))

@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    session_user = User.query.filter_by(username=session['username']).first()
    user_to_unfollow = User.query.filter_by(username=username).first()
    delete_follow = Follows.query.filter_by(follower=session_user.uid,following=user_to_unfollow.uid).first()
    db.session.delete(delete_follow)
    db.session.commit()
    return redirect(url_for('profile', username=username))

if __name__ == "__main__":
    app.run(debug=True)
