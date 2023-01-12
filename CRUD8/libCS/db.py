from flask import Flask
from flaskext.mysql import MySQL
from pymysql import IntegrityError, OperationalError
from libCS.utils import mostrarErrorXConsola, mostrarInfoXConsola
# from utils import mostrarErrorXConsola, mostrarInfoXConsola

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
    self.instanciarMySQL(host, usr, pwd, port, db)

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

  def instanciarMySQL(self, host, usr, pwd, port, db)->None:
    mostrarInfoXConsola(mensaje=f"1.Instanciando MySQL con {host}/{usr}/{pwd}/{port}/{db}",
                        modulo="db.py", funcion="instanciarMySQL()")
    if hasattr(self, "appFlask") and self.appFlask != None:
      mostrarInfoXConsola(mensaje=f"2.Seteo el connection string en Flask con {host}/{usr}/{pwd}/{port}/{db}",
                          modulo="db.py", funcion="instanciarMySQL()")

      # Seteo el connection string en Flask
      self.appFlask.config['MYSQL_DATABASE_HOST'] = host
      self.appFlask.config['MYSQL_DATABASE_USER'] = usr
      self.appFlask.config['MYSQL_DATABASE_PASSWORD'] = pwd
      self.appFlask.config['MYSQL_DATABASE_PORT'] = port
      self.appFlask.config['MYSQL_DATABASE_BD'] = db

      # Creo nueva instancia de MySQL
      if hasattr(self, "mysql") and self.mysql != None:
        mostrarInfoXConsola(mensaje=f"3.Eliminando la instancia que ya existe de MySQL {self.mysql}",
                            modulo="db.py", funcion="instanciarMySQL()")
        # del self.mysql
      else:
        mostrarInfoXConsola(mensaje=f"3.1.Creando la nueva instancia de MySQL",
                            modulo="db.py", funcion="instanciarMySQL()")
        self.mysql = MySQL(self.appFlask)
        mostrarInfoXConsola(mensaje=f"3.2.Creada la nueva instancia de MySQL {self.mysql}",
                            modulo="db.py", funcion="instanciarMySQL()")

      self.resetUltimaExcepcion()
      mostrarInfoXConsola(mensaje=f"4.Ultima Excepción Reseteada {self.getUltimaExcepcion()[0]}",
                          modulo="db.py", funcion="instanciarMySQL()")

      # Pruebo Conectarme
      mostrarInfoXConsola(mensaje=f"5.Inicio Prueba de Conexión",
                          modulo="db.py", funcion="instanciarMySQL()")
      con = self.conectarDB()
      mostrarInfoXConsola(mensaje=f"6.Fin Prueba de Conexión {con=} {self.getUltimaExcepcion()[0]}",
                          modulo="db.py", funcion="instanciarMySQL()")
      if con == None:
        mostrarInfoXConsola(mensaje=f"7.Conexión Vacía ERROR",
                            modulo="db.py", funcion="instanciarMySQL()")
        return False
      con.close()
      mostrarInfoXConsola(mensaje=f"7.Conexión Cerrada",
                          modulo="db.py", funcion="instanciarMySQL()")
      return True
    return False

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

  def obtenerTodosConOtraDB(self, DB, stmt, datos=None)->tuple[tuple, ...]:
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
    mostrarInfoXConsola(f"{stmt=} {datos=}", "db.py", "obtenerTodosConOtraDB()")
    con = self.conectarDB()
    if con == None:
      return None
    cursor = con.cursor() # guarda el Result Set
    cursor.execute("USE " + DB)
    if datos == None or datos == "":
      cursor.execute(stmt)
    else:
      cursor.execute(stmt, datos)
    result = cursor.fetchall()
    con.commit()
    con.close()
    self.resetUltimaExcepcion()
    return result

  def obtenerTodos(self, stmt)->tuple[tuple, ...]:
    """Ejecuta un Select SQL que puede obtener un conjunto de varios registros, típicamente un SELECT sin condición WHERE. Retornando una Tupla de Tuplas con el conjunto de resultado o None si falló.

    :param stmt: SELECT SQL que se desea ejecutar

    :return: Tupla de Tuplas: Exito / None: Falló
    :rtype: Tupla / None
    """
    return self.obtenerTodosConOtraDB(self.getDB(), stmt)

  def obtenerAlgunos(self, stmt, datos)->tuple[tuple, ...]:
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

  def obtenerUnoConOtraDB(self, DB, stmt, datos)->(tuple | None):
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

  def obtenerUno(self, stmt, datos)->(tuple | None):
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
    
  def ejecutarUnitarioConOtraDB(self, DB, stmt, datos)->bool:
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

  def ejecutarUnitario(self, stmt, datos)->bool:
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

  def getCurrentConnectionString(self)->str:
    """Retorna el String de Conexión en uso

    :return: "Connection String: {dbHost=}/{dbUsr=}/{dbPwd=}/{dbPort=}/{dbName=}"
    :rtype: str
    """
    dbHost = self.appFlask.config['MYSQL_DATABASE_HOST']
    dbUsr = self.getDBUser()
    dbPwd = self.appFlask.config['MYSQL_DATABASE_PASSWORD']
    dbPort = self.appFlask.config['MYSQL_DATABASE_PORT']
    dbName = self.getDB()
    return f"Connection String: {dbHost=}/{dbUsr=}/{dbPwd=}/{dbPort=}/{dbName=}"

  def getDB(self)->str:
    """Retorna la DB en uso de la Conexión

    :return: "{dbName}"
    :rtype: str
    """
    return self.appFlask.config['MYSQL_DATABASE_BD']

  def getDBUser(self)->str:
    """Retorna el Usuario en uso de la Conexión

    :return: "{dbUser}"
    :rtype: str
    """
    return self.appFlask.config['MYSQL_DATABASE_USER']

