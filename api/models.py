import datetime

from gino import Gino
from passlib.hash import pbkdf2_sha256


db = Gino()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(
        db.Unicode(30), nullable=False, unique=True)
    password = db.Column(db.Unicode(), nullable=False)

    def verify_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)

    @staticmethod
    def hash_password(raw_password):
        return pbkdf2_sha256.hash(raw_password)


class Joke(db.Model):
    __tablename__ = 'jokes'
    __table_args__ = db.UniqueConstraint('text', 'user_id')

    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Unicode(400), nullable=False)
    user_id = db.Column(None, db.ForeignKey('users.id'), nullable=False)

    def is_joke_owner(self, user):
        return self.user_id == user.id


class ServiceLog(db.Model):
    __tablename__ = 'servicelogs'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(None, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.Unicode(15), nullable=False)
    # I know about now() method doesnt store timezone, but i dont know,
    # how to store with tzinfo.
    request_time = db.Column(db.DateTime(), default=datetime.datetime.now)


async def main():
    # TODO: Need to deprecate.

    await db.set_bind('postgresql://postgres@postgres/gino')
    await db.gino.create_all()
