### INF601 - Advanced Programming in Python
### Jeremy McKowski
### Mini Project 3

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('movies', __name__)

@bp.route('/')
def index():
    db = get_db()
    movies = db.execute(
        'SELECT m.id, title, date_watched, rating, notes, created, author_id, username'
        ' FROM movie m JOIN user u ON m.author_id = u.id'
        ' ORDER BY date_watched DESC'
    ).fetchall()
    return render_template('movies/index.html', movies=movies)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        date_watched = request.form['date_watched']
        rating = request.form['rating']
        notes = request.form['notes']
        error = None

        if not title:
            error = 'Movie title is required.'
        elif not date_watched:
            error = 'Date watched is required.'
        elif not rating:
            error = 'Rating is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO movie (title, date_watched, rating, notes, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, date_watched, rating, notes, g.user['id'])
            )
            db.commit()
            return redirect(url_for('movies.index'))

    return render_template('movies/create.html')

def get_movie(id, check_author=True):
    movie = get_db().execute(
        'SELECT m.id, title, date_watched, rating, notes, created, author_id, username'
        ' FROM movie m JOIN user u ON m.author_id = u.id'
        ' WHERE m.id = ?',
        (id,)
    ).fetchone()

    if movie is None:
        abort(404, f"Movie id {id} doesn't exist.")

    if check_author and movie['author_id'] != g.user['id']:
        abort(403)

    return movie

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    movie = get_movie(id)

    if request.method == 'POST':
        title = request.form['title']
        date_watched = request.form['date_watched']
        rating = request.form['rating']
        notes = request.form['notes']
        error = None

        if not title:
            error = 'Movie title is required.'
        elif not date_watched:
            error = 'Date watched is required.'
        elif not rating:
            error = 'Rating is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE movie SET title = ?, date_watched = ?, rating = ?, notes = ?'
                ' WHERE id = ?',
                (title, date_watched, rating, notes, id)
            )
            db.commit()
            return redirect(url_for('movies.index'))

    return render_template('movies/update.html', movie=movie)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_movie(id)
    db = get_db()
    db.execute('DELETE FROM movie WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('movies.index'))