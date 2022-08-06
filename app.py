#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import abort, jsonify, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#



# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = str(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  print("get venue create")
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue_form = VenueForm(request.form)
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    new_venue = Venue(
      name = venue_form.name.data,
      city = venue_form.city.data,
      state = venue_form.state.data,
      address = venue_form.address.data,
      phone = venue_form.phone.data,
      image_link = venue_form.image_link.data,
      facebook_link = venue_form.facebook_link.data,
      website_link = venue_form.website_link.data,
      seeking_talent = venue_form.seeking_talent.data,
      seeking_description = venue_form.seeking_description.data,
      genres = ','.join(venue_form.genres.data)
    )

    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on successful db insert, flash success
    flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be listed.')
  else:
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  print(venues)

  if len(venues) == 0:
    abort(404)

  unique_city_states = Venue.query.distinct(Venue.city, Venue.state).all()
  print(unique_city_states)

  index = 0
  for ucs in unique_city_states:
    #filter venue table by city and state
    venues_per_city_state = Venue.query.filter(Venue.city == ucs.city, Venue.state == ucs.state)
    venues = []

    for vpcs in venues_per_city_state:
      current_time = datetime.now()
      #filter venue table and show table for upcoming shows 
      upcoming_shows = db.session.query(Venue, Show).filter((Show.venue_id == vpcs.id) & 
      (Show.venue_id == Venue.id) & (Show.start_time > current_time)).all()

      #count upcoming shows per venue
      num_upcoming_shows = len(upcoming_shows)
      
      #create venue per city state
      venue = {
        "id": vpcs.id,
        "name": vpcs.name,
        "num_upcoming_shows": num_upcoming_shows
      }
      #append each venue
      venues.append(venue)

    #assign venue per city state
    unique_city_states[index].venues = venues
    index = index + 1
  
  print(unique_city_states[0].venues)

  return render_template('pages/venues.html', areas=unique_city_states)

#  Search Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', None)
 
  venues = Venue.query.filter(
    Venue.name.ilike("%{}%".format(search_term))
  ).all()
  count_venues = len(venues)

  response={
    "count": count_venues,
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


#  Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  print(venue)

  if venue is None:
    abort(404)

  current_time = datetime.now()
  upcoming_shows = db.session.query(Artist.name, Artist.id, Artist.image_link, Show.start_time).filter((Show.venue_id == venue_id) & (Show.artist_id == Artist.id) & (Show.start_time > current_time)).all()
  past_shows = db.session.query(Artist.name, Artist.id, Artist.image_link, Show.start_time).filter((Show.venue_id == venue_id) & (Show.artist_id == Artist.id) & (Show.start_time < current_time)).all()

  venue.upcoming_shows = upcoming_shows
  venue.past_shows = past_shows
  venue.past_shows_count = len(past_shows)
  venue.upcoming_shows_count = len(upcoming_shows)
  # split string to a list
  venue.genres = venue.genres.split(',')  

  return render_template('pages/show_venue.html', venue=venue)

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_to_update = Venue.query.get(venue_id)

  if venue_to_update is None:
    abort(404)

  venue={
    "id": venue_to_update.id,
    "name": venue_to_update.name,
    "genres": venue_to_update.genres,
    "city": venue_to_update.city,
    "state": venue_to_update.state,
    "phone": venue_to_update.phone,
    "address": venue_to_update.address,
    "website_link": venue_to_update.website_link,
    "facebook_link": venue_to_update.facebook_link,
    "seeking_talent": venue_to_update.seeking_talent,
    "seeking_description": venue_to_update.seeking_description,
    "image_link": venue_to_update.image_link
  }

  form = VenueForm(data=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)

  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = ",".join(form.genres.data)
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.address = form.address.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    print(venue.shows)
    for show in venue.shows:
      db.session.delete(show)

    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return jsonify({'success': True})

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  artist_form = ArtistForm(request.form)
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  print(artist_form.name.data,)
  try:
    new_artist = Artist(
      name = artist_form.name.data,
      city = artist_form.city.data,
      state = artist_form.state.data,
      phone = artist_form.phone.data,
      image_link = artist_form.image_link.data,
      facebook_link = artist_form.facebook_link.data,
      website_link = artist_form.website_link.data,
      seeking_venue = artist_form.seeking_venue.data,
      seeking_description = artist_form.seeking_description.data,
      genres = ','.join(artist_form.genres.data)
    )

    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on successful db insert, flash success
    flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be listed.')
  else:
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  all_artist = db.session.query(Artist.id, Artist.name).all()
  print(all_artist)

  if len(all_artist) == 0:
    abort(404)

  return render_template('pages/artists.html', artists=all_artist)


#  Search Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', None)
 
  artists = Artist.query.filter(
    Artist.name.ilike("%{}%".format(search_term))
  ).all()
  count_artist = len(artists)

  response={
    "count": count_artist,
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  print(artist)

  if artist is None:
    abort(404)

  current_time = datetime.now()
  upcoming_shows = db.session.query(Venue.name, Venue.id, Venue.image_link, Show.start_time).filter((Show.artist_id == artist_id) & (Show.venue_id == Venue.id) & (Show.start_time > current_time)).all()
  past_shows = db.session.query(Venue.name, Venue.id, Venue.image_link, Show.start_time).filter((Show.artist_id == artist_id) & (Show.venue_id == Artist.id) & (Show.start_time < current_time)).all()

  print(past_shows)
  artist.upcoming_shows = upcoming_shows
  artist.past_shows = past_shows
  artist.past_shows_count = len(past_shows)
  artist.upcoming_shows_count = len(upcoming_shows)
  # split string to a list
  artist.genres = artist.genres.split(',')
  
  return render_template('pages/show_artist.html', artist=artist)

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist_to_update = Artist.query.get(artist_id)

  if artist_to_update is None:
    abort(404)

  artist={
    "id": artist_to_update.id,
    "name": artist_to_update.name,
    "genres": artist_to_update.genres,
    "city": artist_to_update.city,
    "state": artist_to_update.state,
    "phone": artist_to_update.phone,
    "website_link": artist_to_update.website_link,
    "facebook_link": artist_to_update.facebook_link,
    "seeking_venue": artist_to_update.seeking_venue,
    "seeking_description": artist_to_update.seeking_description,
    "image_link": artist_to_update.image_link
  }

  form = ArtistForm(data=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)

  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.genres = ",".join(form.genres.data)
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show_form = ShowForm(request.form)
  
  error = False
  try:
    show = Show(
      artist_id=show_form.artist_id.data,
      venue_id=show_form.venue_id.data,
      start_time=show_form.start_time.data
    )

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return flash('An error occurred. Show could not be listed.')
  else:
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  show_venues = db.session.query(Venue.id, Venue.name).filter(Venue.id == Show.venue_id).all()
  show_artists = db.session.query(Artist.id, Artist.name, Artist.image_link).filter(Artist.id == Show.artist_id).all()
  print(shows)
  print(show_venues)
  print(show_artists)

  index = 0
  for sv in show_venues:
    shows[index].venue_id = sv.id
    shows[index].venue_name = sv.name
    index = index + 1

  index = 0
  for sa in show_artists:
    shows[index].artist_id = sa.id
    shows[index].artist_name = sa.name
    shows[index].artist_image_link = sa.image_link
    index = index + 1

  print(shows[0].venue_name)
  print(shows[0].venue_id)

  if len(shows) == 0:
    abort(404)

  return render_template('pages/shows.html', shows=shows)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
