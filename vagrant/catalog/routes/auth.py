import flask
import httplib2
import json
import random
import requests
import string
from flask import flash
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session as login_session
from flask import url_for
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import User


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


DBSession = sessionmaker()
DBH = DBSession()

auth = flask.Blueprint('auth', __name__)


def make_external(url):
    return urljoin(request.url_root, url)


@auth.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@auth.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.header['Content-Type'] = 'application/json'
        return response

    # confirm valid token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # abort if access token info error
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # verify access token user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token user id does not match give user id"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # if stored_credentials is not None and gplus_id == stored_gplus_id:
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'

    # store access token in session
    login_session['provider'] = 'google'
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # get user information
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(login_session['email'])
    if user_id == None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['name'])
    print "done!"
    return output


# Disconnect user
@auth.route("/gdisconnect")
def gdisconnect():
    # only disconnet a connected user
    access_token = login_session.get('access_token')
    # check if connected user
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # revoke current token
    url = ('https://accounts.google.com/a/oauth2/revoke?token=%s' % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # reset session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['name']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
                json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@auth.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            # del login_session['gplus_id']
            # del login_session['access_token']

            # del login_session['name']
            # del login_session['email']
            # del login_session['picture']
            # del login_session['user_id']

        del login_session['provider']

        flash("You have successfully been logged out.")
        return redirect(url_for('category.showCategoryMasterDetail'))
    else:
        flash("Not logged in")
        return redirect(url_for('category.showCategoryMasterDetail'))


def getUserId(email):
    try:
        user = DBH.query(User).filter_by(email=email).one()
    except NoResultFound:
        return None

    return user.id


def getUserInformation(user_id):
    try:
        user = DBH.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        return None

    return user


def createUser(login_session):
    user = User(
        name=login_session['name'],
        email=login_session['email'],
        picture=login_session['picture'])

    DBH.add(user)
    DBH.commit()
    DBH.refresh(user)
    return user.id
