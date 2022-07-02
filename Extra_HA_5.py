#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from time import sleep
from datetime import date, datetime
import random, math

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///api.sqlite"
db = SQLAlchemy(app)
RECORDS_PER_PAGE = 3


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    creation_date = db.Column(db.Date, nullable=False, default=date.today())
    last_update_date = db.Column(db.Date, nullable=False, default=date.today())
    balance = db.Column(db.Float, nullable=False, default=0.0)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'creation_date': self.creation_date,
            'last_update_date': self.last_update_date,
            'balance': self.balance
        }


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False)
    account = db.relationship('Account',
                              backref=db.backref('payments', lazy=True))
    date = db.Column(db.DATETIME, default=datetime.now())
    amount = db.Column(db.Float, nullable=False, default=0.0)
    balance_before = db.Column(db.Float, nullable=False, default=0.0)
    type = db.Column(db.String, nullable=True)
    comment = db.Column(db.String, nullable=True)

    def serialize(self):
        return {
            'date': self.date,
            'amount': self.amount,
            'balance_before': self.balance_before,
            'type': self.type,
            'comment': self.comment
        }


def test_data(db):
    for i in range(20):
        balance = random.randint(0, 100)
        a = Account(name=f"User{i}", balance=balance)
        db.session.add(a)
        b_b = balance
        for j in range(random.randint(1, 50)):
            amount = random.randint(-1 * b_b, b_b)
            p = Payment(account=a, amount=amount, balance_before=b_b, type=random.randint(1, 3))
            b_b += amount
            db.session.add(p)
    db.session.commit()


def pay(db, account_id, page_id, per_page):
    result = []
    for record in db.engine.execute(f'SELECT * FROM payment where account_id= {account_id} order by id'):
        rec_dict = dict()
        rec_dict['id'] = record['id']
        rec_dict['date'] = record['date']
        rec_dict['amount'] = record['amount']
        rec_dict['balance'] = record['balance_before']
        rec_dict['type'] = record['type']
        rec_dict['comment'] = record['comment']
        result.append(rec_dict)
    pages = math.ceil(len(result) / per_page)
    page_id = pages if page_id > pages else page_id

    return result[(page_id - 1) * per_page: page_id * per_page], page_id, pages


def add_payment(db, p):
    query = f"select max(id), balance_before + amount as balance from payment where account_id = {p.account_id}"
    for b in db.engine.execute(query):
        p.balance_before = b['balance']
    db.session.add(p)
    db.session.commit()
    b = db.engine.execute(
        f'update account set balance=(select balance_before+ amount from payment where account_id={p.account_id} '
        f'ORDER BY id DESC LIMIT 1), last_update_date=DATE() where id={p.account_id}')
    return p

@app.before_first_request
def create_tables():
    db.create_all()


@app.route("/account/<id>", methods=['GET'])
def accounts(id):
    try:
        a = Account.query.get(id)
        return jsonify(a.serialize)
    except:
        return {'result': 'error'}


@app.route("/account/<id>/payments", methods=['GET'])
def payments(id):
    try:
        result = dict()
        page = request.args.get('page', 1, type=int)
        a, page, pages = pay(db, id, page, RECORDS_PER_PAGE)
        result['current_page'] = page
        result['per_page'] = RECORDS_PER_PAGE
        result['pages'] = pages
        result['payments'] = a
        return jsonify(result)
    except:
        return {'result': 'error'}


@app.route("/account/<id>/payments", methods=['POST'])
def payments_post(id):
    try:
        data = request.json
        p = Payment(account_id=id, amount=data['amount'], type=data['type'], comment=data['comment'])
        p = add_payment(db, p)
        return jsonify(p.serialize())
    except:
        return {'result': 'error'}


# In[ ]:




