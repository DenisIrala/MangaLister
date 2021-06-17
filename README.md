# Manga Lister
<p align="center">
  <img  src="portada.png">
</p>

## Integrantes:
  * Denis Irala
  * Marcela Espinoza
  * Tony Astuhuaman 
  * Johar Barzola


## Descripción del proyecto
Un manga es una historieta de origen japonés y es uno de los medios de entretenimiento más populares en aquella región. No obstante, debido al gran volumen de franquicias que existen, organizar un horario para poder leerlos todos es una tarea muy tediosa y trabajosa, es a partir de este problema que surge MangaList.
  Esta web page permite al usuario establecer una constancia sobre los mangas que desea leer, los cuales se guardan en una tabla que toma en cuanta la fecha, nombre del manga, nivel de prioridad asignada por el usuario, si el usuario la ha visto o no.

  Adicionalmente, la web ofrece la capacidad filtrar los mangas según los atributos de los mismos, tal como numero de paginas, genero, nombre del autor, etc. 

  La pagina incluira una función de inicio de sesión con usuario y contraseña para así mostrar la información correspondiente a cada usuario. Asimismo, se añadirá una sección de recomendaciones que mostrará mangas de acuerdo a los géneros con mayor presencia en la lista del usuario, los cuales se obtendrán de una lista prehecha de mangas.

## Objetivos principales 

* Implementar un sistema de registro e inicio de sesión.
* Implementar una base de datos relacional que permita visualizar una lista personalizada al usuario y que una interfaz que permita al usuario realizar CRUD con la misma.
* Implementar una respuesta amigable a los errores.
* Implementar un algoritmo que utilice las relaciones entre tablas para brindar una lista de recomendaciones al usuario.

## Misión
* Brindar un servicio que mejore la experiencia de los lectores de mangas que ha leido para así popularizar el rubro y promover la lectura de mangas

## Visión
* Se facilitará el acceso a mangas ya sea a través de una lista personalizada que permite mejorar su organización o una sección de recomendaciones que le permite conocer nuevas franquicias.

## Información acerca de las tecnologías utilizadas en Front-end, Back-end y Base de datos.
### Front end:

### Back end:

### Base de datos:

...
  * ### El nombre del script a ejecutar para iniciar la base de datos con datos. : script.py 

  * ### Información acerca de los API. Requests y respuestas de cada endpoint utilizado en el sistema.

## Hosts
El host usado para la aplicación python fue Amazon Web Services (AWS), mientras que el servicio usado para la base de datos remota fue Amazon RDS.

## Forma de Autenticación.


## Manejo de errores HTTP: 500, 400, 300, 200, 100, etc
En este proyecto los errores ocurren como resultado de un input inválido de parte del usuario, ya sea en el registro, inicio de sesión o en la exposición de las listas.
### Registro:
#### Error por repetición de email.
Si bien pueden haber múltiples emails con el mismo número de usuario, el email es una variable única, ya que es a partir de esta que se crean las listas personalizadas. Es por ello que, de repetirse, se imprimirá el mensaje "El email ya existe"
#### Error por un número inválido de caracteres.
Si el correo, usuario, o contraseña poseen un número de carácteres que no coincide con los pedidos, entonces se imprimirán los siguientes errores según corresponda: "Por favor, ingrese un correo válido", "La contraseña debe ser mayor a 8 caracteres y menor a 20", "El usuario debe ser mayor a 5 caracteres".
```python 
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
 ```
 ### Login:
#### Error por ingreso de contraseña incorrecta
Si la contraseña ingresada no coincide con el email introducido, entonces se imprmirá "Contraseña incorrecta, intente de nuevo".

### Error por ingreso de email inexistente
Si el email ingresado no se encuentra en la base de datos, entonces se imprimirá "El email no existe".

  ```python
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
  ```
### Listas personalizadas:
#### Error por repetición de nombre de lista o manga
  Finalmente, dado que el usuario puede crear numerosas listas, entonces si se intenta crear una nueva lista con un nombre ya presente en la base de datos, entonces se imprimirá "Ya existe una lista con ese nombre.".
  
## Cómo ejecutar el sistema (Deployment scripts)
 Dado que se usa una base de detos remota, entonces no es necesario ejecutar ningún archivo. No obstante, si se desea ejecutar el sistema desde el entorno local, entonces habría que  el archivo script.py, el cual crea la base de datos MangaList.

