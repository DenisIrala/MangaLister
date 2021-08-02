from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask.json import load
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
import json
import sys
import psycopg2
from psycopg2 import Error


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dbp'
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


if __name__ == '__main__':
    app.run(host= "localhost", port=5002, debug=True)