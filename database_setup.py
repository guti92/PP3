import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Cliente(Base):
	__tablename__ = 'cliente'

	id = Column(Integer, primary_key=True)
	
	nombre = Column(String(50), nullable=False)
	telefono = Column(String(250), nullable=False)
	fecha_creacion = Column(DateTime, nullable=False)
	tipo_contacto = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	direccion = Column(String(250), nullable=False)
	tipo_contrato = Column(String(250), nullable=False)
	userid = Column(String(250), nullable=False)
	#user_id = Column(Integer, ForeignKey('user.id'))
	#user = relationship('User')


class Usuario(Base):
	__tablename__ = 'usuario'

	id = Column(Integer, primary_key=True)

	username = Column(String(50), nullable=False)
	rol = Column(String(250), nullable=False)
	pw_hash = Column(String(250), nullable=False)
	fecha_creacion_u = Column(DateTime, nullable=False)
	#posteo = relationship('Blog')

#engine = create_engine('postgresql://admin:nopandea@localhost/stg')
engine = create_engine('postgresql://admin:nopandea@localhost/stg')
Base.metadata.create_all(engine)
