from flaskext.mysql import MySQL
from pymysql import IntegrityError, OperationalError

from libCS.utils import mostrarInfoXConsola

class CS_MySQL():

  SIN_EXCEPCION = ("OK", 0, "")

  def __init__(self, app, host, usr, pwd, port, db) -> None:
    self.app = app # Puntero a la app Flask
    self.mysql = MySQL()
    self.app.config['MYSQL_DATABASE_HOST'] = host
    self.app.config['MYSQL_DATABASE_USER'] = usr
    self.app.config['MYSQL_DATABASE_PASSWORD'] = pwd
    self.app.config['MYSQL_DATABASE_PORT'] = port
    self.app.config['MYSQL_DATABASE_BD'] = db
    self.mysql.init_app(app)
    self.resetUltimaExcepcion()

  def getUltimaExcepcion(self)->tuple:
    return self.ultimaExcepcion

  def setUltimaExcepcion(self, excepcion, codigo, descripcion)->None:
    self.ultimaExcepcion = (excepcion, codigo, descripcion)

  def resetUltimaExcepcion(self)->None:
    self.ultimaExcepcion = self.SIN_EXCEPCION

  def conectarDB(self):
    try:
      con = self.mysql.connect()
    except OperationalError as e:
      try:
        self.setUltimaExcepcion("OperationalError", int(e.args[0]), str(e.args[1]))
      except IndexError:
        print(f"****** MySQL Operational Error: {str(e)}")
      return None
    except Exception as e:
      try:
        self.setUltimaExcepcion("Exception", int(e.args[0]), str(e.args[1]))
      except IndexError:
        print(f"MySQL Exception Error: {str(e)}")
      return None
    self.resetUltimaExcepcion()
    return con

  def obtenerTodosConOtraDB(self, DB, stmt, datos=None):
    mostrarInfoXConsola(f"obtenerTodos(): {stmt}")
    # con = self.mysql.connect()
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
    return self.obtenerTodosConOtraDB(self.getDB(), stmt)

  def obtenerAlgunos(self, stmt, datos):
    return self.obtenerTodosConOtraDB(self.getDB(), stmt, datos)

  def obtenerUnoOtraDB(self, DB, stmt, datos):
    mostrarInfoXConsola(f"obtenerUno(): {stmt} {datos}")
    # con = self.mysql.connect()
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
    return self.obtenerUnoOtraDB(self.getDB(), stmt, datos)
    
  def ejecutarOtraDB(self, DB, stmt, datos):
    mostrarInfoXConsola(f"ejecutar(): {stmt} {datos}")
    # con = self.mysql.connect()
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
        print(f"****** MySQL Integrity Error: {str(e)}")
      con.rollback()    
      con.close()
      # raise IntegrityError(e.args[0])
      return False
    except Exception as e:
      try:
        self.setUltimaExcepcion("Exception", int(e.args[0]), str(e.args[1]))
        # print(f"MySQL Exception Error [{e.args[0]}]: {e.args[1]}")
      except IndexError:
        print(f"MySQL Exception Error: {str(e)}")
      return False
    if (regAfectados == 1):
      con.commit()
    else:
      con.rollback()    
    con.close()
    self.resetUltimaExcepcion()
    return (regAfectados == 1)

  def ejecutar(self, stmt, datos):
    return self.ejecutarOtraDB(self.getDB(), stmt, datos)

  def getDB(self)->str:
    return self.app.config['MYSQL_DATABASE_BD']