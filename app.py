# export FLASK_ENV=development
# flask run --port 4000

import functools
from tabnanny import check
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import ForeignKey


from werkzeug.security import generate_password_hash, check_password_hash
import re
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

    # TODO! there is no need to these two column
    # for now set theme to zero
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
    # TODO: change name of these columns to watched_
    current_season = db.Column(db.Integer(), nullable=False)
    current_episode = db.Column(db.Integer(), nullable=False)

    last_status = db.relationship('MovieUser', back_populates='logs')
    # TODO: problem: same movie user season episode can be commited!


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
    # curl -X POST -H 'content-type: application/json' -d '{"name":"name", "password":"password", "email":"jooo3@gmail.com"}' 'http://localhost:4000/api/movielist/v1.1/register'

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
    # curl -u u1:u1 -X POST -H 'content-type: application/json' -d '{"name":"movie1", "details":"[6,5,10]"}' 'http://localhost:4000/api/movielist/v1.1/addmovie'

    req = request.get_json()
    current_user = auth.current_user()

    if 'details' in req:
        name, details = req['name'], req['details']

        new_movie = Movie(name=name)
        for season, episodeCount in enumerate(details):
            new_movie.info.append(
                MovieInfo(season=season, episode=episodeCount))

        new_movie_user = MovieUser(
            watched_season=-1, watched_episode=-1, movie=new_movie)
        current_user.last_status.append(new_movie_user)

        new_movie_user_log = MovieUserLog(
            current_season=-1, current_episode=-1)

        new_movie_user.logs.append(new_movie_user_log)

        db.session.add(new_movie)
        db.session.commit()

        return {'status': 'movie added!'}
    elif 'movie_id' in req:
        movie_id = req['movie_id']
        print(movie_id)
        new_movie_user = MovieUser(
            user_id=current_user.id, movie_id=movie_id, watched_season=-1, watched_episode=-1)

        new_movie_user_log = MovieUserLog(
            current_season=-1, current_episode=-1)

        new_movie_user.logs.append(new_movie_user_log)
        db.session.add(new_movie_user)
        db.session.commit()

        return {'status': 'movie added!'}


@app.route('/api/movielist/v1.1/movieslog', methods=['GET', 'POST'])
@auth.login_required
def getmovie():
    # curl -u name:password 'http://localhost:4000/api/movielist/v1.1/movieslog'

    current_user = auth.current_user()

    def destruct_movie_user(movie_user):
        user_id = movie_user.user_id
        movie_id = movie_user.movie_id
        # s = movie_user.watched_season
        # e = movie_user.watched_episode
        movie = movie_user.movie
        note = movie_user.note
        movie_name = movie.name
        season_episode_details = [(i.season, i.episode) for i in movie.info]
        # TODO! question: i which order the value retrived from the db.
        return {'user_id': user_id, 'movie_id': movie_id, 'name': movie_name,
                'season_episode_details': season_episode_details, 'note': note}

    def destruct_movie_user_log(movie_user_log):
        user_id = movie_user_log.user_id
        movie_id = movie_user_log.movie_id
        watch_time = movie_user_log.watch_time
        season = movie_user_log.current_season
        episode = movie_user_log.current_episode
        return {'user_id': user_id, 'movie_id': movie_id,
                'season': season, 'episode': episode, 'watch_time': watch_time}

    if request.method == 'GET':
        watchlist = [destruct_movie_user(m)
                     for m in current_user.last_status]
        # !TODO: done!
        # expected return :
        # a dict like :movie_id :{'season':0, 'episode':0, 'watch_time':0}, ... }

        def reshape_watchlist(a, b):
            key = b['movie_id']
            a[key] = {'name': b['name'],
                      'season_episode_details': b['season_episode_details'],
                      'note': b['note']}

            return a

        reshaped_watchlist = functools.reduce(reshape_watchlist, watchlist, {})

        user_log = MovieUserLog.query.filter_by(
            user_id=auth.current_user().id).all()
        log = [destruct_movie_user_log(m) for m in user_log]

        def reshape_log(a, b):
            key = b['movie_id']
            print(key)
            if key not in a:
                a[key] = []
            a[key].append({'season': b['season'],
                           'episode': b['episode'],
                           'watch_time': b['watch_time']})
            return a

        reshaped_log = functools.reduce(reshape_log, log, {})

        return {"watchlist": reshaped_watchlist, "watchlist_log": reshaped_log}
    if request.method == "POST":
        '''
        curl -u u1:u1 -X POST -H 'content-type: application/json'
        -d '{"movie_id":"3", "watched_season":"3" , "watched_episode":"2" }'
        'http://localhost:4000/api/movielist/v1.1/movieslog'


        curl -u name:password -X POST -H 'content-type: application/json' -d '{"movie_id":"3", "watched_season":"3" , "watched_episode":"2" }' 'http://localhost:4000/api/movielist/v1.1/movieslog'

        '''
        request_body = request.get_json()
        user = auth.current_user()
        # TODO! redundant. in addmovie route -1 was set.
        # movie_user = MovieUser.query.filter_by(
        #     user=user, movie_id=request_body['movie_id']).first()

        # movie_user.watched_season = request_body['current_season']
        # movie_user.watched_episode = request_body['current_episode']
        # db.session.add(movie_user)
        log = MovieUserLog(user_id=user.id, movie_id=request_body['movie_id'],
                           current_season=request_body['watched_season'], current_episode=request_body['watched_episode'])

        db.session.add(log)
        db.session.commit()
        return {'watch_time': log.watch_time}


@app.route('/api/movielist/v1.1/signin')
@auth.login_required
def signin():
    #     ➜  ~ curl -u u1:u1 http://localhost:4000/api/movielist/v1.1/signin
    # {
    #   "name": "u1"
    # }
    user = auth.current_user()
    return {'name': user.name}


@app.route('/api/movielist/v1.1/movies', methods=['POST'])
@auth.login_required
def get_movies():
    # curl -u name:password -X POST -H 'content-type: application/json'
    # -d '{"movie_name":"movie1"}'
    # 'http://localhost:4000/api/movielist/v1.1/movies'

    def destruct_movie_user(movie):

        movie_id = movie.id
        movie_name = movie.name
        season_episode_details = {i.season: i.episode
                                  for i in movie.info}
        # TODO! question: i which order the value retrived from the db.
        return {'movie_id': movie_id, 'name': movie_name,
                'season_episode_details': season_episode_details}

    if request.method == 'POST':
        data = request.get_json()
        # TODO!
        # this isn't an efficient way to do this task
        movies = Movie.query.all()
        filtered_movies = [movie for movie in movies if re.search(
            data['movie_name'], movie.name)]
        return {movie.name: destruct_movie_user(movie) for movie in filtered_movies}

        #


@app.route('/api/movielist/v1.1/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    if request.method == 'POST':
        pass


if __name__ == "__main__":
    app.run(debug=True, )
