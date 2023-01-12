from flask import Flask, render_template, request, redirect
from libCS.db import CS_MySQL
from libCS.utils import mostrarErrorXConsola, mostrarInfoXConsola, tuplaToStr, tuplaToTupla
# from db import CS_MySQL
# from utils import mostrarErrorXConsola, mostrarInfoXConsola, tuplaToStr, tuplaToTupla

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
               PKs, columnas, columnasSelect, orderBy, whereBuscar="", objFKs=None) -> None:
    self.objDB = objDB
    self.entidad = entidad
    self.esEL = esEL
    self.tabla = tabla
    self.PKs = PKs
    if isinstance(columnas, str) and columnas.count(",") > 0:
      mostrarErrorXConsola("dbEntidad", "init", "Se definieron múltiples columnas sin utilizar tupla !!")
      raise Exception
    else:
      self.columnas = columnas
    self.columnasSelect = columnasSelect
    self.orderBy = orderBy
    self.whereBuscar = whereBuscar
    self.objFKs = objFKs

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

  def ejecutarUnitario(self, datos, descripcion, stmt, accionEnParticipioPasado)->bool:
    if self.objDB.ejecutarUnitario(stmt, datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} {descripcion} se ha {accionEnParticipioPasado} EXITOSAMENTE!")
      return True
    else:
      if self.getUltimaExcepcion()[2].strip() != "OK:[0]":
        mostrarInfoXConsola(f"No fue necesario ser {accionEnParticipioPasado} {self.strEntidad()} {descripcion}")
      else:
        mostrarInfoXConsola(f"No pudo ser {accionEnParticipioPasado} {self.strEntidad()} {descripcion}")
      return False

  def crear(self, datos, descripcion)->bool:
    return self.ejecutarUnitario(datos, descripcion, self.getInsertStmt(), "Creado")

  def modificar(self, datos, descripcion)->bool:
    return self.ejecutarUnitario(datos, descripcion, self.getUpdateStmt(), "Modificado")

  def borrar(self, datos)->bool:
    return self.ejecutarUnitario(datos, f"con clave {datos}", self.getDeleteStmt(), "Borrado")

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
      if self.tieneFK():
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
    
  def getSelectOneStmt(self)->str:
    stmt = self.getSelectBaseStmt()
    stmt += " " + self.getWhereByPKStmt(self.tieneFK())
    mostrarInfoXConsola(f"getSelectOneStmt(): {stmt}")
    return stmt

  def getInsertStmt(self)->str:
    stmt = "INSERT INTO " + self.getTabla("") + " ("

# Agrego las columnas y valores PK
    if isinstance(self.PKs, str):
      stmt += self.PKs + ", "
      valores = "NULL, "
    else:
      valores = ""
      for k in self.PKs:
        stmt += k + ", "
        valores += "NULL, "

# Agrego las columnas y valores NO PK
    if isinstance(self.columnas, str):
      stmt += self.columnas
      valores += "%s"
    else:
      for c in self.columnas:
        stmt += c + ", "
        valores += "%s, "
      stmt = stmt[0:len(stmt)-2]
      valores = valores[0:len(valores)-2]

# Agrego las columnas y valores FK
    columnasFK, valoresFK = self.getInsertStmtFK()
    stmt += columnasFK
    valores += valoresFK

# Concateno el Insert
    stmt += ") VALUES (" + valores + ")"
    mostrarInfoXConsola(f"getInsertStmt(): {stmt}  /  Valores: {valores}")
    return stmt

  def getUpdateStmt(self)->str:
    stmt = "UPDATE " + self.getTabla("")
    stmt += " SET "

# Agrego las columnas y valores NO PK
    stmt += tuplaToStr(self.columnas, "", "=%s", ", ", True)

# Agrego las columnas y valores FK
    columnasFK = self.getUpdateStmtFK()
    stmt += columnasFK

# Concateno el Update con Where x PK
    stmt += " " + self.getWhereByPKStmt(False)
    mostrarInfoXConsola(f"getUpdateStmt(): {stmt}")
    return stmt

  def getDeleteStmt(self)->str:
    stmt = "DELETE FROM " + self.getTabla("") + " " + self.getWhereByPKStmt(False)
    mostrarInfoXConsola(f"getDeleteStmt(): {stmt}")
    return stmt

  def getSelectBaseStmt(self)->str:
# Obtengo las columnas, tablas y joins de la o las FK
    columnasFK, tablasFK, wheresFK = self.getSelectBaseStmtFKs()

# Agrego las columnas clave de esta Entidad
    stmt = "SELECT " + tuplaToStr(self.PKs, self.getTabla("."), "", ", ", False)

# Agrego las columnas no clave de esta Entidad
    stmt += tuplaToStr(self.columnas, self.getTabla("."), "", ", ", True)

# Agrego las columnas de la o las FK
    if columnasFK != "":
      if stmt[-1] == " ":
        stmt = stmt[:len(stmt)-1]
      stmt += ", " + columnasFK

# Agrego las columnas Extras para el Select
    if self.columnasSelect != "":
      stmt += ", " + self.columnasSelect

# Agrego la tabla de esta Entidad
    stmt += " FROM " + self.getTabla("")

# Agrego las tablas de la o las FK
    if tablasFK != "":
      stmt += ", " + tablasFK

# Agrego el join si hay FK
    if wheresFK != "":
      stmt += " WHERE " + wheresFK

    return stmt
     
  def getSelectBaseStmtFKs(self)->(tuple):
    columnas = ""
    tablas = ""
    joins = ""
    if self.objFKs != None:
      if isinstance(self.objFKs, tuple):
        for objFK in self.objFKs:
          columna, tabla, join = objFK.getSelectBaseStmtFKs()
          if columna != "":
            if columnas != "":
              columnas += ", "
            columnas += columna
          if tabla != "":
            if tablas != "":
              tablas += ", "
            tablas += tabla
          if join != "":
            if joins != "":
              joins += " AND "
            joins += join
      else:
        columnas, tablas, joins = self.objFKs.getSelectBaseStmtFKs()
    return columnas, tablas, joins

  def getInsertStmtFK(self)->str:
    columnasFK = ""
    valoresFK = ""
    if self.objFKs != None:
      if isinstance(self.objFKs, tuple):
        for objFK in self.objFKs:
          columnasFK += ", " + objFK.getColFK()
          valoresFK += ", %s"
      else:
        columnasFK = ", " + self.objFKs.getColFK()
        valoresFK = ", %s"
    return columnasFK, valoresFK

  def getUpdateStmtFK(self)->str:
    columnasFK = ""
    if self.objFKs != None:
      if isinstance(self.objFKs, tuple):
        for objFK in self.objFKs:
          columnasFK += ", " + objFK.getColFK() + "=%s"
      else:
        columnasFK = ", " + self.objFKs.getColFK() + "=%s"
    return columnasFK

  def getWhereByPKStmt(self, incluirTabla)->str:
    if incluirTabla: # Hay FKs y ya existe WHERE x el join
      return "AND " + tuplaToStr(self.PKs, self.getTabla("."), "=%s ", "AND ", True)
    else:
      return "WHERE " + tuplaToStr(self.PKs, "", "=%s ", "AND ", True)

  def getFieldsFromScreen(self)->(tuple):
    campos = []
# Agrego los campos NO PK
    if self.columnas != None:
      if isinstance(self.columnas, tuple):
        for columna in self.columnas:
          campos.append(columna)
      else:
        campos.append(self.columnas)

# Agrego los campos FK
    if self.objFKs != None:
      if isinstance(self.objFKs, tuple):
        for objFK in self.objFKs:
          campos.append(objFK.getColFK())
      else:
        campos.append(self.objFKs.getColFK())

# Retorno la Tupla con los campos NO PK y FK para matchear con el query de Insert y Update
    return tuple(campos)

  def getTabla(self, posfijo)->str:
    return self.tabla + posfijo

  def tieneFK(self)->bool:
    return (self.objFKs != None)

class CS_DB_CRUD_Entidad2_FK():
  """El objeto CS_DB_CRUD_Entidad2_FK implementa una serie de métodos para concentrar los atributos y métodos para incluir una clave foranea en un objeto de tipo CS_DB_CRUD_Entidad2"""
  def __init__(self, tabla, colFK, tablaFK, descripcionFK, whereJoinFK, objFK=None) -> None:
    self.tabla = tabla
    self.colFK = colFK
    self.tablaFK = tablaFK
    self.descripcionFK = descripcionFK
    self.whereJoinFK = whereJoinFK
    self.objFK = objFK

###################################
#  Getters & Setters Propiedades  #
###################################

  def getColFK(self)->str:
    return self.colFK

  def getTablaFK(self)->str:
    return self.tablaFK

  def getObjFK(self):
    return self.objFK

######################
#  Métodos Públicos  #
######################

  def getSelectBaseStmtFKs(self)->(tuple):
    columnas = self.tabla + "." + self.colFK + ", "
    if self.descripcionFK[0] == "(":
      columnas += self.descripcionFK 
    else:
      columnas += self.tablaFK + "." + self.descripcionFK 
    return columnas, self.tablaFK, self.whereJoinFK 


# p = CS_DB_CRUD_Entidad2(None, None, None, "productos", "id", ("descripcion", "precio"), 
#                         "descripcion", "descripcion like %s", 
#                         (CS_DB_CRUD_Entidad2_FK("productos", "id_grupo", "grupos", "descripcion", 
#                                                 "productos.id_grupo = grupos.id"),
#                         CS_DB_CRUD_Entidad2_FK("productos", "id_unidad", "unidades", "descripcion", 
#                                                "productos.id_unidad = unidades.id")))
# # s = p.getSelectAllStmt()
# # s = p.getSelectSomeStmt("productos.descripcion like '%pepe%'", "productos.descripcion")
# # s = p.getSelectOneStmt()
# s = p.getInsertStmt()
# s = p.getUpdateStmt()
# s = p.getDeleteStmt()
