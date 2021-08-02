from datetime import timezone
from operator import or_, sub
from os import error
from typing import List
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey, or_, update, insert
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from flask_login import UserMixin, login_manager, login_user, login_required, logout_user, current_user, LoginManager
from sqlalchemy.sql.expression import false, select, true
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.schema import MetaData
from werkzeug.security import generate_password_hash, check_password_hash #hash = no inverse 
from flask_migrate import Migrate, current
import sys
import json
import psycopg2 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key' #averiguar bien sus usos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/dbpweb' #this may change depending on the name of the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


connection = psycopg2.connect(
    host="localhost",
    database="dbpweb",
    user="postgres",
    password="123")
cursor = connection.cursor()



#DATABASE

lista_manga = db.Table('lista_manga', 
                        db.Column('listaid', db.Integer, db.ForeignKey('Lista.id'), primary_key = True),
                        db.Column('mangaid', db.Integer, db.ForeignKey('Manga.id'), primary_key = True)
)
class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), nullable=False)
    password =  db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True) 
    listas = db.relationship('Lista', backref = "user", lazy = 'select') #one to many     
   
class Lista(db.Model):
    __tablename__='Lista'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime(timezone=True), default=func.now())
    nombre_lista = db.Column(db.String(80), nullable = False)
    usuario_id = db.Column(db.Integer, ForeignKey('User.id'))
    mangas = db.relationship('Manga', secondary = lista_manga, backref= "listas", lazy = 'select' )     

class Manga(db.Model):
    __tablename__='Manga'
    id = db.Column(db.Integer, primary_key=True)
    nombre_manga = db.Column(db.String(200), nullable = False, unique=True)
    descripcion = db.Column(db.String(255))
    link = db.Column(db.String(255))
    autor = db.Column(db.String(80), nullable=False)
    estado = db.Column(db.String(80)) 
    nchap = db.Column(db.Integer, nullable=False)
    demografia = db.Column(db.String(80), nullable=False)


#
login_manager = LoginManager()
login_manager.login_view = 'inicio'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) #como cargamos un usuario, por default busca el id.  

#General
@app.route('/inicio') #biblioteca
def inicio():
    manga = Manga.query.filter_by().all()
    return render_template("biblioteca.html", user = current_user, manga = manga)

@app.route('/')
def index_1():
    return render_template("base1.html", user = current_user)

@app.route('/listas')
@login_required
def listas():
    listas = Lista.query.filter_by(usuario_id = current_user.id).all()
    return render_template("lista.html", user = current_user, listas  = listas)

#Recomendados 
@app.route('/recomendados',methods=['POST'])
@login_required
def recomendar():
    buscar_manga = request.form.get('manga','')
    return render_template('recomendados.html', recomendar_mangas = Manga.query.filter_by(demografia=buscar_manga))

#actualizar estado 
@app.route('/update_estado', methods = ['POST'])
def update_estado():
    response = {}
    try: 
        data = {'estado': request.get_json()['estado']  , 'manga_id': request.get_json()['manga_id'] }
        cursor.execute('UPDATE "Manga" SET estado = %(estado)s WHERE id = %(manga_id)s', data )      
        connection.commit()  
    except:
        connection.rollback()
        print(sys.exc_info())
    return jsonify(response)

#añadir mangas a listas
@app.route('/manga_lista', methods = ['POST'])
def manga_lista():
    response = {}
    try: 
        data = {'lista_id': request.get_json()['lista_id']  , 'manga_id': request.get_json()['manga_id'] }
        cursor.execute('INSERT INTO lista_manga(listaid, mangaid) VALUES (%(lista_id)s, %(manga_id)s)', data )      
        connection.commit()  
    except:
        connection.rollback()
        print(sys.exc_info())
    return jsonify(response)

#Obtener listas y filtrar listas_mangas
@app.route('/lista/<int:lista_id>')
@login_required
def get_lista(lista_id):
    d = {'lista_id':lista_id}
    data = []
    lista = Lista.query.filter_by(id = lista_id).first()
    cursor.execute('SELECT nombre_manga, id FROM "Manga" WHERE id IN (SELECT mangaid FROM lista_manga WHERE listaid = %(lista_id)s)', d)
    for row in cursor:
        data.append(row)
    connection.commit()
    return render_template("lista_detalles.html", user=current_user, lista = lista, mangas = data )

#eliminar mangas de listas
@app.route('/<lista_id>/<todo_id>/delete-manga')
@login_required
def delete_todo_by_id(todo_id, lista_id):
    try:
        data = {'mangaid': todo_id}
        cursor.execute('DELETE FROM lista_manga WHERE mangaid = %(mangaid)s', data)
        connection.commit()
    except:
        connection.rollback()
    return redirect(url_for('get_lista', lista_id = lista_id))


#Eliminar lista 
@app.route('/eliminar_lista/<lista_id>')
@login_required
def delete_lista(lista_id):
    try:
        data = {'listaid': lista_id}
        cursor.execute('DELETE FROM lista_manga WHERE listaid = %(listaid)s', data)
        cursor.execute('DELETE FROM "Lista" WHERE id = %(listaid)s', data)
        connection.commit()
    except:
        connection.rollback()
    return redirect(url_for('listas'))

#Modificar lista 
@app.route('/update_lista', methods = ['POST'])
@login_required
def update_lista():
    response = {}
    try:
        lista_id = request.get_json()['lista_id']
        usuario = request.get_json()['usuario']    
        listas = Lista.query.filter_by(id = lista_id, usuario_id = usuario ).first() 
        listas.nombre_lista = request.get_json()['new_nombre']        
        db.session.commit()  
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return jsonify(response)


#¿Control de errores?
@app.route('/crear_lista', methods = ['POST'])
def crear_lista():
    response = {}
    try:
        nombre_lista = request.get_json()['nombre_lista'] 
        usuario = request.get_json()['usuario']    
        form = Lista(nombre_lista = nombre_lista, usuario_id = usuario)            
        db.session.add(form)
        db.session.commit()  
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return jsonify(response)


#Mostrar detalles de manga
@app.route('/manga/<int:manga_id>')
@login_required
def get_manga(manga_id):
    mangas = Manga.query.filter_by(id = manga_id).first()
    listas = Lista.query.filter_by(usuario_id = current_user.id).all()
    return render_template("manga.html", user=current_user, form = mangas, listas = listas)

#Añadir manga a la base de datos
@app.route('/agregar_manga', methods = ['POST', 'GET'])
@login_required
def agregar_manga():
    if request.method == 'POST':
        nombre_manga = request.form.get('nombre_manga')
        descripcion = request.form.get('descripcion')
        autor = request.form.get('autor')
        nchap = request.form.get('nchap')
        link = request.form.get('link')
        demografia = request.form.get('demografia')  
        manga = Manga.query.filter_by(nombre_manga = nombre_manga).first()
        if manga:
            flash('El manga ya está registrado', category='fail')
        else:
            new_manga = Manga(nombre_manga = nombre_manga, 
                                descripcion = descripcion, 
                                autor = autor, 
                                nchap = nchap, 
                                demografia = demografia,
                                link = link) 
            db.session.add(new_manga)
            db.session.commit()
            flash('Manga añadido a la base de datos exitosamente', category='accepted')
            return redirect(url_for('inicio'))        
    return render_template("addmanga.html")

#Registro
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password') 
        user = User.query.filter_by(email = email).first()
        if user:
            flash('El usuario ya existe', category='fail')

        if len(email) < 10:
            flash('Por favor, ingrese un correo válido', category='fail')
        elif len(username) < 5:
            flash('El usuario debe ser mayor a 5 caracteres', category='fail')
        elif len(password) < 8 or len(password)>20 :
            flash('La contraseña debe ser mayor a 8 caracteres y menor a 20', category='fail')
        else:
            new_user = User(email=email, username=username,password=generate_password_hash(password, method="sha256")) #sha256 algoritmo de seguridad 
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Cuenta creada', category='accepted')
            return redirect(url_for('inicio')) 
    return render_template("register.html", user = current_user)
#Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Inicio de sesión aprobado', category='accepted')#evaluar si dejarlo o no 
                login_user(user, remember=True)
                return redirect(url_for('inicio'))
            else:
                flash('Contraseña incorrecta, intente de nuevo', category='fail')
        else:
            flash('El email no existe', category='fail')
    return render_template("login.html", user = current_user)
#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("base1.html")




if __name__ == '__main__':
    app.run(host= "localhost", port=5002, debug=True)