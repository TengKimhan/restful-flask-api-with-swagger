# from sqlalchemy.orm import sessionmaker
# from database import User
# import os
# Session = sessionmaker(bind = os.environ.get("SQLALCHEMY_DB_URI"))
# session = Session()
# result = session.query(User).all()

# for row in result:
#    print ("Name: ",row.username, "Email:",row.email)

from database import db, User

user = User.query.get().all()
