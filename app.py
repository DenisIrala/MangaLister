#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
import json
import sys
import psycopg2
from psycopg2 import Error


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/dbp10' #this may change depending on the name of the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Recomendados(db.Model):
    __tablename__= 'recomendados'
    titulo = db.Column(db.String(80), primary_key=True)
    genero = db.Column(db.String(80), nullable=False)
    editorial = db.Column(db.String(80), nullable=False)
    autor = db.Column(db.String(80), nullable=False)
    fecha_publicacion = db.Column(db.Integer, nullable=False)

class prueba_recomendados(db.Model):
    __tablename__= 'prueba_recomendados'
    nombre = db.Column(db.String(80), nullable=False, primary_key=True)
    genero =  db.Column(db.String(80), nullable=False)

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

@app.route('/recomendados',methods=['POST'])
def recomendar():
    buscar_manga = request.form.get('manga','')
    return render_template('recomendados.html', recomendar_mangas = Recomendados.query.filter_by(genero=buscar_manga))

"""  buscar_manga = request.form.get('manga','') 
    mangas = [r.genero for r in db.session.query(buscar_manga).filter_by(name=buscar_manga)]
    recomendar_mangas = []
    for manga in mangas:
        elementos = [r.genero for r in db.session.query(Recomendados).filter_by(titulo=manga).distinct()]
        recomendar_mangas.append(elementos)
    return render_template('index.html', recomendar_mangas=recomendar_mangas) """



@app.route('/')
def index():
    return render_template('recomendar_search.html')

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


if __name__ == '__main__':
    app.run(host= "localhost", port=5002, debug=True)