# coding: utf-8

from app.extensions import db


class BaseModelMixin:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def save(self):
        db.session.add(self)
        db.session.commit()


class Account(db.Model, BaseModelMixin):

    __tablename__ = 'account'

    fb_messenger_id = db.Column(db.BigInteger, unique=True)

    imgur_account_id = db.Column(db.Integer)
    imgur_username = db.Column(db.String(400))
    imgur_token = db.Column(db.String(200))
    imgur_refresh_token = db.Column(db.String(200))

    images = db.relationship('Image', backref='account', lazy='dynamic')

    @classmethod
    def get_or_create(cls, user_id):
        account = cls.query.filter_by(fb_messenger_id=user_id).first()
        if account:
            return account, False

        account = cls()
        account.fb_messenger_id = user_id
        account.save()

        return account, True

    def is_loggined_to_imgur(self):
        return bool(self.imgur_token)


tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('picture_id', db.Integer, db.ForeignKey('picture.id'))
)


class Image(db.Model, BaseModelMixin):
    __tablename__ = 'picture'

    facebook_url = db.Column(db.String(4000))

    imgur_id = db.Column(db.String(1000))
    imgur_url = db.Column(db.String(4000))

    uploaded = db.Column(db.Boolean, default=False)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    tags = db.relationship('Tag', secondary=tags,
                           backref=db.backref('pictures', lazy='dynamic'))


class Tag(db.Model, BaseModelMixin):
    __tablename__ = 'tag'

    text = db.Column(db.String(1000))

    def __repr__(self):
        return "Tag: {}".format(self.text)

    @classmethod
    def from_str_list(cls, str_list):
        objects = list(Tag.query.filter(Tag.text.in_(str_list)))
        to_create = set(str_list).difference(set([tag.text for tag in objects]))
        created = []
        for item in to_create:
            t = Tag()
            t.text = item
            db.session.add(t)
            created.append(t)

        db.session.commit()
        return created+objects