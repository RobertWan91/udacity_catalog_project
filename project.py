from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items

engine = create_engine('sqlite:///categoriesitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Main page
@app.route('/')  # localhost: 8000 --> all categories
def categoriesMain():
    categories = session.query(Categories).all()
    return render_template('mainpage.html', categories=categories)


# Items list page
@app.route('/catalog/<catalog_name>/items/')
def catagoriesItem(catalog_name):
    category = session.query(Categories).filter_by(name=catalog_name).one()
    items = session.query(Items).filter_by(cat_id=category.id)
    return render_template('itempage.html', categories=category, items=items)


# Item description page
@app.route('/catalog/<catalog_name>/<item_name>/')
def itemdescription(catalog_name, item_name):
    category = session.query(Categories).filter_by(name=catalog_name).one()
    items = session.query(Items).filter_by(cat_id=category.id)
    for i in items:
        if i.title == item_name:
            return render_template('describepage.html', items=i)


# Edit page
@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    edititem = session.query(Items).filter_by(title=item_name).one()
    editcategory = session.query(Categories).filter_by(id=edititem.cat_id).one()
    if request.method == 'POST':
        if request.form['title']:
            edititem.title = request.form['title']
        if request.form['description']:
            edititem.description = request.form['description']
        session.add(edititem)
        session.commit()
        return redirect(url_for('itemdescription', catalog_name=editcategory.name, item_name=edititem.title))
    else:
        return render_template('edititem.html', catalog_name=editcategory.name, item_name=edititem.title,
                               item_description=edititem.description)


# Delete page
@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    itemToDelete = session.query(Items).filter_by(title=item_name).one()
    categoryDelete = session.query(Categories).filter_by(id=itemToDelete.cat_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('catagoriesItem', catalog_name=categoryDelete.name))
    else:
        return render_template('deleteitem.html', catalog_name=categoryDelete.name, item_name=itemToDelete.title)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
