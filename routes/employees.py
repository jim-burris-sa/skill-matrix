from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from models import db, Titles, Departments, Skills, Employees, Scores
from __main__ import app
from datetime import datetime
from views import TitleForm, DepartmentsForm, SkillsForm, EmployeesForm, ScoreForm
from common import *



@app.route("/employees", methods=["GET", "POST"])
def employees():

    results = db.session.query(
        Employees.ID,
        Employees.FullName,
        Employees.Title,
        Employees.Department,
        Employees.CreateDate,
        Employees.UpdateDate
        )
    
    if request.method == 'POST' and 'tag' in request.form:
       tag = request.form["tag"]
       search = "%{}%".format(tag)
       results = Employees.query.filter(Employees.FullName.like(search))
       return render_template("employees/employees-list.html", title = "Employees", results=results, tag=tag)

    return render_template("employees/employees-list.html", title = "Employees", results=results)

@app.route("/employees/add/", methods=["GET", "POST"])
def add_employees():

    if request.method == 'POST':

        record = Employees(
            FirstName = request.form['FirstName'],
            LastName = request.form['LastName'],
            Title = request.form['Title'],
            Department = request.form['Department'],
            CreateDate=datetime.now(), 
            UpdateDate=datetime.now()
            )
        db.session.add(record)
        db.session.commit()

        return redirect("/employees")
    
    else:
        form = EmployeesForm()
        form.Department.choices = get_departments()
        form.Title.choices = get_titles()

    return render_template("employees/employee-edit-form.html", title = "Add Employees", form=form, action='add')


@app.route("/employees/edit/<id>", methods=["GET", "POST"])
def edit_employees(id):

    if request.method == 'POST':

        db.session.query(Employees).\
            filter(Employees.ID == id).\
            update(dict(
                FirstName = request.form['FirstName'],
                LastName = request.form['LastName'],
                Title = request.form['Title'],
                Department = request.form['Department'],
                UpdateDate=datetime.now()
                ))
        db.session.commit()

        return redirect("/employees")
    
    else:

        results = Employees.query.filter_by(ID=id).first()
        form = EmployeesForm()
        form.FirstName.default = results.FirstName
        form.LastName.default = results.LastName
        form.Title.choices = get_titles()
        form.Title.default = results.Title
        form.Department.choices = get_departments()
        form.Department.default = results.Department
        form.process()

    return render_template("employees/employee-edit-form.html", title = "Edit Employees", form=form, id=id, action='edit')
