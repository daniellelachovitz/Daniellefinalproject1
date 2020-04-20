"""
Project by: Danielle Lachovitz
Date: TASHAP
Grade: 10th grade, Tichonet

Routes and views for the flask application.
"""
from GadFinalProjectDemo import app

import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
from   matplotlib.figure import Figure
import pandas as pd

import io
import base64
import json 
import requests

from flask     import Flask, render_template, flash, redirect, request
from flask_wtf import FlaskForm
from wtforms   import Form, validators, ValidationError
from wtforms   import BooleanField, StringField, PasswordField, TextField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired


from wtforms.fields.html5 import DateField , DateTimeField



from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)

from datetime import datetime
from os       import path

# Integrate internal project models
# ---------------------------------
from GadFinalProjectDemo.Models.LocalDatabaseRoutines import create_LocalDatabaseServiceRoutines
from GadFinalProjectDemo.Models.FormStructure import DataQueryFormStructure 
from GadFinalProjectDemo.Models.FormStructure import LoginFormStructure 
from GadFinalProjectDemo.Models.FormStructure import UserRegistrationFormStructure 
from GadFinalProjectDemo.Models.FormStructure import ExpandForm
from GadFinalProjectDemo.Models.FormStructure import CollapseForm
from GadFinalProjectDemo.Models.FormStructure import SinglePresidentForm
from GadFinalProjectDemo.Models.FormStructure import AllOfTheAboveForm
from GadFinalProjectDemo.Models.FormStructure import Covid19DayRatio

from GadFinalProjectDemo.Models.DataQuery     import plot_to_img
from GadFinalProjectDemo.Models.DataQuery     import Get_NormelizedUFOTestmonials
from GadFinalProjectDemo.Models.DataQuery     import create_covid_data
from GadFinalProjectDemo.Models.DataQuery     import get_states_choices
from GadFinalProjectDemo.Models.DataQuery     import Get_NormelizedWeatherDataset
from GadFinalProjectDemo.Models.DataQuery     import MergeUFO_and_Weather_datasets
from GadFinalProjectDemo.Models.DataQuery     import MakeDF_ReadyFor_Analysis


#### Subclasses spawn
db_Functions = create_LocalDatabaseServiceRoutines() 


# Landing page - Home page
@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

# Contact page
@app.route('/contact')
def contact():
    return render_template(
        'contact.html',
        title='Danielle Lachovitz',
        year=datetime.now().year,
        message='Stident, Tichonet'
    )

# About Page
@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='About The Project',
        message='The project is a year-end final project within the framework of the "data science" course',
        year=datetime.now().year
     
    )



# -------------------------------------------------------
# Register new user page
# -------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def Register():
    form = UserRegistrationFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (not db_Functions.IsUserExist(form.username.data)):
            db_Functions.AddNewUser(form)
            flash('Welcom - '+ form.FirstName.data + " " + form.LastName.data )
        else:
            flash('Error: User with this Username already exist ! - '+ form.username.data)

    return render_template(
        'register.html', 
        form=form, 
        title='Register New User',
        year=datetime.now().year,
        )

# -------------------------------------------------------
# Login page
# This page is the filter before the data analysis
# -------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (db_Functions.IsLoginGood(form.username.data, form.password.data)):
            flash('Login approved!')
            #return redirect('<were to go if login is good!')
        else:
            flash('Error in - Username and/or password')
   
    return render_template(
        'login.html', 
        form=form, 
        title='Login to data analysis',
        year=datetime.now().year,
        )


# Data model description, used by the site
@app.route('/DataModel')
def DataModel():
    return render_template(
        'DataModel.html',
        title='This is my Data Model page about Covid19 Cases',
        year=datetime.now().year,
        message='On this page, we will describe the data page with the number of the Covid19 cases'
    )


@app.route('/DataSet1')
def DataSet1():

    df = pd.read_csv(path.join(path.dirname(__file__), 'static\\Data\\Covid19.csv'))
    raw_data_table = df.sample(30).to_html(classes = 'table table-hover')

    return render_template(
        'DataSet1.html',
        title='Covid19 cases, by country and date',
        raw_data_table = raw_data_table,
        year=datetime.now().year,
        message='This page displays data that can be analyzed and help us understand the Covid19 empidemic'
    )







@app.route('/DataQuery', methods=['GET', 'POST'])
def DataQuery():

    """
    There is a variable name form in this function, like `form.start_date`
    form let you get all the variables passed by the user in the form (in the html)
    if use put a start date in the form it will be in `form.start_date`
    """

    df_covid = create_covid_data()

    UFO_table = ""
    fig_image = ""

    form = DataQueryFormStructure(request.form)
    
    #set default values of datetime, to indicate ALL the rows
  
    #Set the list of states from the data set of all US states
    form.states.choices = get_states_choices() 
 
     
    if (request.method == 'POST'):

        ##df_ufo = Get_NormelizedUFOTestmonials()

        # Get the user's parameters for the query
        state = form.states.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        df_covid = df_covid.set_index('countriesAndTerritories').loc[ state ]
        # Filter only the requested Dates
        df_covid_dates = df_covid.loc[lambda df: (df['dateRep'] >= start_date) & (df['dateRep'] <= end_date)]
        df_covid_dates = df_covid_dates.sort_values('datetime')
        # create plot object ready for graphs
        fig = plt.figure()
        ax = fig.add_subplot()
        data = pd.DataFrame({'Date': df_covid_dates['datetime'], 'Cases': df_covid_dates['cases']})
        data.plot(x='Date', y='Cases' ,ax = ax, kind='bar', grid=True)
        fig_image = plot_to_img(fig)

    return render_template('DataQuery.html', 
            form = form, 
            fig_image = fig_image,
            title='User Data Query',
            year=datetime.now().year,
            message='Please enter the parameters you choose, to analyze the database'
        )
