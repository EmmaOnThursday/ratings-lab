"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    
    # if user is logged in, create variable from their session user id
    session_user_id = session.get('user')

    # if user is logged in, pass email address to homepage.html template
    # if no user is logged in, pass empty email variable to template
    if session_user_id:
        current_user = User.query.get(session_user_id)
        user_email = current_user.email
    else:
        user_email = None

    return render_template("homepage.html", session_user_id=user_email)


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route('/users/<int:user_id>')
def user_details(user_id):
    """Show user details."""

    # create instance of user based on user_id from url
    display_user = User.query.get(user_id)

    return render_template('user.html', display_user=display_user)


@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by('title').all()

    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<int:movie_id>')
def movie_details(movie_id):
    """Show movie details."""

    # instantiate Movie object based on movie_id provided by URL
    movie = Movie.query.get(movie_id)

    # if user is logged in, create variable from their session user id
    session_user_id = session.get('user')

    return render_template("movie.html", movie=movie, session_user_id=session_user_id)


@app.route('/movies/<int:movie_id>/user-rating', methods=['POST'])
def display_form(movie_id):

    # extract form info
    score = request.form.get('score')

    # rating = db.session.query(Rating).filter(Rating.user_id == session['user'], Rating.movie_id == movie_id).first()
    rating = Rating.query.filter(Rating.user_id == session['user'], Rating.movie_id == movie_id).first()
    
    # if user has already submitted a score for this movie, then update DB
    if rating:
        rating.score = score
    # else, add new rating to DB
    else:
        rating = Rating(user_id=session['user'], movie_id=movie_id, score=score)
        db.session.add(rating)
        
    db.session.commit()

    flash(("Your rating of {} has been saved!").format(score))

    return redirect(url_for('movie_details', movie_id=movie_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for returning users."""

    # checks if form has been submitted; if so...
    if request.method == 'POST':
        email = request.form.get('email')
        password  = request.form.get('password')

        # try to instantiate user based on email & pw provided in form
        # user = db.session.query(User).filter(User.email == email, User.password == password).all()
        user = User.query.filter(User.email == email, User.password == password).first()

        # if user is created, log them in & redirect to homepage
        if user: 
            flash('You were successfully logged in')
            session['user'] = user.user_id
            return redirect(url_for('index'))
        # if user is not in DB, prompt them to try to log in again
        else: 
            flash('Email and password do not match records.')
            return render_template('login-page.html')

    return render_template('login-page.html')


@app.route('/new-user-signup', methods=['GET', 'POST'])
def new_user_signup():
    """Form for new user signups."""

    # if form has been submitted...
    if request.method == 'POST':
        #save all variables from form
        email = request.form.get('email')
        password  = request.form.get('password')
        zipcode = request.form.get('zipcode')
        age = int(request.form.get('age'))

        # try to instantiate user based on email from form
        user = User.query.filter(User.email == email).all()

        # if user already in DB, redirect to login page
        if user != []:
            flash("Looks like you've already signed up! Please log in.")
            return redirect(url_for('login'))
        # if user does not exist, create & commit to DB
        else:
            new_user = User(email=email, password=password, zipcode=zipcode, age=age)
            print new_user
            db.session.add(new_user)
            db.session.commit()
            flash("Welcome to MovieJudgements!")
            return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    """Logout the current user."""

    # remove user_id from flask session dictionary; redirect to homepage
    session.pop('user', None)
    flash("You've logged out.")

    return redirect(url_for('index'))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

