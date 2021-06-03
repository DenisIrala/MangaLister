from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/dbp10'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Usuarios(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password =  db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Todo: {self.username}>'

class Recordatorios(db.Model):
    __tablename__='recordatorios'
    username = db.Column(db.String(80), ForeignKey("clientes.username"), nullable=False)
    fecha= db.Column(db.String(80), nullable=False)
    tipo_de_actividad=db.Column(db.String(80), nullable=False)
    prioridad=db.Column(db.Integer, nullable=False)


db.create_all()

fetch('/my/request'.{
    method:: 'POST',
body:
})


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    #description = request.form.get('description', '')
    username=request.form.get('username','')
    password= request.form.get('username', '')
    NuevoUsuario = Usuarios(username=username,password=password)
    db.session.add(NuevoUsuario)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/create', methods=['GET'])
def create_todo_get():
    print("inserting using get method")
    description = request.args.get('description', '')
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/createjson', methods=['POST'])
def create_todo_json():
    print("inserting json object")
    data_string = request.data
    data_dictionary = json.loads(data_string)
    description = data_dictionary["description"]
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    todo = Todo.query.get(todo_id)
    return 'The todo is: ' + todo.description

@app.route('/recordatorio')
def index():
    return render_template('index.html', data=Recordatorios.query.all())
    '''return render_template('index.html', data=[
        {'description': 'Todo1'},
        {'description': 'Todo2'},
        {'description': 'Todo3'},
        {'description': 'Todo4'}
    ])'''

if __name__ == '__main__':
    app.run(port=5002, debug=True)
else:
    print('using global variables from FLASK')
