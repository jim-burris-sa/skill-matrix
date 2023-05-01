from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from models import db, Titles, Departments, Skills, Employees, Scores
from __main__ import app
from datetime import datetime
from views import TitleForm, DepartmentsForm, SkillsForm, EmployeesForm, ScoreForm
from common import *


# Departments
# ----------------

@app.route("/departments", methods=["GET", "POST"])
def departments():

    departments = Departments.query.all()

    results = db.session.query(
        Departments.Department,
        Departments.CreateDate
        )

    if request.method == 'POST' and 'tag' in request.form:
       tag = request.form["tag"]
       search = "%{}%".format(tag)
       results = Departments.query.filter(Departments.Department.like(search))
       return render_template("departments/departments-list.html", title = "Departments", results=results, tag=tag)

    return render_template("departments/departments-list.html", title = "Departments", results=results)


@app.route("/departments/add/", methods=["GET", "POST"])
def add_department():

    if request.method == 'POST':

        record = Departments(
            Department=str(request.form['Department']), 
            CreateDate=datetime.now()
            )
        db.session.add(record)
        db.session.commit()

        return redirect("/departments")
    
    else:
        form = DepartmentsForm()

    return render_template("departments/department-edit-form.html", title = "Add Department", form=form, action='add')


# @app.route("/departments/edit/<id>", methods=["GET", "POST"])
# def edit_department(id):

#     if request.method == 'POST':

#         results = Departments.query.filter_by(ID=id).first()

#         results.Department = request.form['Department']
#         results.UpdateDate=datetime.now()
#         db.session.commit()

#         return redirect("/departments")

#     else: 

#         results = Departments.query.filter_by(ID=id).first()
#         form = DepartmentsForm()
#         form.Department.default = results.Department
#         form.process()

#         return render_template("departments/department-edit-form.html", title = "Edit Department", form=form, id=id, action='edit')
