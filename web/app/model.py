from flask_login import UserMixin
from app.exts import db






UserRole =db.Table(
'UserRoles',
db.Column('user_id',db.Integer(), db.ForeignKey('Users.id', ondelete='CASCADE')),
db.Column('role_id',db.Integer(), db.ForeignKey('Roles.id', ondelete='CASCADE'))
)



class User(db.Model, UserMixin):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean())

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='UserRoles', backref=db.backref("user", lazy="dynamic"))
    
    



# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('User', secondary='UserRoles', backref=db.backref("role", lazy="dynamic"))



'''
# # Define the UserRoles association table
class UserRole(db.Model):
    __tablename__ = 'UserRoles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('Users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('Roles.id', ondelete='CASCADE'))
'''



class Locker(db.Model):
    __tablename__ = 'Locker'
    id = db.Column(db.Integer(), primary_key=True)
    room = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50),nullable=False)
    


class TestRecord(db.Model):
    __tablename__ = 'TestRecord'
    id = db.Column(db.Integer, primary_key=True)
    runid = db.Column(db.Integer)
    project = db.Column(db.String(255), nullable=True)
    sn = db.Column(db.String(255), nullable=True)
    room = db.Column(db.String(50), nullable=False, unique=True)
    stage = db.Column(db.String(255), nullable=True)
    IP = db.Column(db.String(255), nullable=True)
    testMode = db.Column(db.String(255), nullable=True)
    OPID = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(255), nullable=True)
    startTime = db.Column(db.BigInteger, nullable=True)
    endTime = db.Column(db.BigInteger, nullable=True)





          



    
   



if __name__ == "__main__":
    pass


    '''
    db.create_all()

    user = User(username="Tom",password="111111")
    user2 = User(username="Ernie",password="1")

    role = Role(name="admin")
    role2 = Role(name="user")

    user.roles.append(role)
    user2.roles.append(role2)

    db.session.add(user)
    db.session.add(user2)
    db.session.commit()
    '''








