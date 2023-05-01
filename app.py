from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from datetime import datetime
# from views import TitleForm, DepartmentsForm, SkillsForm, EmployeesForm, ScoreForm

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

from models import db, Titles, Departments, Skills, Employees, Scores

from routes.employees import *
from routes.deparments import *
from routes.skills import *
from routes.titles import *
from routes.scores import *
from routes.reports import *

@app.route("/")
def index():
    return redirect('/employees')


def get_departments():

    departments = Departments.query.with_entities(Departments.Department).all()
    
    list = []
    for row in departments:
        list.append((row[0], row[0]))

    return list


def get_titles():

    titles = Titles.query.with_entities(Titles.Title).all()
    
    list = []
    for row in titles:
        list.append((row[0], row[0]))

    return list


def get_skills():

    skills = Skills.query.with_entities(Skills.ID, Skills.SkillName).all()

    list = []
    for row in skills:
        list.append((row[0], row[1]))

    return list


def get_employees():

    employees = Employees.query.with_entities(Employees.ID, Employees.FullName).all()

    list = []
    for row in employees:
        list.append((row[0], row[1]))

    return list


if __name__ == "__main__":
    # app.app_context().push()
    # db.create_all()
    app.run()