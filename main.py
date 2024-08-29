from flask import Flask, render_template, jsonify, Blueprint, redirect, url_for, request
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, DateField, BooleanField, FloatField, IntegerField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task3.db'
db = SQLAlchemy(app)


class OrgStructure(db.Model):
    __tablename__ = 'Org_structure'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'id: {self.id} Name: {self.name}'


class Employee(db.Model):
    __tablename__ = 'Employee'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey(OrgStructure.id), nullable=False)
    cheif_id = db.Column(db.Integer, db.ForeignKey('Employee.id'), nullable=True)
    cheif = db.relationship('Employee', remote_side=[id], backref='employee')
    name = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Float, nullable=False)

    def __init__(self, dep_id, name, salary,  cheif_id=None):
        self.name = name
        self.salary = salary
        self.department_id = dep_id
        self.cheif_id = cheif_id

    def __repr__(self):
        return (f'(id: {self.id},\n department_id: {self.department_id},\n cheif_id: {self.cheif_id},\n name: {self.name},\n'
                f'salary: {self.salary})')



'''
    SELECT e.id, e.name, e.salary, c.id AS chief_id, c.name AS chief_name, c.salary AS chief_salary
    FROM Employee e
    JOIN Employee c ON e.cheif_id = c.id
    WHERE e.salary >= c.salary;
'''
def get_employees_earning_more_than_chief():
    Chief = db.aliased(Employee)
    query = db.session.query(Employee).join(
        Chief, Employee.cheif_id == Chief.id
    ).filter(
        Employee.salary >= Chief.salary
    ).all()

    return query


def fill_db():
    dep1 = OrgStructure(name='dep1')
    dep2 = OrgStructure(name='dep2')
    dep3 = OrgStructure(name='dep3')

    db.session.add(dep1)
    db.session.add(dep2)
    db.session.add(dep3)
    db.session.commit()

    e1 = Employee(name='e1', dep_id=dep1.id, salary=100, cheif_id=None)
    e2 = Employee(name='e2', dep_id=dep2.id, cheif_id=4, salary=1000)
    e3 = Employee(name='e3', dep_id=dep1.id, cheif_id=2, salary=99)
    e4 = Employee(name='e4', dep_id=dep3.id, cheif_id=1, salary=1000)
    e5 = Employee(name='e5', dep_id=dep1.id, cheif_id=2, salary=100)

    db.session.add(e1)
    db.session.add(e2)
    db.session.add(e3)
    db.session.add(e4)
    db.session.add(e5)
    db.session.commit()



with app.app_context():
    db.drop_all()
    db.create_all()
    fill_db()
    employees = get_employees_earning_more_than_chief()
    for employee in employees:
        print(f"Employee: {employee.name}, Salary: {employee.salary}")

# Second query
second_query = """
 SELECT o.name, SUM(e.salary) AS total_salary
    FROM Org_structure o
    JOIN Employee e ON o.id = e.department_id
    GROUP BY o.name
    ORDER BY total_salary DESC
    LIMIT 3;
"""
