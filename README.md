# CS50 Web 2020 Final Project

For my final project I created a website called MySousChef that lets you search for recipes, add your own recipes, add items to a virtual pantry and keep track of use by dates, best before dates, when a jar was opened and use within data. The website also lets you search for recipes by filtering for ingredients only in your virtual pantry. You can also create a vitual shopping list.

This website is deployed using heroku:
[heroku link](https://mysouschef.herokuapp.com/)

## This project uses

- Python Django framework
- Postgres SQL database
- Javascript
- HTML
- SCSS and CSS, using a colorlib template
- Spoonacular API
- deployed on Heroku
- CI/Cl using travis
- Database caching

This project is broken down into 2 django apps working together: accounts and recipes.

## Main project folder

Here I have the gitignore file (used to exclude files from git version control), travis.yml (used to build my project in travis when changes are commited), manage.py (Django file to run django commands), requirments.txt (file containing names of all dependencies), procfile (Used by heroku to deploy application) and this README file.

## Static directory

In this folder you will find all javascript files, scss files and css file.

## mysouschef directory

In this folder you will find init.py, settings.py (this includes all settings to do with caching, database, email and static files), urls.py, asgi.py and wsgi.py (files to do with deployment).

## accounts directory

This folder contains all the files for the accounts app. This includes: templates, migrations, admin.py, forms.py, models.py, signals.py, tests.py, tokens.py, urls.py and views.py.

This app lets the user register for an account, activate account by clciking on a link sent by email, login, logout, complete a contact form that emails the form content to admin, change password, change email or change username.

## recipes directory

This folder contains all the files for the recipes app. This includes: templates, migrations, custom templatetags, admin.py, forms.py, models.py, signals.py, tests.py, urls.py, utils.py and views.py.

This app lets you put items in a virtual pantry, create a shopping list, search recipes using the spoonacular api and save them, create own recipes and save them  and finally render a personalised dashboard.
