from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items

engine = create_engine('sqlite:///categoriesitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/') # localhost: 8000 --> all categories
def categoriesMain():
	categories = session.query(Categories).all()
	output = ''
	for i in categories:
		output += i.name
		output += '</br>'
	return output

@app.route('/catalog/<catalog_name>/items/')
def catagoriesItem(catalog_name):
    output = ''
    category = session.query(Categories).filter_by(name=catalog_name).one()
    output += category.name
    output += '</br>'
    items = session.query(Items).filter_by(cat_id = category.id)
    for i in items:
		output += i.title
		output += '</br>'
    return output

@app.route('/catalog/<catalog_name>/<item_name>/')
def itemdescription(catalog_name, item_name):
    output = ''
    category = session.query(Categories).filter_by(name=catalog_name).one()
    items = session.query(Items).filter_by(cat_id = category.id)
    for i in items:
        if True:
            output += i.title
            output += '</br>'
            output += i.description
            output += '</br>'
            break
    return output


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
