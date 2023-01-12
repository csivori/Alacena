from flask import Flask, current_app
from flaskext.mysql import MySQL

#Creo la app Flask
print("1.-Voy a crear app Flask")
appFlask = Flask(__name__)
print(f"2.-Creada appFlask: {appFlask}")

print("3.-Voy a setear el string de conexion a la DB de la appFlask")
appFlask.config['MYSQL_DATABASE_HOST'] = 'cafeigso.mysql.pythonanywhere-services.com'
appFlask.config['MYSQL_DATABASE_USER'] = 'cafeigso'
appFlask.config['MYSQL_DATABASE_PASSWORD'] = 'mardel1234'
appFlask.config['MYSQL_DATABASE_BD'] = 'cafeigso$alacena'
appFlask.config['MYSQL_DATABASE_PORT'] = 3306
print(f"4.-Seteada el string de conexion a la DB de la app Flask {appFlask.config}")

print("5.-Voy a instanciar el objeto MySQL")
mysql = MySQL(appFlask)
print(f"6.-Instanciado el objeto MySQL: {MySQL}")

# Pruebo Conectarme
print("7.-Voy a conectarme a MySQL")
with appFlask.app_context():
  con = mysql.connection.cursor()
print(f"8.-Conectado a MySQL: {con}")

print("9.-Voy a cerrar la conexión a MySQL")
con.close()
print("10.-Cerrada la conexión a MySQL")

print("11.-Fin Prueba")
