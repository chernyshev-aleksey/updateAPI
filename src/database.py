from gino import Gino


db = Gino()


class User(db.Model):
    __tablename__ = 'Users'

    site = db.Column(db.BigInteger(), primary_key=True)
    id_vk = db.Column(db.BigInteger(), nullable=True)
    vk_name = db.Column(db.String(), nullable=True)
    site_login = db.Column(db.String())
    full_name = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(), nullable=True)


class MasterGroup(db.Model):
    __tablename__ = 'MasterGroupPaid'

    site_id = db.Column(db.BigInteger(), db.ForeignKey('Users.site'))
    paid_cost = db.Column(db.BigInteger())
    product = db.Column(db.String())
    subject = db.Column(db.String())
    _class = db.Column(db.String())
    data_created = db.Column(db.DateTime(), nullable=False)
    data_paid = db.Column(db.DateTime(), nullable=False)
    valid = db.Column(db.Boolean, nullable=False)
    unique_code = db.Column(db.String(), primary_key=True)
    type_pay = db.Column(db.String())


class Course(db.Model):
    __tablename__ = 'CoursePaid'

    site_id = db.Column(db.BigInteger(), db.ForeignKey('Users.site'))
    paid_cost = db.Column(db.BigInteger())
    product = db.Column(db.String())
    subject = db.Column(db.String())
    _class = db.Column(db.String())
    data_created = db.Column(db.DateTime(), nullable=False)
    data_paid = db.Column(db.DateTime(), nullable=False)
    valid = db.Column(db.Boolean, nullable=False)
    unique_code = db.Column(db.String(), primary_key=True)
    type_pay = db.Column(db.String())