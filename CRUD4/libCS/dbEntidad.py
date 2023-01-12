from flask import Flask, render_template, request, redirect
from libCS.db import CS_MySQL
from libCS.utils import mostrarInfoXConsola, tuplaToStr, tuplaToTupla
# from db import CS_MySQL
# from utils import mostrarInfoXConsola, tuplaToStr, tuplaToTupla

class CS_DB_CRUD_Entidad2():
  """El objeto CS_DB_CRUD_Entidad2 implementa una serie de métodos para facilitar la construcción de las sentencias SQL de un CRUD Básico. ....
  
  
  Soporta automáticamente las siguientes operaciones:
    - 
  
  El objetivo es ir haciéndolo crecer a medida que aparecen situaciones que haya que salvar y/o mejorar.

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

  def __init__(self, objDB: CS_MySQL, entidad, esEL, tabla,
               PKs, columnas, orderBy, whereBuscar="", FKs="", 
               FKsDescripcion="", FKsTabla="", FKsWhereJoin="") -> None:
    self.objDB = objDB
    self.entidad = entidad
    self.esEL = esEL
    self.tabla = tabla
    self.PKs = PKs
    self.columnas = columnas
    self.orderBy = orderBy
    self.whereBuscar = whereBuscar
    self.FKs = FKs
    self.FKsDescripcion = FKsDescripcion
    self.FKsTabla = FKsTabla
    self.FKsWhereJoin = FKsWhereJoin

###################################
#  Getters & Setters Propiedades  #
###################################

  def getDBUser(self)->str:
    return self.objDB.getDBUser()

  def getEntidad(self)->str:
    return self.entidad

  def getEsEl(self)->bool:
    return self.esEL

  def getColumnas(self)->str:
    return self.columnas
    
  def getFKs(self)->str:
    return self.FKs
    
  def getFKsTabla(self)->str:
    return self.FKsTabla

  def getWhereBuscar(self)->str:
    return self.whereBuscar

  def setOrderBy(self, newOrderBy)->None:
    self.orderBy = newOrderBy

  def getUltimaExcepcion(self)->tuple:
    return self.objDB.getUltimaExcepcion()

#########################
#  Métodos Repetidores  #
#########################

  def obtenerTodos(self):
    return self.objDB.obtenerTodos(self.getSelectAllStmt())

  def obtenerAlgunosBuscar(self, datos, condicionWhere="", newOrderBy=""):
    return self.objDB.obtenerAlgunos(self.getSelectSomeStmt(condicionWhere, newOrderBy), datos)

  def obtenerUno(self, datos):
    return self.objDB.obtenerUno(self.getSelectOneStmt(), datos)

  def crear(self, datos, descripcion)->bool:
    if self.objDB.ejecutarUnitario(self.getInsertStmt(), datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} {descripcion} se ha Creado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Crear {self.strEntidad()} {descripcion}")
      return False

  def modificar(self, datos, descripcion)->bool:
    if self.objDB.ejecutarUnitario(self.getUpdateStmt(), datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} {descripcion} se ha Modificado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Modificar {self.strEntidad()} {descripcion}")
      return False

  def borrar(self, datos)->bool:
    if self.objDB.ejecutarUnitario(self.getDeleteStmt(), datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} con clave {datos} se ha Borrado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Borrar {self.strEntidad()} con clave {datos}")
      return False

######################
#  Métodos Privados  #
######################

  def strEntidad(self)->str:
    if self.esEL:
      return "el " + self.entidad
    else:
      return "la " + self.entidad

  def getSelectAllStmt(self)->str:
    stmt = self.getSelectBaseStmt()
    stmt += " ORDER BY " + self.orderBy
    mostrarInfoXConsola(f"getSelectAllStmt(): {stmt}")
    return stmt
    
  def getSelectSomeStmt(self, condicionWhere="", newOrderBy="")->str:
    stmt = self.getSelectBaseStmt()
    if condicionWhere != "":
      if self.FKs != "":
        stmt += " AND " + condicionWhere
      else:
        stmt += " WHERE " + condicionWhere
    stmt += " ORDER BY "
    if newOrderBy == "":
      stmt += self.orderBy
    else:
      stmt += newOrderBy
    mostrarInfoXConsola(f"getSelectSomeStmt(): {stmt}")
    return stmt
    
  def getSelectOneStmt(self, datos=[])->str:
    stmt = self.getSelectBaseStmt()
    stmt += " " + self.getWhereByPKStmt((self.FKs != ""))
    mostrarInfoXConsola(f"getSelectOneStmt(): {stmt}")
    return stmt

  def getInsertStmt(self)->str:
    stmt = "INSERT INTO " + self.getTabla("") + " ("
    if isinstance(self.PKs, str):
      stmt += self.PKs + ", "
      valores = "NULL, "
    else:
      valores = ""
      for k in self.PKs:
        stmt += k + ", "
        valores += "NULL, "

    if self.FKs != "":
      if isinstance(self.FKs, str):
        stmt += self.FKs + ", "
        valores += "%s, "
      else:
        for k in self.FKs:
          stmt += k + ", "
          valores += "%s, "

    if isinstance(self.columnas, str):
      stmt += self.columnas
      valores += "%s"
    else:
      for c in self.columnas:
        stmt += c + ", "
        valores += "%s, "
      stmt = stmt[0:len(stmt)-2]
      valores = valores[0:len(valores)-2]
    stmt += ") VALUES (" + valores + ")"
    mostrarInfoXConsola(f"getInsertStmt(): {stmt}  /  Valores: {valores}")
    return stmt

  def getUpdateStmt(self)->str:
    stmt = "UPDATE " + self.getTabla("")
    stmt += " SET "
    if self.FKs != "":
      stmt += tuplaToStr(self.FKs, "", "=%s", ", ", False)
    stmt += tuplaToStr(self.columnas, "", "=%s", ", ", True)
    stmt += " " + self.getWhereByPKStmt(False)
    mostrarInfoXConsola(f"getUpdateStmt(): {stmt}")
    return stmt

  def getDeleteStmt(self)->str:
    stmt = "DELETE FROM " + self.getTabla("") + " " + self.getWhereByPKStmt(False)
    mostrarInfoXConsola(f"getDeleteStmt(): {stmt}")
    return stmt

  def getSelectBaseStmt(self)->str:
    stmt = "SELECT " + tuplaToStr(self.PKs, self.getTabla("."), "", ", ", False)
    if self.FKs != "":
      stmt += tuplaToStr(self.FKs, self.getTabla("."), "", ", ", False)
      if self.FKsDescripcion != "":
        tuplaPrefijoTablasFKs = tuplaToTupla(self.FKsTabla, "", ".")
        stmt += tuplaToStr(self.FKsDescripcion, tuplaPrefijoTablasFKs, "", ", ", False)
    stmt += tuplaToStr(self.columnas, self.getTabla("."), "", ", ", True) + " "
    stmt += "FROM " + self.getTabla("")
    if self.FKsDescripcion != "":
      stmt += ", " + tuplaToStr(self.FKsTabla, "", "", ", ", True)
      stmt += " WHERE " + self.FKsWhereJoin
    return stmt
     
  def getWhereByPKStmt(self, incluirTabla)->str:
    if incluirTabla: # Hay FKs y ya existe WHERE x el join
      return "AND " + tuplaToStr(self.PKs, self.getTabla("."), "=%s ", "AND ", True)
    else:
      return "WHERE " + tuplaToStr(self.PKs, "", "=%s ", "AND ", True)

  def getTabla(self, posfijo)->str:
    return self.tabla + posfijo