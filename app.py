#!/usr/bin/env python3
from datetime import timezone
from operator import or_, sub
from flask import Flask, render_template, request, flash, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey, or_, update
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from flask_login import UserMixin, login_manager, login_user, login_required, logout_user, current_user, LoginManager
from sqlalchemy.sql.expression import select, true
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.schema import MetaData
from werkzeug.security import generate_password_hash, check_password_hash #hash = no inverse 
from flask_migrate import Migrate, current

import sys

#APP
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key' #averiguar bien sus usos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@mangalist.cohth3owbwy4.us-east-2.rds.amazonaws.com:5432/mangalist0' #this may change depending on the name of the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#DATABASE

lista_manga = db.Table('lista_manga', 
                        db.Column('listaid', db.Integer, db.ForeignKey('Lista.id'), primary_key = True),
                        db.Column('mangaid', db.Integer, db.ForeignKey('Manga.id'), primary_key = True)
)
manga_genero = db.Table('manga_genero', 
                        db.Column('mangaid', db.Integer, db.ForeignKey('Manga.id'), primary_key = True),
                        db.Column('generoid', db.Integer, db.ForeignKey('Genero.id'), primary_key = True)
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
    generos = db.relationship('Genero', secondary = manga_genero, backref= "generos", lazy = 'select' )
   
    
class Genero(db.Model):
    __tablename__ = 'Genero'
    id = db.Column(db.Integer, primary_key = True)
    genero = db.Column(db.String(80), nullable = False)

class Recomendados(db.Model):
    __tablename__= 'recomendados'
    titulo = db.Column(db.String(80), primary_key=True)
    genero = db.Column(db.String(80), nullable=False)
    editorial = db.Column(db.String(80), nullable=False)
    autor = db.Column(db.String(80), nullable=False)
    fecha_publicacion = db.Column(db.Integer, nullable=False)
#
login_manager = LoginManager()
login_manager.login_view = 'index_1'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) #como cargamos un usuario, por default busca el id.  

#VIEWS

@app.route('/')
def index_1():
    return render_template("index.html", user = current_user)

@app.route('/user', methods=['POST', 'GET'])
@login_required
def user_main():
    if request.method == 'POST':
        lista_nombre = request.form.get('addlista')
        lista = Lista.query.filter_by(nombre_lista = lista_nombre, usuario_id = current_user.id).first()
        if lista:
            flash('El nombre de la lista ya existe', category='fail') 
        else: 
            new_lista = Lista(nombre_lista = lista_nombre, usuario_id = current_user.id)
            db.session.add(new_lista)
            db.session.commit()
            flash('Lista añadida', category='accepted')
    return render_template("user_main.html", user=current_user)

@app.route('/biblioteca', methods=['POST', 'GET'])
@login_required
def biblioteca():
    manga = Manga.query.filter_by().all()

    return render_template("biblioteca.html", manga = manga)

@app.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    if request.method == 'POST':
        nombre_manga = request.form.get('nombre_manga')
        descripcion = request.form.get('descripcion')
        autor = request.form.get('autor')
        #estado = request.form.get('estado')
        nchap = request.form.get('nchap')
        link = request.form.get('link')
        #generos = request.form.get('genero')
        
        manga = Manga.query.filter_by(nombre_manga = nombre_manga).first()
        if manga:
            flash('El manga ya está registrado', category='fail')
        else:
            new_manga = Manga(nombre_manga = nombre_manga, 
                                descripcion = descripcion, 
                                autor = autor, 
                                nchap = nchap, 
                                link = link) 
            db.session.add(new_manga)
            db.session.commit()
            flash('Manga añadido a la base de datos exitosamente', category='accepted')
            return redirect(url_for('biblioteca'))        
    return render_template("addmanga.html")
#REVISAR_no funciona
@app.route('/search', methods=['POST', 'GET']) 
@login_required
def search():
    if request.method == 'POST':
        busqueda = request.form
        buscar = "%{}%".format(busqueda['search_box'])
        resultados = Manga.query.filter(or_(Manga.nombre_manga.like(buscar), 
                                        Manga.descripcion.like(buscar), 
                                        Manga.autor.like(buscar) )).all()
        return render_template("biblioteca.html", Manga = resultados)            
    else:
        flash('El manga no se encuentra en la base de datos. Sin embargo, es capaz de añadirlo', category='fail')
        return redirect(url_for('biblioteca')) 

#mostrar manga o lista por id 
@app.route('/lista/<int:lista_id>/show')
@login_required
def show_lista(lista_id):
    listas = Lista.query.filter_by(id = lista_id).first() 
    return render_template("lista.html", user=current_user, form = listas)

@app.route('/manga/<int:manga_id>')
@login_required
def get_manga(manga_id):
    mangas = Manga.query.filter_by(id = manga_id).first()
    return render_template("manga.html", user=current_user, form = mangas)

@app.route('/manga/<int:manga_id>/update', methods=['POST', 'GET'])
@login_required
def estado_upgrade(manga_id):   
    if request.method == 'POST':
        mangas = Manga.query.filter_by(id=manga_id).first() 
        newestado = request.form.get('newestado')
        if len(newestado)>10:
            flash('Se recomienda ingresar "Leido, "Abandonado", "Favorito", "Pendiente", "Siguiendo"', category='fail')
        else:
            mangas.estado = newestado
            db.session.commit()
    return render_template("manga.html", user=current_user, form = mangas)

#editar una lista
@app.route('/lista/<int:lista_id>')
@login_required
def get_lista(lista_id):
    listas = Lista.query.filter_by(id = lista_id).first() 
    return render_template("update_list.html", user=current_user, form = listas)

@app.route('/lista/<int:lista_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_lista(lista_id):
    if request.method == 'POST':
        listas = Lista.query.filter_by(id = lista_id).first() 
        db.session.delete(listas)
        db.session.commit()
    return render_template("user_main.html", user=current_user)


@app.route('/lista/<int:lista_id>/update', methods=['POST', 'GET'])
@login_required
def update_lista(lista_id):   
    if request.method == 'POST':
        listas = Lista.query.filter_by(id = lista_id).first() 
        listas.nombre_lista = request.form.get('newname')
        db.session.commit()
    return render_template("user_main.html", user=current_user, form = listas)



#INICIO

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("index.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password') 

        user = User.query.filter_by(email = email).first()
        if user:
            flash('El email ya existe', category='fail')

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
            return redirect(url_for('user_main'))

    return render_template("register.html", user = current_user)

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
                return redirect(url_for('user_main'))
            else:
                flash('Contraseña incorrecta, intente de nuevo', category='fail')
        else:
            flash('El email no existe', category='fail')


    return render_template("login.html", user = current_user)

@app.route('/recomendados',methods=['POST'])
def recomendar():
    buscar_manga = request.form.get('manga','')
    return render_template('Recomendados.html', recomendar_mangas = Recomendados.query.filter_by(genero=buscar_manga))

"""  buscar_manga = request.form.get('manga','') 
    mangas = [r.genero for r in db.session.query(buscar_manga).filter_by(name=buscar_manga)]
    recomendar_mangas = []
    for manga in mangas:
        elementos = [r.genero for r in db.session.query(Recomendados).filter_by(titulo=manga).distinct()]
        recomendar_mangas.append(elementos)
    return render_template('index.html', recomendar_mangas=recomendar_mangas) """


if __name__ == '__main__':
    app.run(host= "localhost", port=5002, debug=True)
<<<<<<< HEAD
    
=======
>>>>>>> ab07b0ff2814892747925f547745637d0ab91cad
