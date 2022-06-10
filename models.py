from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
 
login = LoginManager()
db = SQLAlchemy()
 
class User(UserMixin, db.Model):
    '''Table containing user authentication information.'''
    __tablename__ = 'users'
 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %s>' % self.email
 
    def set_password(self, password):
        '''Sets password of a user and saves it in database using hashing.'''
        self.password_hash = generate_password_hash(password)
     
    def check_password(self, password):
        '''Returns True if given password is the same as the one stored in database for the user 
        and False otherwise.
        As arguments takes:
        password - password to compare with information stored in database'''
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    '''Loads user identified with id.
    As arguments takes:
    id - identification number of user'''
    return User.query.get(int(id))
 
class Solution(db.Model):
    '''Table containing user saved solutions to Max3Sat problems.'''
    __tablename__ = "solutions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    percentage = db.Column(db.String(6), nullable=False)
    size_population = db.Column(db.Integer, nullable=False)
    number_populations = db.Column(db.Integer, nullable=False)
    number_parents = db.Column(db.Integer, nullable=False)
    probability_crossover = db.Column(db.Float, nullable=False)
    probability_gene_crossover = db.Column(db.Float, nullable=False)
    probability_smart_mutation = db.Column(db.Float, nullable=False)
    probability_gene_mutation =db.Column(db.Float, nullable=False)
    run_time = db.Column(db.Integer, nullable=False)
    solution = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (self.name, self.percentage, self.size_population, 
                self.number_populations, self.number_parents, self.probability_crossover, self.probability_gene_crossover, 
                self.probability_smart_mutation, self.probability_gene_mutation, self.run_time, self.solution)