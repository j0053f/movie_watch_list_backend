# export FLASK_ENV=development
# flask run --port 4000
from tabnanny import check
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import ForeignKey

from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///watch_list.db'
db = SQLAlchemy(app)

auth = HTTPBasicAuth()


@auth.verify_password
def verify_auth(username, password):
    current_user = User.query.filter_by(name=username).first()
    # if current_user and password == current_user.password_hash:
    if current_user and check_password_hash(current_user.password_hash, password):
        return current_user


class User(db.Model):
    """
    id, name, email, password
    """

    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(64))
    # private public status
    ppstatus = db.Column(db.Boolean(), default=False, nullable=False)
    score = db.Column(db.Integer(), default=0, nullable=False)

    last_status = db.relationship('MovieUser', back_populates='user')

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
    name = db.Column(db.String(80), nullable=False, unique=True)

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


@auth.error_handler
def auth_error(status):
    res = make_response(jsonify({'actual_status_code': status}), 403)
    return res


@app.route('/')
def index():
    return 'descriptions of API endpoints'


@app.route('/api/movielist/v1.1/<string:username>')
@auth.login_required
def home_page(username):
    return f'hello, {auth.current_user()}'


@app.route('/api/movielist/v1.1/register', methods=['post'])
def register():
    # TODO add email verification
    # curl -X POST -H 'content-type: application/json' -d '{"name":"yosuef", "password":"this is my password keep it safe", "email":"jooo3@gmail.com"}' 'http://localhost:4000/api/movielist/v1.1/register'

    req = request.get_json()
    name, email, password = req['name'], req['email'], req['password']
    new_user = User(name=name, email=email,
                    password_hash=generate_password_hash(password))

    db.session.add(new_user)
    db.session.commit()
    return {"status": 'created'}


@app.route('/api/movielist/v1.1/addmovie', methods=['POST'])
@auth.login_required
def addmovie():
    # curl -u u1:u1 -X POST -H 'content-type: application/json'
    # -d '{"name":"movie1", "details":"[6,5,10]"}'
    # 'http://localhost:4000/api/movielist/v1.1/addmovie'

    req = request.get_json()
    name, details = req['name'], req['details']

    new_movie = Movie(name=name)
    for season, episodeCount in enumerate(details):
        new_movie.info.append(MovieInfo(season=season, episode=episodeCount))

    current_user = auth.current_user()

    new_movie_user = MovieUser(
        watched_season=0, watched_episode=0, movie=new_movie)
    current_user.last_status.append(new_movie_user)

    new_movie_user_log = MovieUserLog(current_season=0, current_episode=0)
    new_movie_user.logs.append(new_movie_user_log)

    db.session.add(new_movie)
    db.session.commit()
    import pdb
    pdb.set_trace()
    return 'ohh'


@app.route('/api/movielist/v1.1/signin')
@auth.login_required
def signin():
    #     ➜  ~ curl -u u1:u1 http://localhost:4000/api/movielist/v1.1/signin
    # {
    #   "name": "u1"
    # }
    user = auth.current_user()
    return {'name': user.name}

    # curl -X POST -H 'content-type: application/json' -d '{"name":"yousef", "password":"1234"}' 'http://localhost:4000/api/movielist/v1.1/signin'
    #  {
    #    "authenticated": false
    #  }

    # req = request.get_json()
    # name, password = req['name'], req['password']
    # try:
    #     user_record = User.query.filter_by(name=name).first()
    #     if check_password_hash(user_record.password_hash, password):
    #         return {'is_authenticated': True}
    #     return {'is_authenticated': False}
    # except:
    #     return {'is_authenticated': False}


@app.route('/api/movielist/v1.1/movies', methods=['GET'])
@auth.login_required
def get_movies():
    pass


@app.route('/api/movielist/v1.1/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    if request.method == 'POST':
        pass


if __name__ == "__main__":
    app.run(debug=True, )
