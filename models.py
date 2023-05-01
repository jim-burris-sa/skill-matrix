from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  UniqueConstraint, ForeignKey

db = SQLAlchemy(app)


class Titles(db.Model):
    
    # __tablename__ = 'dim_titles'

    Title = db.Column(db.String(100), unique=True, primary_key=True)
    CreateDate = db.Column(db.DateTime)



class Departments(db.Model):

    # __tablename__ = "dim_departments"

    Department = db.Column(db.String(100), unique=True, primary_key=True)
    CreateDate = db.Column(db.DateTime)



class Skills(db.Model):

    # __tablename__ = "dim_skills"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Department = db.Column(db.String(100))
    Skill = db.Column(db.String(100))
    SkillName = db.column_property(Department + " - " + Skill)
    SkillFactor = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime)
    UpdateDate = db.Column(db.DateTime)
    UniqueConstraint('Department', 'Skill')    


class Employees(db.Model):

    # __tablename__ = "dim_employees"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(100))
    LastName = db.Column(db.String(100))
    FullName = db.column_property(FirstName + " " + LastName)
    Department = db.Column(db.String(100))
    Title = db.Column(db.String(100))
    CreateDate = db.Column(db.DateTime)
    UpdateDate = db.Column(db.DateTime)    


class Scores(db.Model):

    # __tablename__ = "fact_scores"   

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Employee_ID = db.Column(db.Integer)
    Skill_ID = db.Column(db.Integer)
    Score = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime)
    UpdateDate = db.Column(db.DateTime)   
    UniqueConstraint('Employee_ID', 'Skill_ID')    

