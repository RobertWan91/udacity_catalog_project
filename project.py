from flask import Flask, render_template
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items

engine = create_engine('sqlite:///categoriesitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Main page
@app.route('/') # localhost: 8000 --> all categories
def categoriesMain():
	categories = session.query(Categories).all()
	return render_template('mainpage.html', categories=categories)

# Items list page
@app.route('/catalog/<catalog_name>/items/')
def catagoriesItem(catalog_name):
    output = ''
    category = session.query(Categories).filter_by(name=catalog_name).one()
    items = session.query(Items).filter_by(cat_id = category.id)
    return render_template('itempage.html', categories= category,items=items)

# Item description page
@app.route('/catalog/<catalog_name>/<item_name>/')
def itemdescription(catalog_name, item_name):
    output = ''
    category = session.query(Categories).filter_by(name=catalog_name).one()
    items = session.query(Items).filter_by(cat_id = category.id)
    for i in items:
        if i.title == item_name:
	        return render_template('describepage.html', items=i)

# Edit page
@app.route('/catalog/<item_name>/edit')
def editItem(item_name):
    return 'Edit page as first phase'

# Delete page
@app.route('/catalog/<item_name>/delete')
def deleteItem(item_name):
    return 'Delete page as first phase'

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
