from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items

engine = create_engine('sqlite:///categoriesitem.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

# CREATE

# first Categories
myFirstCategories = Categories(name="Soccer")
session.add(myFirstCategories)
session.commit()
session.query(Categories).all()

# first Items
myFirstItem = Items(title="Zidane",
                    description="Zidane acted as the coach of Real Madrid "
                                "with three European Champion",
                    categories=myFirstCategories)
session.add(myFirstItem)
session.commit()
session.query(Items).all()


# READ
readfirst = session.query(Items).first()
print(readfirst.name)
