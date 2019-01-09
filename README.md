#udacity_catalog_project
This is the project of a web application of Udacity Backend Nanodegree

So this project includes a build of a website for users to add, edit and delete items.

First, we run:
python database_setup.py
to build the database.

Second, we run:
python addallitems.py
to add all info into the database.

When running the whole application, we run
python project.py,
then open the browser in localhost:5000 to the main page.

Click on login button to login via google.

Url: localhost:5000/catalog/<catalog_name>/items/
To see all items under one catalog

Url:  localhost:5000/catalog/<catalog_name>/<item_name>/
To see the description for one specific item

Url: localhost:5000/catalog.json
To obtain all data in json format
