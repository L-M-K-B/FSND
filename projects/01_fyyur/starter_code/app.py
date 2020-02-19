#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))

# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# --my comment-- Artist already exists


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)
    return d

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    for place in Venue.query.distinct(Venue.city):
        city_dict = {"city": place.city, "state": place.state}

        venues = []
        for venue in Venue.query.filter(Venue.city == place.city):
            venue_dict = {"id": venue.id, "name": venue.name}

            shows = Show.query.filter(Show.venue_id == venue.id).all()
            upcoming_shows = []
            for show in shows:
                if datetime.now() < show.start_time:
                    upcoming_shows.append(show.id)

            venue_dict["num_upcoming_shows"] = len(upcoming_shows)
            venues.append(venue_dict)

        city_dict["venues"] = venues
        data.append(city_dict)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form['search_term']
    suggestions = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(suggestions)
    }
    data = []
    for suggestion in suggestions:
        venue_dict = {
            "id": suggestion.id,
            "name": suggestion.name,
        }
        shows = Show.query.filter(Show.venue_id == suggestion.id).all()
        venue_dict["num_upcoming_shows"] = len(
            ["placeholder" for show in shows if datetime.now() < show.start_time])

        data.append(venue_dict)

    response["data"] = data

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    data = row2dict(Venue.query.get(venue_id))
    shows = Show.query.filter(Show.venue_id == venue_id).all()

    past_shows = []
    upcoming_shows = []
    for show in shows:
        if datetime.now() > show.start_time:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            pastShow_dict = {
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.isoformat()
            }
            past_shows.append(pastShow_dict)

        else:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            upcomingShow_dict = {
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.isoformat()
            }
            upcoming_shows.append(upcomingShow_dict)

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    try:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
        )
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue' +
              request.form['name']+'could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # replace with real data returned from querying the database
    data = []
    for artist in Artist.query.all():
        artist_dict = {"id": artist.id, "name": artist.name}
        data.append(artist_dict)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form['search_term']
    suggestions = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(suggestions)
    }
    data = []
    for suggestion in suggestions:
        artist_dict = {
            "id": suggestion.id,
            "name": suggestion.name,
        }
        shows = Show.query.filter(Show.artist_id == suggestion.id).all()
        artist_dict["num_upcoming_shows"] = len(
            ["placeholder" for show in shows if datetime.now() < show.start_time])

        data.append(artist_dict)

    response["data"] = data

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    data = row2dict(Artist.query.get(artist_id))
    shows = Show.query.filter(Show.artist_id == artist_id).all()

    past_shows = []
    upcoming_shows = []
    for show in shows:
        if datetime.now() > show.start_time:
            venue = Venue.query.filter_by(id=show.venue_id).first()
            pastShow_dict = {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.isoformat()
            }
            past_shows.append(pastShow_dict)

        else:
            venue = Venue.query.filter_by(id=show.venue_id).first()
            upcomingShow_dict = {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.isoformat()
            }
            upcoming_shows.append(upcomingShow_dict)

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # populate form with fields from artist with ID <artist_id>
    artist = Artist.query.filter_by(id=artist_id).first()
    form = ArtistForm(obj=artist)
    form.populate_obj(artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter_by(id=artist_id).first()
    try:
        artist.name = request.form['name'],
        artist.city = request.form['city'],
        artist.state = request.form['state'],
        artist.phone = request.form['phone'],
        artist.genres = request.form.getlist('genres'),
        artist.website = request.form['website'],
        artist.facebook_link = request.form['facebook_link'],
        artist.image_link = request.form['image_link']
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # populate form with values from venue with ID <venue_id>
    venue = Venue.query.filter_by(id=venue_id).first()
    form = VenueForm(obj=venue)
    form.populate_obj(venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.filter_by(id=venue_id).first()
    try:
        venue.name = request.form['name'],
        venue.address = request.form['address'],
        venue.city = request.form['city'],
        venue.state = request.form['state'],
        venue.phone = request.form['phone'],
        venue.genres = request.form.getlist('genres'),
        venue.website = request.form['website'],
        venue.facebook_link = request.form['facebook_link'],
        venue.image_link = request.form['image_link']
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    try:
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link']
        )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist' +
              request.form['name']+'could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # replace with real venues data.
    # ==> according to mock data this is not required: num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    shows = Show.query.all()
    for show in Show.query.all():
        show_dict = {"venue_id": show.venue_id,
                     "artist_id": show.artist_id, "start_time": show.start_time.isoformat()}

        venue = Venue.query.filter_by(id=show.venue_id).first()
        show_dict["venue_name"] = venue.name

        artist = Artist.query.filter_by(id=show.artist_id).first()
        show_dict["artist_name"] = artist.name
        show_dict["artist_image_link"] = artist.image_link

        data.append(show_dict)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead
    try:
        show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
