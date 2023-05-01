from __main__ import app
from models import db, Titles, Departments, Skills, Employees, Scores


def get_departments():

    departments = Departments.query.with_entities(Departments.Department).all()
    
    list = []
    for row in departments:
        list.append((row[0], row[0]))

    return list


def get_emp_departments():

    departments = Employees.query.with_entities(Employees.Department).distinct(Employees.Department).all()
    
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