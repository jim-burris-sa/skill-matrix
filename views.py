from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms import Form, StringField, validators, SelectField, HiddenField



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

    