from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, app
from flask import session as login_session
import string
import random
import logging
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app.secret_key = 'super_secret_key'


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App Udacity"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items, User

engine = create_engine('sqlite:///categoriesitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON_items endpoint
@app.route('/catalog.json')
def categoriesMainJSON():
    categories_all = session.query(Categories).all()
    # items_all = [session.query(Items).filter_by(cat_id=category.id) for category in categories_all]
    rev_sub = []
    rev_json = {'Category': rev_sub}
    for i in categories_all:
        i_item = session.query(Items).filter_by(cat_id=i.id).all()
        i_json_item = [element_item.serialize for element_item in i_item]
        if i_json_item:
            element_sub = {'id': i.id, 'name': i.name, 'items': i_json_item}
        else:
            element_sub = {'id': i.id, 'name': i.name}
        rev_sub.append(element_sub)
    return jsonify(rev_json)


# Main page
@app.route('/')  # localhost: 8000 --> all categories
def categoriesMain():
    categories = session.query(Categories).all()
    last_items = session.query(Items).order_by(Items.id.desc()).limit(10)
    if 'username' not in login_session:
        return render_template('publicmainpage.html', categories=categories, last_items=last_items)
    else:
        return render_template('mainpage.html', categories=categories, last_items=last_items)


# Items list page
@app.route('/catalog/<catalog_name>/items/')
def catagoriesItem(catalog_name):
    category = session.query(Categories).filter_by(name=catalog_name).one()
    items = session.query(Items).filter_by(cat_id=category.id)
    return render_template('itempage.html', categories=category, items=items)


# Item description page
@app.route('/catalog/<item_name>/')
# def itemdescription(catalog_name, item_name):
def itemdescription(item_name):
    # category = session.query(Categories).filter_by(name=catalog_name).one()
    # items = session.query(Items).filter_by(cat_id=category.id)
    items = session.query(Items).filter_by(title=item_name)
    # creator = getUserID(items.user_id)
    for i in items:
        if i.title == item_name:
            creator = getUserInfo(i.user_id)
            if 'username' not in login_session or creator.id != login_session['user_id']:
                return render_template('publicdescribepage.html', items=i)
            else:
                return render_template('describepage.html', items=i)


# Add new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItems():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Categories).filter_by(name=request.form['category']).one()
        items = session.query(Items).filter_by(cat_id=category.id)
        newItem = Items(title=request.form['title'], description=request.form['description'], cat_id=category.id,
                        user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return render_template('itempage.html', categories=category, items=items)
    else:
        return render_template('newitem.html')


# Edit page
@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    edititem = session.query(Items).filter_by(title=item_name).one()
    editcategory = session.query(Categories).filter_by(id=edititem.cat_id).one()
    if request.method == 'POST':
        if request.form['title']:
            edititem.title = request.form['title']
        if request.form['description']:
            edititem.description = request.form['description']
        session.add(edititem)
        session.commit()
        flash("Item/description has been edit!")
        return redirect(url_for('itemdescription', catalog_name=editcategory.name, item_name=edititem.title))
    else:
        return render_template('edititem.html', catalog_name=editcategory.name, item_name=edititem.title,
                               item_description=edititem.description)


# Delete page
@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Items).filter_by(title=item_name).one()
    categoryDelete = session.query(Categories).filter_by(id=itemToDelete.cat_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item/description has been deleted!")
        return redirect(url_for('catagoriesItem', catalog_name=categoryDelete.name))
    else:
        return render_template('deleteitem.html', catalog_name=categoryDelete.name, item_name=itemToDelete.title)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
