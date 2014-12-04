from app import db, app
import flask.ext.whooshalchemy as whooshalchemy

ROLE_USER = 0
ROLE_ADMIN = 1
ACCESS_PRIVATE = 0
ACCESS_PUBLIC = 1

class User(db.Model):
    id =         db.Column(db.Integer, primary_key = True)
    google_id =  db.Column(db.String(1024), unique = True)
    fb_id =      db.Column(db.String(1024), unique = True)
    twitter_id = db.Column(db.String(1024), unique = True)
    name =       db.Column(db.String(64))
    email =      db.Column(db.String(120), index = True, unique = True)
    role =       db.Column(db.SmallInteger, default = ROLE_USER)
    topics =     db.relationship('Topic', backref = 'author', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<ID:%r, User:%r, email:%r, google_id:%r, fb_id:%r, twitter_id:%r, role:%r>' % \
                (self.id, self.name, self.email, self.google_id, self.fb_id, self.twitter_id, self.role)

class Topic(db.Model):
    id =       db.Column(db.Integer, primary_key = True)
    topic =    db.Column(db.String(80))
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'))
    snippets = db.relationship('Snippet', order_by='desc(Snippet.timestamp)', backref = 'topic', lazy = 'dynamic')

    def __repr__(self):
        return '<ID:%r, Topic:%r>' % (self.id, self.topic)

class Snippet(db.Model):
    __searchable__ = ['title', 'description', 'code']

    id =          db.Column(db.Integer, primary_key = True)
    title =       db.Column(db.String(256))
    description = db.Column(db.Text)
    code =        db.Column(db.Text)
    timestamp =   db.Column(db.DateTime)
    ref_count =   db.Column(db.Integer)
    language  =   db.Column(db.String(30))
    access =      db.Column(db.Boolean)
    creator_id =  db.Column(db.Integer)
    topic_id  =   db.Column(db.Integer, db.ForeignKey('topic.id'))

    def __init__(self, title, description, code, timestamp, topic, creator_id, language, access=ACCESS_PRIVATE):
        self.title = title
        self.description = description
        self.code = code
        self.timestamp = timestamp
        self.ref_count = 1
        self.language = language
        self.access = access
        self.creator_id = creator_id
        self.topic = topic

    def inc_ref(self):
        self.ref_count += 1;

    def dec_ref(self):
        self.ref_count -= 1;

    def __repr__(self):
        return '<ID:%r, title:%r, description:%r, code:%r, timestamp:%r, ref_count:%r, access:%r, creator_id:%r>' % \
                (self.id, self.title, self.description, self.code, self.timestamp,
                 self.ref_count, self.language, self.access, self.creator_id)

whooshalchemy.whoosh_index(app, Snippet)
