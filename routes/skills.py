from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from models import db, Titles, Departments, Skills, Employees, Scores
from __main__ import app
from datetime import datetime
from views import TitleForm, DepartmentsForm, SkillsForm, EmployeesForm, ScoreForm
from common import *




# Skills
# ------------

@app.route("/skills", methods=["GET", "POST"])
def skill():

    results = db.session.query(
        Skills.ID,
        Skills.Department,
        Skills.Skill,
        Skills.SkillName,
        Skills.SkillFactor,
        Skills.CreateDate,
        Skills.UpdateDate
        )

    if request.method == 'POST' and 'tag' in request.form:
       tag = request.form["tag"]
       search = "%{}%".format(tag)
       results = Skills.query.filter(Skills.SkillName.like(search))
       return render_template("skills/skills-list.html", title = "Skill", results=results, tag=tag)

    return render_template("skills/skills-list.html", title = "Skills", results=results)



@app.route("/skills/add/", methods=["GET", "POST"])
def add_skills():

    if request.method == 'POST':

        record = Skills(
            Skill=request.form['Skill'], 
            Department = request.form['Department'],
            SkillFactor = request.form['SkillFactor'],
            CreateDate=datetime.now(), 
            UpdateDate=datetime.now()
            )
        db.session.add(record)
        db.session.commit()

        return redirect("/skills")
    
    else:
        form = SkillsForm()
        form.Department.choices = get_departments()

    return render_template("skills/skill-edit-form.html", title = "Add Skill", form=form, action='add')


@app.route("/skills/edit/<id>", methods=["GET", "POST"])
def edit_skill(id):

    if request.method == 'POST':

        results = Skills.query.filter_by(ID=id).first()

        results.Skill = request.form['Skill']
        results.SkillFactor = request.form['SkillFactor']
        results.Department = request.form['Department']

        results.UpdateDate=datetime.now()
        db.session.commit()

        return redirect("/skills")

    else: 

        results = Skills.query.filter_by(ID=id).first()
        form = SkillsForm()
        form.Department.choices = get_departments()
        form.Skill.default = results.Skill
        form.Department.default = results.Department
        form.SkillFactor.default = results.SkillFactor
        form.process()

        return render_template("skills/skill-edit-form.html", title = "Edit Skill", form=form, id=id, action='edit')

