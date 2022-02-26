from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context
from datetime import datetime

from sqlalchemy import ForeignKey
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///watch_list.db'
db = SQLAlchemy(app)


class User(db.Model):
    """
    id, name, email, password
    """
    # TODO add user score and status of private/public.
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(64))

    logs = db.relationship('UserMovie', back_populates='user')

#     def hash_password(self, password):
#         self.password_hash = custom_app_context.encrypt(password)

#     def verify_password(self, password):
#         return custom_app_context.verify(password, self.password_hash)
    def __repr__(self):
        return f'<{self.id}:{self.name}>'


class UserMovie(db.Model):
    # TODO: sepreate the log table from user_movie table (better performance)

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    movie_id = db.Column(db.Integer(), db.ForeignKey("movies.id"))

    current_season = db.Column(db.Integer(), nullable=False)
    current_episode = db.Column(db.Integer(), nullable=False)
    watch_time = db.Column(db.DateTime(), default=datetime.utcnow)
    note = db.Column(db.String(300))

    user = db.relationship('User', back_populates='logs')
    movie = db.relationship('Movie', back_populates='logs')

    def __repr__(self):
        return f'<{self.id},{self.movie}, season:{self.current_season}, episode:{self.current_episode} watched.>'


class Movie(db.Model):
    __tablename__ = 'movies'
    """ columns
        id name picture
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    info = db.relationship("MovieInfo", back_populates='movie')
    logs = db.relationship('UserMovie', back_populates='movie')

    def __repr__(self):
        return f"<{self.id}:{self.name}>"


class MovieInfo(db.Model):
    """ columns
        id season episode movie_id
    """

    __tablename__ = 'infos'
    id = db.Column(db.Integer(), primary_key=True)
    season = db.Column(db.Integer(), nullable=False)
    episode = db.Column(db.Integer(), nullable=False)
    movie_id = db.Column(db.Integer(), db.ForeignKey('movies.id'))

    movie = db.relationship('Movie', back_populates='info')

    def __repr__(self):
        return f'<{self.id}:{self.season}, {self.episode}>'


"""
In [3]: from app import User, Movie, UserMovie, MovieInfo                                                                                                                  

In [4]: yousef = User(name='usf.stdd', email='usf.stdd@gmail.com',password_hash='fvsvfvfjfkfnveeccc')

In [7]: yousef                                                                                                                                                             
Out[7]: <None:usf.stdd>

In [9]: yousef.logs                                                                                                                                                        
Out[9]: []

In [10]: m1 = Movie(name='matrix')                                                                                                                                         

In [11]: m1                                                                                                                                                                
Out[11]: <None:matrix>


In [7]: movie_details = MovieInfo(movie=m1, season=1 ,episode=10)                                                                                                          

In [8]: movie_details                                                                                                                                                      
Out[8]: None:1, 10

In [9]: m1.info                                                                                                                                                            
Out[9]: [None:1, 10]

In [10]: MovieInfo(movie=m1, season=2, episode=9)                                                                                                                          
Out[10]: None:2, 9

In [11]: m1.info                                                                                                                                                           
Out[11]: [None:1, 10, None:2, 9]


"""


@app.route('/')
def index():
    return 'descriptions of API endpoints'


if __name__ == "__main__":
    app.run(debug=True)
