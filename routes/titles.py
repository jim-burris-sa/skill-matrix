from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from models import db, Titles, Departments, Skills, Employees, Scores
from __main__ import app
from datetime import datetime
from views import TitleForm, DepartmentsForm, SkillsForm, EmployeesForm, ScoreForm
from common import *


# Titles
# ------------

@app.route("/titles")
def titles():

    titles = Titles.query.all()

    return render_template("titles/titles-list.html", title = "Titles", titles=titles)


@app.route("/titles/add/", methods=["GET", "POST"])
def add_title():
    

    if request.method == 'POST':

        record = Titles(
            Title=str(request.form['Title']), 
            CreateDate=datetime.now()
            )
        db.session.add(record)
        db.session.commit()

        return redirect("/titles")
    
    else:
        form = TitleForm()

    return render_template("titles/title-edit-form.html", title = "Add Title",  form=form, action='add')


@app.route("/titles/edit/<id>", methods=["GET", "POST"])
def edit_title(id):

    if request.method == 'POST':

        results = Titles.query.filter_by(ID=id).first()

        results.Title = request.form['Title']
        results.UpdateDate=datetime.now()
        db.session.commit()

        return redirect("/titles")

    else: 

        results = Titles.query.filter_by(ID=id).first()
        
        form = TitleForm()
        form.Title.default = results.Title
        form.process()

        return render_template("titles/title-edit-form.html", title = "Edit Title", titles=results, id=id, form=form, action='edit')
