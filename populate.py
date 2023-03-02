from models import *
from datetime import datetime


def populate():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        user1 = User("User 1", "1234567890", "user1@example.com", "password1")
        user2 = User("User 2", "2345678901", "user2@example.com", "password2")
        user3 = User("User 3", "2345678901", "user3@example.com", "password3")
        user4 = User("User 4", "2345678901", "user4@example.com", "password4")
        user5 = User("User 5", "2345678901", "user5@example.com", "password5")
        user6 = User("User 6", "2345678901", "user6@example.com", "password6")
        user7 = User("User 7", "2345678901", "user7@example.com", "password7")
        user8 = User("User 8", "2345678901", "user8@example.com", "password8")
        user9 = User("User 9", "2345678901", "user9@example.com", "password9")
        user10 = User("User 10", "2345678901", "user10@example.com", "password10")
        user11 = User("User 11", "2345678901", "user11@example.com", "password11")
        user12 = User("User 12", "2345678901", "user12@example.com", "password12")
        user13 = User("User 13", "2345678901", "user13@example.com", "password13")
        user14 = User("User 14", "2345678901", "user14@example.com", "password14")

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)
        db.session.add(user5)
        db.session.add(user6)
        db.session.add(user7)
        db.session.add(user8)
        db.session.add(user9)
        db.session.add(user10)
        db.session.add(user11)
        db.session.add(user12)
        db.session.add(user13)
        db.session.add(user14)
        db.session.commit()
        group1 = Group("Group 1", user1.id, datetime.now(), datetime.now(), True, 100.0, 50.0)
        group2 = Group("Group 2", user2.id, datetime.now(), datetime.now(), False, 200.0, 100.0)
        db.session.add(group1)
        db.session.add(group2)
        db.session.commit()
        users = User.query.all()
        for i in range(0, 6):
            db.session.add(Friend(users[i].id, group1.id, None, "Banana"))
        for i in range(7, 13):
            db.session.add(Friend(users[i].id, group2.id, None, "Maçã"))
        db.session.commit()


populate()
