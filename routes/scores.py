from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from models import db, Titles, Departments, Skills, Employees, Scores
from __main__ import app
from datetime import datetime
from views import TitleForm, DepartmentsForm, SkillsForm, EmployeesForm, ScoreForm
from common import *


# Scores
# -----------

@app.route("/scores", methods=["GET", "POST"])
def scores():

    results = db.session.query(
        Scores.ID,
        Employees.FullName,
        Skills.SkillName,
        Scores.Score,
        Scores.CreateDate,
        Scores.UpdateDate
        ).join(Skills, Skills.ID == Scores.Skill_ID)\
        .join(Employees, Employees.ID == Scores.Employee_ID)

    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
       
        results = db.session.query(
            Scores.ID,
            Employees.FullName,
            Skills.SkillName,
            Scores.Score,
            Scores.CreateDate,
            Scores.UpdateDate
            ).join(Skills, Skills.ID == Scores.Skill_ID)\
            .join(Employees, Employees.ID == Scores.Employee_ID)\
            .filter(Employees.FullName.like(search))
            
        return render_template("scores/scores-list.html", title = "Scores", results=results, tag=tag)

    return render_template("scores/scores-list.html", title = "Scores", results=results)



@app.route("/scores/add/", methods=["GET", "POST"])
def add_scores():

    if request.method == 'POST':

        record = Scores(
            Employee_ID = request.form['Employee'],
            Skill_ID = request.form['Skill'],
            Score = request.form['Score'],
            CreateDate=datetime.now(), 
            UpdateDate=datetime.now()
            )
        db.session.add(record)
        db.session.commit()

        return redirect("/scores")
    
    else:
        form = ScoreForm()
        form.Employee.choices = get_employees()
        form.Skill.choices = get_skills()
        form.process()

    return render_template("scores/score-edit-form.html", title = "Add Scores", form=form, action='add')


def get_departments():

    departments = Departments.query.with_entities(Departments.Department).all()
    
    list = []
    for row in departments:
        list.append((row[0], row[0]))

    return list
