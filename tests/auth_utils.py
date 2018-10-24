from mod_auth.models import Users, AccountType
from database import db
from run import app


def login(client, email, password, submit='password'):
    with client.session_transaction() as sess:
        admin_user = Users.query.filter(
            Users.email == app.config['ADMIN_EMAIL']).first()

        if admin_user is None:
            admin_user = Users(email=email,
                               name=app.config['ADMIN_NAME'],
                               password=app.config['ADMIN_PWD'],
                               account_type=AccountType.admin)

            db.session.add(admin_user)
            db.session.commit()
        sess['user_id'] = admin_user.id
