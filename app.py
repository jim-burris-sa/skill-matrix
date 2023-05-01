from flask import Flask, render_template, session, request, redirect
from datetime import datetime
from wtforms import StringField
from wtforms import Form, StringField, validators, SelectField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  UniqueConstraint
import pandas as pd
import numbers


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


# -------------------------------------------------------
# Routes
# -------------------------------------------------------

@app.route("/")
def index():
    return redirect('/employees')

# Departments

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


# Employees

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

# Reports

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


# Scores

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


# Skills

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


# Titles

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


# -------------------------------------------------------
# Views
# -------------------------------------------------------

class TitleForm(Form):
    Title = StringField("Title", validators=[validators.input_required()])
    CreateDate = StringField("Create Date")
    UpdateDate = StringField("Update Date")


class DepartmentsForm(Form):
    Department = StringField("Department", validators=[validators.input_required()])
    CreateDate = StringField("Create Date")
    UpdateDate = StringField("Update Date")


class SkillsForm(Form):
    Skill = StringField("Skill", validators=[validators.input_required()])
    Department = SelectField("Department", validators=[validators.input_required()], choices=[] )
    SkillFactor = StringField("Skill Factor", validators=[validators.input_required()])    


class EmployeesForm(Form):
    FirstName = StringField("First Name", validators=[validators.input_required()])
    LastName = StringField("Last Name", validators=[validators.input_required()])
    Title = SelectField("Title", validators=[validators.input_required()], choices=[] )
    Department = SelectField("Department", validators=[validators.input_required()], choices=[] )
      

class ScoreForm(Form):
    Employee = SelectField("Employee", validators=[validators.input_required()], choices=[] )
    Skill = SelectField("Skill", validators=[validators.input_required()], choices=[] )
    Score = StringField("Score", validators=[validators.input_required()])

class SkillMatrixForm(Form):
    Department = SelectField("Department", validators=[validators.input_required()], choices=[] )

    
# -------------------------------------------------------
# Models
# -------------------------------------------------------

class Titles(db.Model):
    
    Title = db.Column(db.String(100), unique=True, primary_key=True)
    CreateDate = db.Column(db.DateTime)


class Departments(db.Model):

    Department = db.Column(db.String(100), unique=True, primary_key=True)
    CreateDate = db.Column(db.DateTime)


class Skills(db.Model):

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Department = db.Column(db.String(100))
    Skill = db.Column(db.String(100))
    SkillName = db.column_property(Department + " - " + Skill)
    SkillFactor = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime)
    UpdateDate = db.Column(db.DateTime)
    UniqueConstraint('Department', 'Skill')    


class Employees(db.Model):

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(100))
    LastName = db.Column(db.String(100))
    FullName = db.column_property(FirstName + " " + LastName)
    Department = db.Column(db.String(100))
    Title = db.Column(db.String(100))
    CreateDate = db.Column(db.DateTime)
    UpdateDate = db.Column(db.DateTime)    


class Scores(db.Model):

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Employee_ID = db.Column(db.Integer)
    Skill_ID = db.Column(db.Integer)
    Score = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime)
    UpdateDate = db.Column(db.DateTime)   
    UniqueConstraint('Employee_ID', 'Skill_ID')    



# -------------------------------------------------------
# Common
# -------------------------------------------------------

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


if __name__ == "__main__":
    # app.app_context().push()
    # db.create_all()
    app.run()