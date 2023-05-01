from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from models import db, Titles, Departments, Skills, Employees, Scores
from __main__ import app
from datetime import datetime
from views import TitleForm, DepartmentsForm, SkillsForm, EmployeesForm, ScoreForm, SkillMatrixForm
import pandas as pd
import numbers
from common import *

@app.route("/reports/skillmatrix", methods=["GET", "POST"] )
def skill_matrix():

    form = SkillMatrixForm()
    form.Department.choices = get_emp_departments()

    df = pd.read_sql_query(
        sql = db.session.query(
            Employees.FullName.label('Employee'),
            Employees.Title,
            Employees.Department.label('Department'),
            Skills.SkillName.label('Skill'),
            Skills.SkillFactor,
            Scores.Score,
            Skills.SkillFactor * Scores.Score)\
                .join(Skills, Skills.ID == Scores.Skill_ID)\
                .join(Employees, Employees.ID == Scores.Employee_ID)\
                .statement, con = db.engine)
    

    if request.method == 'POST' and 'Department' in request.form:
        tag = request.form["Department"]
        df = df[df['Department'].str.contains(tag, regex=True, na=True)]
    else:
        tag = ""


    df['Skill_Score'] = df['anon_1']
    df.drop(columns=['anon_1', 'SkillFactor',  'Score'], inplace=True)

    df_pivot = pd.pivot_table(df, index=['Department', 'Employee', 'Title'], values='Skill_Score', aggfunc='sum', columns=['Skill'], margins=True, margins_name='Totals' ) 
    df_pivot = df_pivot.fillna('')
    df_pivot.reset_index(inplace=True)

    # Gen table
    dict_data = [df_pivot.to_dict(), df_pivot.to_dict('index')]

    header_style = "-ms-writing-mode: tb-rl; -webkit-writing-mode: vertical-rl; writing-mode: vertical-rl; transform: rotate(-180deg);"

    return_str = '<table class="table table-striped"><tr>'

    # Headers
    for key in dict_data[0].keys():
        if str(key) in ['Department', 'Employee', 'Title']:
            return_str = return_str + '<th style = "vertical-align: bottom;">' + str(key) + '</th>'
        else:
            return_str = return_str + f'<th style = "{header_style}">' + str(key) + '</th>'

    return_str = return_str + '</tr>'

    # Rows
    for key in dict_data[1].keys():

        return_str = return_str + '<tr>'
        for subkey in dict_data[1][key]:

            if isinstance(dict_data[1][key][subkey], numbers.Number):
                return_str = return_str + '<td align ="right">' + str(int(dict_data[1][key][subkey])) + '</td>'
            else:
                return_str = return_str + '<td align ="right">' + str(dict_data[1][key][subkey]) + '</td>'
                
    return_str = return_str + '</tr></table>'

    return render_template("/reports/skillmatrix.html",  tables=[return_str], titles=df.columns.values , tag=tag, form=form)
