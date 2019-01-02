from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'super_secret_key'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items

engine = create_engine('sqlite:///categoriesitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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


# Add new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItems():
    if request.method == 'POST':
        category = session.query(Categories).filter_by(name=request.form['category']).one()
        items = session.query(Items).filter_by(cat_id=category.id)
        newItem = Items(title=request.form['title'], description=request.form['description'], cat_id=category.id)
        session.add(newItem)
        session.commit()
        return render_template('itempage.html', categories=category, items=items)
    else:
        return render_template('newitem.html')


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
        flash("Item/description has been edit!")
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
        flash("Item/description has been deleted!")
        return redirect(url_for('catagoriesItem', catalog_name=categoryDelete.name))
    else:
        return render_template('deleteitem.html', catalog_name=categoryDelete.name, item_name=itemToDelete.title)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
