"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson
import pdb
import math 
# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

    def predict_score(self, movie_id):
        """For a movie, predict's user's score."""

        # generate list of ratings objects: all ratings provided by user
        p_user_movie_ids = [rating.movie_id for rating in self.ratings]

        # instantiate movie object; build list of ids for all the users who have rated this movie
        movie = Movie.query.get(movie_id)
        other_users = [rating.user for rating in movie.ratings]

        final_pearson = [0,0]

        # z_user refers to user we are comparing primary user to 
        for z_user in other_users:
            pairs = []
            
            # check if each of z_user's ratings is for a movie that p_user has rated
            for z_rating in z_user.ratings:
                if z_rating.movie_id in p_user_movie_ids:
                    p_rating = Rating.query.filter(Rating.user_id == self.user_id, Rating.movie_id == z_rating.movie_id).one()
                    pairs.append((p_rating.score, z_rating.score))

            # check if p_user and z_user have any overlap. If so:
            if pairs:
                r = pearson(pairs)
                if abs(r) > abs(final_pearson[1]):
                    final_pearson = [z_user.user_id, r]

        # get z_user rating object for movie in question
        z_movie_rating = Rating.query.filter(Rating.user_id == final_pearson[0], Rating.movie_id == movie_id).one()
        print "the pearson coefficient r is ", r
        print final_pearson
        print "user z gave this movie", z_movie_rating.score

        # return score prediction, if Pearson is pos or neg
        if final_pearson[1] > 0:
            score_prediction = final_pearson[1] * z_movie_rating.score
        else: 
            score_prediction = -(final_pearson[1]) * (6-z_movie_rating.score)
        
        print score_prediction

        return round(score_prediction, 1)



class Movie(db.Model):
    """List of movies from MovieLens 100K"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id=%s title=%s>" % (self.movie_id, self.title)



class Rating(db.Model):
    """List of ratings by users."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    movie = db.relationship("Movie",
            backref=db.backref("ratings", order_by=rating_id))

    user = db.relationship("User",
            backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating rating_id=%s movie_title=%s score=%s>" % (self.rating_id, self.movie.title, self.score)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
