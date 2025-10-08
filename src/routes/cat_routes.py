from flask import Blueprint, render_template, url_for, g, request, redirect
from ..database.connection import get_db_connection, close_db_connection
from ..repos.cat_repo import CatRepo
from ..models.cat_model import Cat
import mysql.connector

cats = Blueprint('cats', __name__, url_prefix = "/cats")
cat_repo = CatRepo()

@cats.before_request
def establish_db_connection():
    if 'db_connection' not in g:
        g.db_connection = get_db_connection()


@cats.route('/')
def home():
    return render_template('cats/home.html')

@cats.route('/cat-data', methods = ['POST', 'GET'])
def data_cat():
    connection = g.db_connection
    datas = cat_repo.get_all(connection)

    if request.method == 'POST':
        data_form = Cat.model_validate(request.form.to_dict())
        cat_repo.insert_cat(connection, data_form)
        return redirect(url_for('data_cat'))

    return render_template('cats/data_cat.html', datas = datas)

@cats.route('/delete')
def delete():
    return '<h1>Delete</h1>'
