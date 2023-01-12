from flask import Flask
from flaskext.mysql import MySQL
from pymysql import IntegrityError, OperationalError

from libCS.utils import mostrarErrorXConsola, mostrarInfoXConsola

class CS_MySQL():
  """El objeto CS_MySQL implementa una serie de métodos para facilitar la interaccion de la aplicación con la Base de Datos. El objetivo es ir haciéndolo crecer a medida que aparecen situaciones que haya que salvar y/o mejorar.

  :param appFlask: puntero al objeto Flask de app.py 
  :param host: Servidor. Típicamente localhost
  :param usr: Usuario. Típicamente root
  :param pwd: Contraseña. Típicamente ""
  :param port: Puerto. Típicamente 3306 ó 3307. 
  :param db: DB con la que interactúan los queries x defecto.

Principales Métodos:
  - obtenerTodos(stmt): -> ((<col1>,..,<colN>),(<col1>,..,<colN>),..)
  - obtenerAlgunos(stmt, datos): -> ((<col1>,..,<colN>),(<col1>,..,<colN>),..)
  - obtenerUno(stmt, datos): -> (<col1>,<col2>,..,<colN>)
  - ejecutarUnitario(stmt, datos): -> True / False
  - getUltimaExcepcion(): -> ("<excepcion>", <código>, "<descripcion>")
  """

  SIN_EXCEPCION = ("OK", 0, "")

  def __init__(self, appFlask: Flask, host, usr, pwd, port, db) -> None:
    self.appFlask = appFlask # Puntero a la app Flask
    self.mysql = MySQL()
    self.appFlask.config['MYSQL_DATABASE_HOST'] = host
    self.appFlask.config['MYSQL_DATABASE_USER'] = usr
    self.appFlask.config['MYSQL_DATABASE_PASSWORD'] = pwd
    self.appFlask.config['MYSQL_DATABASE_PORT'] = port
    self.appFlask.config['MYSQL_DATABASE_BD'] = db
    self.mysql.init_app(appFlask)
    self.resetUltimaExcepcion()

  def getUltimaExcepcion(self)->tuple:
    """Rescata de la memoria la última Excepción ocurrida, para que pueda ser consultada por instancias superiores.

    :return: Tupla(excepcion, codigo, descripcion)
    :rtype: (String, int, String)
    """
    return self.ultimaExcepcion

  def setUltimaExcepcion(self, excepcion, codigo, descripcion)->None:
    """Guarda en la memoria la última Excepción ocurrida, para que pueda ser consultada por instancias superiores.

    :param excepcion: String con la Excepcion capturada en el except 
    :param codigo: Int con el código de Error. Típicamente ex.arg[0].
    :param descripcion: String con la descripción del Error. Típicamente ex.arg[1].
    """
    self.ultimaExcepcion = (excepcion, codigo, descripcion)

  def resetUltimaExcepcion(self)->None:
    """Limpia de la memoria la última Excepción ocurrida."""
    self.ultimaExcepcion = self.SIN_EXCEPCION

  def conectarDB(self):
    """Establece una conexión con el motor de Base de Datos para ejecutar sentencias SQL. Retornando una Conection o None si algo falló.

    :return: Connection: Exito / None: Falló
    :rtype: Connection / None
    """
    try:
      con = self.mysql.connect()
    except OperationalError as e:
      try:
        self.setUltimaExcepcion("OperationalError", int(e.args[0]), str(e.args[1]))
      except IndexError:
        self.setUltimaExcepcion("OperationalError", 99999, str(e))
        mostrarErrorXConsola("db.py", "conectarDB()", f"MySQL Operational Error: {str(e)}")
      return None
    except Exception as e:
      try:
        self.setUltimaExcepcion("Exception", int(e.args[0]), str(e.args[1]))
      except IndexError:
        self.setUltimaExcepcion("Exception", 99999, str(e))
        mostrarErrorXConsola("db.py", "conectarDB()", f"MySQL Exception: {str(e)}")
      return None
    self.resetUltimaExcepcion()
    return con

  def obtenerTodosConOtraDB(self, DB, stmt, datos=None):
    """Ejecuta un Select SQL que puede obtener un conjunto de varios registros, típicamente un SELECT con o sin condición WHERE. Retornando una Tupla de Tuplas con el conjunto de resultado o None si falló.

    :param DB: DB en la que se desea ejecutar
    :param stmt: SELECT SQL que se desea ejecutar
    :param datos: los parametros utilizados en el query
    :type datos: tuple, list or dict

    :return: Tupla de Tuplas: Exito / None: Falló
    :rtype: Tupla / None

    Si datos es una lista o tupla, usar %s como variable en el stmt.
    Si datos es un diccionario, usar %(nombre)s como variable en el stmt. 
    """
    mostrarInfoXConsola(stmt, "db.py", "obtenerTodosConOtraDB()")
    con = self.conectarDB()
    if con == None:
      return None
    cursor = con.cursor() # guarda el Result Set
    cursor.execute("USE " + DB)
    if datos == None:
      cursor.execute(stmt)
    else:
      cursor.execute(stmt, datos)
    result = cursor.fetchall()
    con.commit()
    con.close()
    self.resetUltimaExcepcion()
    return result

  def obtenerTodos(self, stmt):
    """Ejecuta un Select SQL que puede obtener un conjunto de varios registros, típicamente un SELECT sin condición WHERE. Retornando una Tupla de Tuplas con el conjunto de resultado o None si falló.

    :param stmt: SELECT SQL que se desea ejecutar

    :return: Tupla de Tuplas: Exito / None: Falló
    :rtype: Tupla / None
    """
    return self.obtenerTodosConOtraDB(self.getDB(), stmt)

  def obtenerAlgunos(self, stmt, datos):
    """Ejecuta un Select SQL que puede obtener un conjunto de varios registros, típicamente un SELECT con o sin condición WHERE. Retornando una Tupla de Tuplas con el conjunto de resultado o None si falló.

    :param stmt: SELECT SQL que se desea ejecutar
    :param datos: los parametros utilizados en el query
    :type datos: tuple, list or dict

    :return: Tupla de Tuplas: Exito / None: Falló
    :rtype: Tupla / None

    Si datos es una lista o tupla, usar %s como variable en el stmt.
    Si datos es un diccionario, usar %(nombre)s como variable en el stmt. 
    """
    return self.obtenerTodosConOtraDB(self.getDB(), stmt, datos)

  def obtenerUnoConOtraDB(self, DB, stmt, datos):
    """Ejecuta un Select SQL que obtiene solo 1 registro, típicamente un SELECT x clave Primaria. Retornando una Tupla con el registro resultado o None si falló.

    :param DB: DB en la que se desea ejecutar
    :param stmt: SELECT SQL que se desea ejecutar
    :param datos: los parametros utilizados en el query
    :type datos: tuple, list or dict

    :return: Tupla: Exito / None: Falló
    :rtype: Tupla / None

    Si datos es una lista o tupla, usar %s como variable en el stmt.
    Si datos es un diccionario, usar %(nombre)s como variable en el stmt. 
    """
    mostrarInfoXConsola(f"{stmt=} {datos=}", "db.py", "obtenerUnoConOtraDB()")
    con = self.conectarDB()
    if con == None:
      return None
    cursor = con.cursor() # guarda el Result Set
    cursor.execute("USE " + DB)
    cursor.execute(stmt, datos)
    result = cursor.fetchone()
    con.commit()
    con.close()
    self.resetUltimaExcepcion()
    return result

  def obtenerUno(self, stmt, datos):
    """Ejecuta un Select SQL que obtiene solo 1 registro, típicamente un SELECT x clave Primaria. Retornando una Tupla con el registro resultado o None si falló.

    :param stmt: SELECT SQL que se desea ejecutar
    :param datos: los parametros utilizados en el query
    :type datos: tuple, list or dict

    :return: Tupla de Tuplas: Exito / None: Falló
    :rtype: Tupla / None

    Si datos es una lista o tupla, usar %s como variable en el stmt.
    Si datos es un diccionario, usar %(nombre)s como variable en el stmt. 
    """
    return self.obtenerUnoConOtraDB(self.getDB(), stmt, datos)
    
  def ejecutarUnitarioConOtraDB(self, DB, stmt, datos):
    """Ejecuta una instrucción SQL que afecte solo 1 registro, típicamente un INSERT de un nuevo registro, o un UPDATE o DELETE x clave Primaria. Retornando True o False según haya impactado 1 registro

    :param DB: DB en la que se desea ejecutar
    :param stmt: instrucción SQL que se desea ejecutar
    :param datos: los parametros utilizados en el query
    :type datos: tuple, list or dict

    :return: True: Exito / False: Falló
    :rtype: bool

    Si datos es una lista o tupla, usar %s como variable en el stmt.
    Si datos es un diccionario, usar %(nombre)s como variable en el stmt. 
    """
    mostrarInfoXConsola(f"{stmt=} {datos=}", "db.py", "ejecutarConOtraDB()")
    con = self.conectarDB()
    if con == None:
      return False

    regAfectados = 0
    cursor = con.cursor() # guarda el Result Set
    try:
      cursor.execute("USE " + DB)
      regAfectados = cursor.execute(stmt, datos)
    except IntegrityError as e:
      try:
        self.setUltimaExcepcion("IntegrityError", int(e.args[0]), str(e.args[1]))
      except IndexError:
        self.setUltimaExcepcion("IntegrityError", 99999, str(e))
        mostrarErrorXConsola("db.py", "ejecutarUnitarioConOtraDB()", f"MySQL Integrity Error: {str(e)}")
      con.rollback()    
      con.close()
      # raise IntegrityError(e.args[0])
      return False
    except Exception as e:
      try:
        self.setUltimaExcepcion("Exception", int(e.args[0]), str(e.args[1]))
      except IndexError:
        self.setUltimaExcepcion("Exception", 99999, str(e))
        mostrarErrorXConsola("db.py", "ejecutarUnitarioConOtraDB()", f"MySQL Exception Error: {str(e)}")
      return False
    if (regAfectados == 1):
      con.commit()
    else:
      con.rollback()    
    con.close()
    self.resetUltimaExcepcion()
    return (regAfectados == 1)

  def ejecutarUnitario(self, stmt, datos):
    """Ejecuta una instrucción SQL que afecte solo 1 registro, típicamente un INSERT de un nuevo registro, o un UPDATE o DELETE x clave Primaria. Retornando True o False según haya impactado 1 registro

    :param stmt: instrucción SQL que se desea ejecutar
    :param datos: los parametros utilizados en el query
    :type datos: tuple, list or dict

    :return: True: Exito / False: Falló
    :rtype: bool

    Si datos es una lista o tupla, usar %s como variable en el stmt.
    Si datos es un diccionario, usar %(nombre)s como variable en el stmt. 
    """
    return self.ejecutarUnitarioConOtraDB(self.getDB(), stmt, datos)

  def getDB(self)->str:
    return self.appFlask.config['MYSQL_DATABASE_BD']

  def getDBUser(self)->str:
    return self.appFlask.config['MYSQL_DATABASE_USER']