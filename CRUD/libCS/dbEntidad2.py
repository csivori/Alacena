from flask import Flask, render_template, request, redirect
from libCS.db import CS_MySQL
from libCS.dbEntidad import CS_CRUD_Entidad
from libCS.utils import mostrarErrorXConsola, mostrarInfoXConsola, asegurarTupla, tuplaToStr, tuplaToTupla
from producto import Producto

class CS_CRUD_Entidad2():
  def __init__(self, appFlask: Flask, objDB: CS_MySQL, entidad,
               esEL, tabla, PKs, columnas, orderBy, 
               FKs="", FKsDescripcion="", FKsTabla="", FKsWhereJoin="",
               FKsObj=None, retornos="/") -> None:
    self.appFlask = appFlask
    self.objDB = objDB
    self.entidad = entidad
    self.esEL = esEL
    self.tabla = tabla
    self.PKs = PKs
    self.orderBy = orderBy
    self.FKs = FKs
    self.FKsDescripcion = FKsDescripcion
    self.FKsTabla = FKsTabla
    self.FKsWhereJoin = FKsWhereJoin
    self.FKsObj = FKsObj
    self.columnas = columnas
    self.retornos = retornos 
    self.agregarEndpoints()

  def obtenerTodos(self):
    return self.objDB.obtenerTodos(self.getSelectAllStmt())

  def obtenerUno(self, datos):
    return self.objDB.obtenerUno(self.getSelectOneStmt(), datos)

  def crear(self, datos, posDescripcion)->bool:
    if self.objDB.ejecutar(self.getInsertStmt(), datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} {datos[posDescripcion]} se ha Creado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Crear {self.strEntidad()} {datos[posDescripcion]}")
      return False

  def modificar(self, datos, posDescripcion)->bool:
    if self.objDB.ejecutar(self.getUpdateStmt(), datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} {datos[posDescripcion]} se ha Modificado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Modificar {self.strEntidad()} {datos[posDescripcion]}")
      return False

  def borrar(self, datos)->bool:
    if self.objDB.ejecutar(self.getDeleteStmt(), datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} con clave {datos} se ha Borrado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Borrar {self.strEntidad()} con clave {datos}")
      return False

  def requestToDatos(self, request, id=None)->tuple:
    lista = []
    if self.FKs != "":
      if isinstance(self.FKs, str):
        lista.append(request.form[self.FKs])
      else:
        for c in self.FKs:
          dato = request.form[c]
          lista.append(dato)
    if isinstance(self.columnas, str):
      lista.append(request.form[self.columnas])
    else:
      for c in self.columnas:
        dato = request.form[c]
        lista.append(dato)
    if id != None:
      lista.append(id)
    return tuple(lista)

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
    # return "`" + self.objDB.getDB() + "`.`" + self.tabla + "`" + posfijo





############################################
# MANEJO DE ENDPOINTS Y TRANSACCIONES CRUD #
############################################

  def agregarEndpoints(self):
    self.appFlask.add_url_rule(f"/{self.entidad}/listar", self.entidad+"_Listar", self.accionListar)
    self.appFlask.add_url_rule(f"/{self.entidad}/crear", self.entidad+"_Crear", self.accionCrear2, methods=['POST'])
    self.appFlask.add_url_rule(f"/{self.entidad}/modificar/<int:id>", self.entidad+"_Modificar", self.accionModificar)
    self.appFlask.add_url_rule(f"/{self.entidad}/modificar2/<int:id>", self.entidad+"_Modificar2", self.accionModificar2, methods=['POST'])
    self.appFlask.add_url_rule(f"/{self.entidad}/borrar/<int:id>", self.entidad+"_Borrar", self.accionBorrar)
    self.appFlask.add_url_rule(f"/{self.entidad}/borrar2/<int:id>", self.entidad+"_Borrar2", self.accionBorrar2, methods=['POST'])

  def accionListar(self):
    mostrarInfoXConsola("****** Entró en Acción Listar !!!")
    context = self.setContextForSelect()
    return render_template(f'{self.entidad}/listado.html', **context) 
  
  def accionCrear2(self):
    mostrarInfoXConsola("****** Entró en Acción Crear !!!")
    datos = self.requestToDatos(request)
    if self.crear(datos, 0):
      mostrarInfoXConsola(f"Creó EXITOSAMENTE {self.strEntidad()}")
    else:
      mostrarErrorXConsola("accionCrear2()", f"No se pudo Crear {self.strEntidad()}")
      context = self.setContextForErrorMsg(f"NO se pudo Crear {self.strEntidad()}", self.getLastErrorMsg(), self.getRetornarA("crear"))
      return render_template(f'comunes/error.html', **context)
    return self.retornarA("crear")

  def accionModificar(self, id: str):
    mostrarInfoXConsola(f"****** Entró en Acción Modificar {self.strEntidad()} id:{id} !!!")
    context = self.setContextForUpdate(id)
    return render_template(f'{self.entidad}/modificar.html', **context)

  def accionModificar2(self, id):
    mostrarInfoXConsola("****** Entró en Acción Modificar2 !!!")
    datos = self.requestToDatos(request, id)
    if self.modificar(datos, 1):
      mostrarInfoXConsola("****** Modificó EXITOSAMENTE")
    else:
      mostrarErrorXConsola("accionModificar2()", f"No se pudo Modificar {self.strEntidad()}")
      context = self.setContextForErrorMsg(f"NO se pudo Modificar {self.strEntidad()}", self.getLastErrorMsg(), self.getRetornarA("modificar"))
      return render_template(f'comunes/error.html', **context)
    return self.retornarA("modificar")

  def accionBorrar(self, id):
    mostrarInfoXConsola("****** Entró en Acción Borrar !!!")
    context = {}
    context["entidad"] = self.entidad
    context["itemABorrar"] = self.obtenerUno(id)
    context["retornarA"] = self.getRetornarA("borrar")
    return render_template(f'{self.entidad}/borrar.html', **context)

  def accionBorrar2(self, id):
    mostrarInfoXConsola("****** Entró en Acción Borrar2 !!!")
    if self.borrar(id):
      mostrarInfoXConsola("****** Borró EXITOSAMENTE")
    else:
      mostrarErrorXConsola("accionBorrar2()", f"No se pudo Borrar {self.strEntidad()}")
      context = self.setContextForErrorMsg(f"NO se pudo Borrar {self.strEntidad()}", self.getLastErrorMsg(), self.getRetornarA("borrar"))
      return render_template(f'comunes/error.html', **context)
    return self.retornarA("borrar")
    
  def getLastErrorMsg(self)->tuple:
    err = self.objDB.getUltimaExcepcion()
    msgRaiz = f"{err[0]}:[{err[1]}] {err[2]}"
    if err[1] == 1062:
      msgCausa = f"{self.tabla.capitalize()} no acepta duplicados y Ya existe otro registro igual en {self.tabla.capitalize()}."
      if self.esEL:
        los = "los"
      else:
        los = "las"
      msgSolucion = f"Primero revise {los} {self.entidad}s existentes ya ingresados."
    elif err[1] == 1451:
      msgCausa = f"{self.strEntidad()} podría estar siendo utilizado por otra entidad."
      msgSolucion = f"Primero intente identificando la Entidad que lo está utilizando. Luego modifíquela o bórrela, para reintentar esta operación."
    else:
      msgCausa = "No identificada."
      msgSolucion = "Comuníquese con SISTEMAS."
    return (msgCausa, msgSolucion, msgRaiz)

  def setContextForErrorMsg(self, titulo, mensaje, proximoPaso)->dict:
    return self.setContextForMsg("danger", titulo, mensaje, proximoPaso)

  def setContextForInfoMsg(self, titulo, mensaje, proximoPaso)->dict:
    return self.setContextForMsg("success", titulo, mensaje, proximoPaso)

  def setContextForMsg(self, tipo, titulo, mensaje, proximoPaso)->dict:
    context = {}
    context["alertaTipo"] = tipo
    context["alertaTitulo"] = titulo
    context["alertaMsgCausa"] = mensaje[0]
    context["alertaMsgSolucion"] = mensaje[1]
    context["alertaMsgRaiz"] = mensaje[2]
    context["alertaProximoPaso"] = proximoPaso
    return context

  def setContextForSelect(self)->dict:
    listado = self.obtenerTodos()
    context = {}
    context["entidad"] = self.entidad
    context["lista"] = listado
    context["listaVacia"] = (len(listado) == 0)
    context["retornarA"] = self.retornarA("listar")
  # Si hay FKs cargo Codigo/Descripción
    if self.FKsObj != None:
      context = self.setContextForFKs(context)
    return context

  def setContextForUpdate(self, id)->dict:
    context = {}
    context["entidad"] = self.entidad
    context["itemAEditar"] = self.obtenerUno(id)
    context["retornarA"] = self.getRetornarA("modificar")
  # Si hay FKs cargo Codigo/Descripción
    if self.FKsObj != None:
      context = self.setContextForFKs(context)
    return context

  def setContextForFKs(self, context)->dict:
  # Si hay FKs cargo Codigo/Descripción
    if self.FKsObj != None:
      if isinstance(self.FKsObj, list):
        k = "lista" + self.FKsTabla.capitalize()
        mostrarInfoXConsola(f"setContextForFKs() Cargué la lista: {k} \n {context[k]=}")
        context[k] = self.FKsObj.obtenerTodos()
      elif isinstance(self.FKsObj, CS_CRUD_Entidad2) or \
           isinstance(self.FKsObj, CS_CRUD_Entidad) or \
           isinstance(self.FKsObj, Producto):
        k = "lista" + self.FKsTabla.capitalize()
        mostrarInfoXConsola(f"setContextForFKs() Cargué la lista: {k}")
        context[k] = self.FKsObj.obtenerTodos()
      else:
        mostrarInfoXConsola(f"setContextForFKs() FKsObj no es un Objeto CS_CRUD_Entidad, ni una Lista de CS_CRUD_Entidad {self.FKsObj =} {type(self.FKsObj) =}")
    return context

  def retornarA(self, accion: str)->redirect:
    return redirect(self.getRetornarA(accion))

  def getRetornarA(self, accion: str)->str:
    if accion == "listar":
      return self.retornos[0]
    elif accion == "crear":
      return self.retornos[1]
    elif accion == "modificar":
      return self.retornos[1]
    elif accion == "borrar":
      return self.retornos[1]
