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

    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(64))
    ppstatus = db.Column(db.Boolean(), default=False, nullable=False)
    score = db.Column(db.Integer(), default=0, nullable=False)

    last_status = db.relationship('MovieUser', back_populates='user')

#     def hash_password(self, password):
#         self.password_hash = custom_app_context.encrypt(password)

#     def verify_password(self, password):
#         return custom_app_context.verify(password, self.password_hash)
    def __repr__(self):
        return f'<{self.id}:{self.name}>'


class MovieUser(db.Model):

    user_id = db.Column(db.Integer(), db.ForeignKey(
        "user.id"), primary_key=True)
    movie_id = db.Column(db.Integer(), db.ForeignKey(
        "movies.id"), primary_key=True)

    watched_season = db.Column(db.Integer(), nullable=False)
    watched_episode = db.Column(db.Integer(), nullable=False)

    watch_time = db.Column(db.DateTime(), default=datetime.utcnow)
    note = db.Column(db.String(500))

    user = db.relationship('User', back_populates='last_status')
    movie = db.relationship('Movie', back_populates='last_status')
    logs = db.relationship('MovieUserLog', back_populates='last_status')

    def __repr__(self):
        return f'<user-movie:{self.user_id}-{self.movie_id},{self.movie}, season:{self.watched_season}, episode:{self.watched_episode} watched.>'


class MovieUserLog(db.Model):
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['user_id', 'movie_id'], ['movie_user.user_id', 'movie_user.movie_id']),

    )
    id = db.Column(db.Integer(), primary_key=True)

    user_id = db.Column(db.Integer(), nullable=False)
    movie_id = db.Column(db.Integer(), nullable=False)
    watch_time = db.Column(db.DateTime(), default=datetime.utcnow)

    current_season = db.Column(db.Integer(), nullable=False)
    current_episode = db.Column(db.Integer(), nullable=False)

    last_status = db.relationship('MovieUser', back_populates='logs')


class Movie(db.Model):
    __tablename__ = 'movies'
    """ columns
        id name picture
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    info = db.relationship("MovieInfo", back_populates='movie')
    last_status = db.relationship('MovieUser', back_populates='movie')

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
In [4]: from app import User, Movie, MovieUser, MovieInfo,MovieUserLog, db                                                                                                               

In [5]: u1 = User(name='yousef', email='usf.stdd@gmail.com', password_hash='password_hash')                                                             

In [6]: db.session.add(u1)                                                      

In [7]: db.session.commit()                                                     

In [8]: m1 = Movie(name='matrix')                                               

In [9]: db.session.new                                                          
Out[9]: IdentitySet([])

In [10]: db.session.add(m1)                                                     

In [11]: db.session.new                                                         
Out[11]: IdentitySet([<None:matrix>])

In [12]: db.session.commit()                                                    

In [13]: m1                                                                     
Out[13]: <1:matrix>

In [18]: mu = MovieUser(user=u1, movie=m1, watched_season=0, watched_episode=0 )  

In [11]: mu                                                                     
Out[11]: <user-movie:None-None,<1:matrix>, season:0, episode:0 watched.>

In [12]: m1                                                                     
Out[12]: <1:matrix>

In [13]: db.session.add(mu)                                                     

In [14]: db.session.commit()                                                    

In [15]: db.session.new                                                         
Out[15]: IdentitySet([])

In [16]: u1                                                                     
Out[16]: <1:yousef>

In [17]: u1.last_status                                                         
Out[17]: [<user-movie:1-1,<1:matrix>, season:0, episode:0 watched.>]

In [19]: mu.movie                                                               
Out[19]: <1:matrix>

In [20]: mu                                                                     
Out[20]: <user-movie:1-1,<1:matrix>, season:0, episode:0 watched.>

In [21]: type(mu)                                                               
Out[21]: app.MovieUser

In [22]: u1.last_status                                                         
Out[22]: [<user-movie:1-1,<1:matrix>, season:0, episode:0 watched.>]

In [26]: type(u1.last_status[0])                                                
Out[26]: app.MovieUser

In [27]: u1.last_status[0].movie                                                
Out[27]: <1:matrix>

In [29]: mulog = MovieUserLog(last_status=mu, current_season=1, current_episode=1)                                                                     

In [30]: mulog                                                                  
Out[30]: <MovieUserLog (transient 139832421025440)>

In [31]: db.session.add(mulog)                                                  

In [32]: db.session.new                                                         
Out[32]: IdentitySet([<MovieUserLog (transient 139832409596160)>, <MovieUserLog (transient 139832421025440)>])

In [33]: db.session.commit()                                                                                                              

In [34]: mulog.last_status                                                                                                                
Out[34]: <user-movie:1-1,<1:matrix>, season:0, episode:0 watched.>

In [35]: mulog.last_status.user                                                                                                           
Out[35]: <1:yousef>


"""


@app.route('/')
def index():
    return 'descriptions of API endpoints'


if __name__ == "__main__":
    app.run(debug=True)
