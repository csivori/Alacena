from flask import Flask, request
from flask import render_template
from alacena import Alacena
import libCS
from libCS.utils import mostrarInfoXConsola
from libCS.db import CS_MySQL
from libCS.dbEntidad import CS_DB_CRUD_Entidad2_FK
from libCS.dbInit import CS_DB_Initialization
from libCS.webEntidad import CS_WEB_CRUD_Entidad

#Defino el Ambiente
__ambiente__ = "L" # Web Server y MySQL Server local en la PC
# __ambiente__ = "F" # Web Server local en la PC y MySQL Server en Free MySQL Hosting
# __ambiente__ = "P" # Web Server y MySQL Server en www.PythonAnywhere.com
# __ambiente__ = "G" # Web Server y MySQL Server en Google Cloud

#Creo la app Flask
appFlask = Flask(__name__)

#Creo la conexión a la DB
if __ambiente__ == "L":
  mysql = CS_MySQL(appFlask=appFlask, host='localhost', usr='root', pwd='', port=3306, db='crud_python_tf')
elif __ambiente__ == "F":
  mysql = CS_MySQL(appFlask=appFlask, host='sql10.freemysqlhosting.net', usr='sql10588086', pwd='3tQCvx6VMZ', port=3306, db='sql10588086')
elif __ambiente__ == "P":
  mysql = CS_MySQL(appFlask=appFlask, host='cafeigso.mysql.pythonanywhere-services.com', usr='cafeigso', pwd='mardel1234', port=3306, db='cafeigso$alacena')
elif __ambiente__ == "G":
  pass

test = CS_DB_Initialization(appFlask=appFlask, mysql=mysql)
alacena = Alacena(appFlask=appFlask, objDB=mysql)

@appFlask.route('/')
def login():
  return render_template('index.html', accesoATablas="hidden") 

if __name__ == '__main__':
  if __ambiente__ == "L" or __ambiente__ == "F":
    appFlask.run(debug=True, host='localhost', port=5000)
  elif __ambiente__ == "P":
    appFlask.run(debug=False, port=5000)
