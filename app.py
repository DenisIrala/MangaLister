#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
import json
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/dbp10' #this may change depending on the name of the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Usuarios(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer)
    username = db.Column(db.String(80), nullable=False, primary_key=True)
    password =  db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Todo: {self.username}>'

class Lista(db.Model):
    __tablename__='lista'
    username = db.Column(db.String(80), ForeignKey("clientes.username"), primary_key=True)
    fecha= db.Column(db.String(80), nullable=False)
    nombre=db.Column(db.String(80), nullable=False)
    visto=db.Column(db.String(80), nullable=False)

class Mangas(db.Model):
    __tablename__='Mangas'
    nombre=db.Column(db.String(80), nullable=False, primary_key=True)
    autor = db.Column(db.String(80), nullable=False)
    genero =  db.Column(db.String(80), nullable=False)
    npag = db.Column(db.String(80), nullable=False)

db.create_all()


@app.route('/')
def index_1():#line 83 overwriting function index
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    #description = request.form.get('description', '')
    try:
        error=False
        username=request.form.get('username','')
        password= request.form.get('username', '')
        NuevoUsuario = Usuarios(username=username,password=password)
        db.session.add(NuevoUsuario)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        return render_template('register.html', error=error)
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/createjson', methods=['POST'])
def create_manga_json():
    data_string = request.data
    data_dictionary = json.loads(data_string)
    description = data_dictionary["description"]
    mangas = Mangas(nombre=description)
    db.session.add(mangas)
    db.session.commit()
    return jsonify(description=mangas.description)

@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    todo =get_todo_by_id.query.get(todo_id)
    return 'The todo is: ' + todo.description

@app.route('/recordatorio') #line 42 overwriting function index
def index():
    return render_template('list.html', data=Lista.query.all())

if __name__ == '__main__':
    app.run(host= "localhost", port=5002, debug=True)