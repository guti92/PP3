from flask import Flask, render_template, url_for, flash
from flask import request, redirect, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Cliente, Usuario
from functools import wraps
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random
import string
import json
import datetime
import hashlib
import httplib2
#import requests
import os

app = Flask(__name__)

# Connect to Database and create database session
#engine = create_engine('admin:nopandea//postgres:@localhost/stg')
engine = create_engine('postgresql://admin:nopandea@localhost/stg')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Pantalla principal - Login
@app.route('/', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		state = ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		# store it in session for later use
		login_session['state'] = state
		return render_template('login2.html', STATE = state) 
	else:
		if request.method == 'POST':
			print ("dentro de POST login")
			usuario = session.query(Usuario).filter_by(
				username = request.form['username']).first()

			if usuario and valid_pw(request.form['username'],
								request.form['password'],
								usuario.pw_hash):
			
				login_session['username'] = request.form['username']
				#return render_template('public.html', username=login_session['username'])
				return redirect(url_for('ultimos5'))

			else:
				error = "Sus credenciales son erroneas o no esta registado."
				return render_template('login2.html', error = error)

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' not in login_session:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

#Password Hash
def make_salt():
	return ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		
def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256((name + pw + salt).encode('utf-8')).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)		

"""------------------------------------------------USUARIOS---------------------------------------------------"""

# Crear usuario
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()
	if request.method == 'GET':
		return render_template('add-user.html', usuario=usuario)
	else:
		if request.method == 'POST':
			if request.form ['password'] == request.form ['repeat-password']:
				username = request.form['username']
				password=request.form['password']
				rol = request.form['rol']
				

				pw_hash = make_pw_hash(username, password)
				nuevoUsuario = Usuario(
						username = username,
						rol = rol,
						pw_hash=pw_hash,
						fecha_creacion_u = datetime.datetime.now()) 
				session.add(nuevoUsuario)
				session.commit()
				login_session['username'] = request.form['username']
				return redirect(url_for('users'))
			else:
				error = "Las contraseñas ingresadas no coinciden, vuelva a intentarlo."
				return render_template('add-user.html', error = error, usuario=usuario)

#Ultimos 5 clientes creados
@app.route('/welcome', methods=['GET', 'POST'])
def ultimos5():
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()
	ultimos = session.query(Cliente).order_by(Cliente.fecha_creacion.desc()).limit(5).all()
	if request.method == 'GET':
		return render_template('welcome.html', ultimos = ultimos, usuario=usuario)

#Listar usuarios
@app.route('/usuarios', methods=['GET', 'POST'])
def users():
	users = session.query(Usuario).all()
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()

	return render_template('users.html', users = users, usuario=usuario)

#Editar Usuario
@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def edit_user(id):

	usuario = session.query(Usuario).filter_by(id = id).one()

	if request.method == 'GET':
		username = login_session['username']
		return render_template('edit-user.html', usuario = usuario)
	else:
		if request.method == 'POST':
			print(id)
			usuario = session.query(Usuario).filter_by(id = id).one()
			if request.form ['password'] == request.form ['repeat-password']:
				username = request.form['username']
				password = request.form['password']
				rol = request.form['rol']

				pw_hash = make_pw_hash(username, password)

				usuario.username = username,
				usuario.pw_hash = pw_hash,
				usuario.rol = rol
				session.commit()
				return redirect(url_for('users'))
			else:
				error = "Las contraseñas ingresadas no coinciden, Vuelva a intentarlo."
				return render_template('edit-user.html', error = error, usuario=usuario)


#Eliminar Usuario
@app.route('/usuarios/eliminar/<int:id>', methods=['GET', 'POST'])
def delete_user(id):

	usuario = session.query(Usuario).filter_by(id = id).one()

	if request.method == 'GET':
		return render_template('delete-user.html', usuario = usuario)
	else:
		if request.method == 'POST':
			session.delete(usuario)
			session.commit()
			return redirect(url_for('users'))


"""------------------------------------------------CLIENTES---------------------------------------------------"""

# Crear cliente
@app.route('/alta_cliente', methods=['GET', 'POST'])
def add_cli():
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()
	if request.method == 'GET':
		return render_template('add-cli.html', usuario=usuario)
	else:
		if request.method == 'POST':
			nombre = request.form['nombre']
			telefono=request.form['telefono']
			tipo_contacto = request.form['tipo_contacto']
			direccion = request.form['direccion']
			email = request.form['email'] 
			tipo_contrato = request.form['tipo_contrato'] 
			userid = login_session['username']

			#pw_hash = make_pw_hash(username, password)
			nuevoCliente = Cliente(
					nombre = nombre,
					telefono = telefono,
					tipo_contacto = tipo_contacto,
					fecha_creacion = datetime.datetime.now(),
					direccion = direccion,
					email = email,
					tipo_contrato = tipo_contrato,
					userid = userid
					)
			session.add(nuevoCliente)
			session.commit()
			#login_session['username'] = request.form['username']
			return redirect(url_for('clients'))

# Listar clientes
@app.route('/clientes', methods=['GET', 'POST'])
def clients():
	clients = session.query(Cliente).all()
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()

	if 'username' in login_session:
		username = login_session['username']

	return render_template('clients.html', clients=clients, username=username, usuario=usuario)

"""# Buscar cliente
@app.route('/buscar-cliente', methods=['GET', 'POST'])
def search_client():
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()"""


#Editar Cliente
@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def edit_cli(id):

	cliente = session.query(Cliente).filter_by(id = id).one()
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()

	if request.method == 'GET':
		username = login_session['username']
		return render_template('edit-cli.html', cliente = cliente, usuario=usuario)
	else:
		if request.method == 'POST':
			print(id)
			cliente = session.query(Cliente).filter_by(id = id).one()
			cliente.nombre = request.form['nombre'],
			cliente.telefono = request.form['telefono'],
			cliente.tipo_contacto = request.form['tipo_contacto'],
			cliente.email = request.form['email'],
			cliente.direccion = request.form['direccion'],
			cliente.tipo_contrato = request.form['tipo_contrato'],
			cliente.userid = login_session['username']
			session.commit()
			return redirect(url_for('clients'))

#Eliminar Cliente
@app.route('/clientes/eliminar/<int:id>', methods=['GET', 'POST'])
def delete_cli(id):

	cliente = session.query(Cliente).filter_by(id = id).one()
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()

	if request.method == 'GET':
		return render_template('delete-cli.html', cliente = cliente, usuario=usuario)
	else:
		if request.method == 'POST':
			session.delete(cliente)
			session.commit()
			return redirect(url_for('clients'))

# Cambiar contraseña
@app.route('/newpass', methods=['GET', 'POST'])
def newpass():
	userlog= session.query(Usuario).filter_by(
		username = login_session['username'], id = id)
	usuario = session.query(Usuario).filter_by(
				username = login_session['username']).first()
	
	if request.method == 'GET':
		return render_template('new-pass.html', userlog = userlog, usuario=usuario)
	else:
		if request.method == 'POST':
			userlog= session.query(Usuario).filter_by(
			username = login_session['username']).one()
			if request.form ['password'] == request.form ['repeat-password']:
				password = request.form ['password']
				username = login_session['username']
				pw_hash = make_pw_hash(username, password)
				
				userlog.username = username,
				userlog.pw_hash = pw_hash
				session.commit()
				flash ('Contraseña cambiada con éxito!')
				return redirect(url_for('login'))

			else:
				error = "Las contraseñas ingresadas no coinciden, Vuelva a intentarlo."
				return render_template('new-pass.html', error = error)
			

@app.route('/logout')
def logout():
		
		del login_session['username']

		#return render_template('public.html')
		return redirect(url_for('login'))


if __name__=='__main__':
	app.secret_key = "secret key"
	app.run('0.0.0.0', 5000, debug=True)