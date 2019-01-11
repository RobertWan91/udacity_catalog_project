from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items, User

engine = create_engine('sqlite:///categoriesitem.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/'
                     '18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Categories: Soccer
category1 = Categories(user_id=1, name="Soccer")
session.add(category1)
session.commit()

# Items under Soccer
soccerItem1 = Items(user_id=1, title="Zidane",
                    description="Zidane was in Real Madrid",
                    categories=category1)
session.add(soccerItem1)
session.commit()

soccerItem2 = Items(user_id=1, title="Messi",
                    description=" best forward striker in Barcelona",
                    categories=category1)
session.add(soccerItem2)
session.commit()

# Categories: Basketball
category2 = Categories(user_id=1, name="Basketball")
session.add(category2)
session.commit()

basketItem1 = Items(user_id=1, title="Kobe Byrant",
                    description="best PG in Lakers",
                    categories=category2)
session.add(basketItem1)
session.commit()

basketItem2 = Items(user_id=1, title="Stephen Curry",
                    description="best 3 point shooter in NBA",
                    categories=category2)
session.add(basketItem2)
session.commit()

# Categories: Tennis
category3 = Categories(user_id=1, name="Tennis")
session.add(category3)
session.commit()

tennisItem1 = Items(user_id=1, title="Roger Ferderer",
                    description="best tennis player",
                    categories=category3)
session.add(tennisItem1)
session.commit()

# Categories: Ping Pong
category4 = Categories(user_id=1, name="Ping Pong")
session.add(category4)
session.commit()

pingpongItem1 = Items(user_id=1, title="Guoliang Liu",
                      description="best ping-pong player and coach",
                      categories=category4)
session.add(pingpongItem1)
session.commit()

# Categories: Formula 1
category5 = Categories(user_id=1, name="Formula 1")
session.add(category5)
session.commit()

F1Item1 = Items(user_id=1, title="Michael Schumacher",
                description="best F1 player",
                categories=category5)
session.add(F1Item1)
session.commit()

# Categories: Swimming
category6 = Categories(user_id=1, name="Swimming")
session.add(category6)
session.commit()

swimItem1 = Items(user_id=1, title="Michael Phelps",
                  description="best swimming player",
                  categories=category6)
session.add(swimItem1)
session.commit()

# Categories: Boxing
category7 = Categories(user_id=1, name="Boxing")
session.add(category7)
session.commit()

boxItem1 = Items(user_id=1, title="Michael Tyson",
                 description="great boxing prof",
                 categories=category7)
session.add(boxItem1)
session.commit()

# Categories: Running
category8 = Categories(user_id=1, name='Running')
session.add(category8)
session.commit()

runItem1 = Items(user_id=1, title="Usain Bolt",
                 description="best sprinter",
                 categories=category8)
session.add(runItem1)
session.commit()

# Categories: Badminton
category9 = Categories(user_id=1, name="Badminton")
session.add(category9)
session.commit()

badminItem1 = Items(user_id=1, title="Roger",
                    description="best tennis player",
                    categories=category3)
session.add(badminItem1)
session.commit()


print('All items added!')
