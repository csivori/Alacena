from datetime import date, timedelta
from flask import Flask, redirect, render_template, request
from libCS.db import CS_MySQL
from libCS.dbEntidad import CS_DB_CRUD_Entidad2, CS_DB_CRUD_Entidad2_FK
from libCS.utils import mostrarErrorXConsola, mostrarInfoXConsola
# from db import CS_MySQL
# from dbEntidad import CS_DB_CRUD_Entidad2, CS_DB_CRUD_Entidad2_FK
# from utils import mostrarErrorXConsola, mostrarInfoXConsola

class CS_WEB_CRUD_Entidad():
  """El objeto CS_WEB_CRUD_Entidad implementa una serie de métodos para facilitar la construcción de un CRUD Básico. Soporta automáticamente las siguientes operaciones:
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

  def __init__(self, appFlask: Flask, objDB: CS_MySQL, entidad,
               esEL, tabla, PKs, columnas, columnasSelect="", orderBy="",
               whereBuscar="", objFKs=None, retornos="/") -> None:
    self.appFlask = appFlask
    self.objDB_CRUD = CS_DB_CRUD_Entidad2(objDB=objDB, entidad=entidad, esEL=esEL, tabla=tabla,
                            PKs=PKs, columnas=columnas, columnasSelect=columnasSelect,
                            orderBy=orderBy, whereBuscar=whereBuscar, objFKs=objFKs)
    self.hayWhereBuscar = (whereBuscar != "")
    self.hayFKs = (objFKs != None)
    self.retornos = []
    if isinstance(retornos, str):
      self.retornos.append(retornos)
      self.retornos.append(retornos)
      self.retornos.append(retornos)
      self.retornos.append(retornos)
    elif retornos.__len__() == 1:
      self.retornos.append(retornos[0])
      self.retornos.append(retornos[0])
      self.retornos.append(retornos[0])
      self.retornos.append(retornos[0])
    elif retornos.__len__() == 2:
      self.retornos.append(retornos[0])
      self.retornos.append(retornos[1])
      self.retornos.append(retornos[1])
      self.retornos.append(retornos[1])
    elif retornos.__len__() == 3:
      self.retornos.append(retornos[0])
      self.retornos.append(retornos[1])
      self.retornos.append(retornos[2])
      self.retornos.append(retornos[2])
    else:
      self.retornos.append(retornos[0])
      self.retornos.append(retornos[1])
      self.retornos.append(retornos[2])
      self.retornos.append(retornos[3])
    self.agregarEndpoints()

  def obtenerTodos(self):
    return self.objDB_CRUD.obtenerTodos()

  def obtenerAlgunosBuscar(self, datos, condicionWhere=""):
    return self.objDB_CRUD.obtenerAlgunosBuscar(datos, condicionWhere)

  def obtenerUno(self, datos):
    return self.objDB_CRUD.obtenerUno(datos)

  def ejecutarUnitario(self, datos, descripcion, stmt, accionEnParticipioPasado)->bool:
    return self.objDB_CRUD.ejecutarUnitario(datos, descripcion, stmt, accionEnParticipioPasado)

  def crear(self, datos, descripcion)->bool:
    return self.objDB_CRUD.crear(datos, descripcion)

  def modificar(self, datos, descripcion)->bool:
    return self.objDB_CRUD.modificar(datos, descripcion)

  def borrar(self, datos)->bool:
    return self.objDB_CRUD.borrar(datos)

############################################
# MANEJO DE ENDPOINTS Y TRANSACCIONES CRUD #
############################################

  def agregarEndpoints(self):
    ruta = self.objDB_CRUD.getEntidad()
    self.appFlask.add_url_rule(f"/{ruta}/listar", ruta+"_Listar", self.accionListar)
    self.appFlask.add_url_rule(f"/{ruta}/crear", ruta+"_Crear", self.accionCrear2, methods=['POST'])
    self.appFlask.add_url_rule(f"/{ruta}/modificar/<int:id>", ruta+"_Modificar", self.accionModificar)
    self.appFlask.add_url_rule(f"/{ruta}/modificar2/<int:id>", ruta+"_Modificar2", self.accionModificar2, methods=['POST'])
    self.appFlask.add_url_rule(f"/{ruta}/borrar/<int:id>", ruta+"_Borrar", self.accionBorrar)
    self.appFlask.add_url_rule(f"/{ruta}/borrar2/<int:id>", ruta+"_Borrar2", self.accionBorrar2, methods=['POST'])
    if self.hayWhereBuscar:
      self.appFlask.add_url_rule(f"/{ruta}/buscar", ruta+"_Buscar", self.accionBuscar, methods=['POST'])
    
  def accionListar(self)->str:
    mostrarInfoXConsola("****** Entró en Acción Listar !!!")
    context = self.setContextForSelect()
    if context == None:
      return self.render_templateErrorDB("listar")
    return render_template(f'{self.objDB_CRUD.getEntidad()}/listado.html', **context) 
  
  def accionBuscar(self)->str:
    mostrarInfoXConsola("****** Entró en Acción Buscar !!!")
    campoForm = 'buscar' + self.objDB_CRUD.getEntidad()
    datoABuscar = request.form[campoForm]
    if datoABuscar != "":
      if datoABuscar[0] != "%":
        datoABuscar = "%" + datoABuscar
      if datoABuscar[-1] != "%":
        datoABuscar = datoABuscar + "%"

    context = self.setContextForSelect(datos=datoABuscar, condicionWhere=self.objDB_CRUD.getWhereBuscar())
    if context == None:
      return self.render_templateErrorDB("listar")
    return render_template(f'{self.objDB_CRUD.getEntidad()}/listado.html', **context) 

  def accionBuscarEspecial(self, datos, condicionWhere, newOrderBy="", contextoEspecial=None, newTemplateHTML="")->str:
    mostrarInfoXConsola("****** Entró en Acción Buscar Especial !!!")
    context = self.setContextForSelect(datos, condicionWhere, newOrderBy)
    if context == None:
      return self.render_templateErrorDB("listar")
    if contextoEspecial != None and isinstance(contextoEspecial, dict):
      context.update(contextoEspecial)
    if newTemplateHTML == "":
      return render_template(f'{self.objDB_CRUD.getEntidad()}/listado.html', **context) 
    else:
      return render_template(f'{self.objDB_CRUD.getEntidad()}/{newTemplateHTML}', **context) 

  def accionCrear2(self)->str:
    mostrarInfoXConsola("****** Entró en Acción Crear !!!")
    datos = self.requestToDatos(request)
    if self.crear(datos, datos[0]):
      mostrarInfoXConsola(f"Creó EXITOSAMENTE {self.objDB_CRUD.strEntidad()}")
    else:
      return self.render_templateErrorDB("crear")
    return self.retornarA("crear")

  def accionModificar(self, id: str)->str:
    mostrarInfoXConsola(f"****** Entró en Acción Modificar {self.objDB_CRUD.strEntidad()} id:{id} !!!")
    context = self.setContextForUpdate(id)
    if context == None:
      return self.render_templateErrorDB("modificar")
    return render_template(f'{self.objDB_CRUD.getEntidad()}/modificar.html', **context)

  def accionModificar2(self, id)->str:
    mostrarInfoXConsola(f"****** Entró en Acción Modificar2 con {id=}!!!")
    datos = self.requestToDatos(request, id)
    if self.modificar(datos, datos[1]):
      mostrarInfoXConsola("****** Modificó EXITOSAMENTE")
    else:
      if self.getLastErrorMsg()[2].strip() != "OK:[0]":
        return self.render_templateErrorDB("modificar")
      mostrarInfoXConsola("****** No Modificó Nada")
    return self.retornarA("modificar")

  def accionBorrar(self, id)->str:
    mostrarInfoXConsola(f"****** Entró en Acción Borrar con {id=}!!!")
    context = self.setContextForDelete(id)
    if context == None:
      return self.render_templateErrorDB("borrar")
    return render_template(f'{self.objDB_CRUD.getEntidad()}/borrar.html', **context)

  def accionBorrar2(self, id)->str:
    mostrarInfoXConsola(f"****** Entró en Acción Borrar2 con {id=}!!!")
    if self.borrar(id):
      mostrarInfoXConsola("****** Borró EXITOSAMENTE")
    else:
      return self.render_templateErrorDB("borrar")
    return self.retornarA("borrar")

  def render_templateErrorDB(self, accion)->str:
    """Muestra la Pantalla de Errores de la Base de Datos. Consultará la última excepcion de Base de Datos ocurrida:

    :param accion: El nombre de la acción que estaba en ejecución cuando surgió el Error (listar, crear, modificar, borrar)
    """
    Accion = accion.capitalize()
    mostrarErrorXConsola("webEntidad.py", f"accion{Accion}()", f"No se pudo {Accion} {self.objDB_CRUD.strEntidad()}")
    context = self.setContextForErrorMsg(f"NO se pudo {Accion} {self.objDB_CRUD.strEntidad()}", self.getLastErrorMsg(), self.getRetornarA(accion))
    return render_template(f'comunes/error.html', **context)

  def getLastErrorMsg(self)->tuple:
    err = self.objDB_CRUD.getUltimaExcepcion()
    msgRaiz = f"{err[0]}:[{err[1]}] {err[2]}"
    if err[1] == 1045:
      msgCausa = f"Acceso a la DB Denegado para este Usuario y Contraseña ({self.objDB_CRUD.getDBUser()}/)."
      msgSolucion = f"Verifique que el Usuario y Contraseña (modulo libCS/db.py), con los que la Aplicación se conecta a la Base de Datos, tenga los permisos de acceso adecuados."
    elif err[1] == 1062:
      msgCausa = f"{self.tabla.capitalize()} no acepta duplicados y Ya existe otro registro igual en {self.tabla.capitalize()}."
      if self.esEL:
        los = "los"
      else:
        los = "las"
      msgSolucion = f"Primero revise {los} {self.objDB_CRUD.getEntidad()}s existentes ya ingresados."
    elif err[1] == 1451:
      msgCausa = f"{self.objDB_CRUD.strEntidad()} podría estar siendo utilizado por otra entidad."
      msgSolucion = f"Primero intente identificando la Entidad que lo está utilizando. Luego modifíquela o bórrela, para reintentar esta operación."
    elif (err[1] == 2003 or err[1] == 2013):
      msgCausa = f"No se puede conectar con el Servidor de Base de Datos."
      msgSolucion = f"Verifique que este en funcionamiento el motor de MySQL o Comuníquese con SISTEMAS."
    else:
      msgCausa = "No identificada."
      msgSolucion = "Comuníquese con SISTEMAS."
    return (msgCausa, msgSolucion, msgRaiz)

#######################
#  SETEO de CONTEXTOS #
#######################

  def setContextForErrorMsg(self, titulo, mensaje, proximoPaso)->dict:
    return self.setContextForMsg("danger", titulo, mensaje, proximoPaso)

  def setContextForInfoMsg(self, titulo, mensaje, proximoPaso)->dict:
    return self.setContextForMsg("success", titulo, mensaje, proximoPaso)

  def setContextForMsg(self, tipo, titulo, mensaje, proximoPaso)->dict:
    context = self.getContextBase()
    context["alertaTipo"] = tipo
    context["alertaTitulo"] = titulo
    context["alertaMsgCausa"] = mensaje[0]
    context["alertaMsgSolucion"] = mensaje[1]
    context["alertaMsgRaiz"] = mensaje[2]
    context["alertaProximoPaso"] = proximoPaso
    return context

  def setContextForSelect(self, datos="", condicionWhere="", newOrderBy="")->dict:
    sonTodos = ""
    if datos == "":
      if newOrderBy == "":
        listado = self.objDB_CRUD.obtenerTodos()
      else:
        listado = self.objDB_CRUD.obtenerAlgunosBuscar(datos, condicionWhere, newOrderBy)
      sonTodos = "Se listan "
      if self.objDB_CRUD.getEsEl():
        sonTodos += "todos los "
      else:
        sonTodos += "todas las "
      sonTodos += self.objDB_CRUD.getTabla("").capitalize() + " existentes en la base de datos"
    else:
      listado = self.objDB_CRUD.obtenerAlgunosBuscar(datos, condicionWhere, newOrderBy)
      sonTodos = "Se listan "
      if self.objDB_CRUD.getEsEl():
        sonTodos += "los "
      else:
        sonTodos += "las "
      sonTodos += self.objDB_CRUD.getTabla("").capitalize() + " que cumplen con el filtro especificado"

    if listado == None:
      return None

    context = self.getContextBase()
    context["entidad"] = self.objDB_CRUD.getEntidad()
    context["lista"] = listado
    context["listaVacia"] = (len(listado) == 0)
    context["todasLasEntidadesExistentes"] = sonTodos
    context["retornarA"] = self.retornarA("listar")
  # Si hay FKs cargo Codigo/Descripción
    if self.hayFKs:
      context = self.setContextForFKs(context)
    return context

  def setContextForUpdate(self, id)->dict:
    context = self.getContextBase()
    context["entidad"] = self.objDB_CRUD.getEntidad()
    context["itemAEditar"] = self.obtenerUno(id)
    context["retornarA"] = self.getRetornarA("modificar")
  # Si hay FKs cargo Codigo/Descripción
    if self.hayFKs:
      context = self.setContextForFKs(context)
    return context

  def setContextForDelete(self, id)->dict:
    context = self.getContextBase()
    context["entidad"] = self.objDB_CRUD.getEntidad()
    context["itemABorrar"] = self.obtenerUno(id)
    context["retornarA"] = self.getRetornarA("borrar")
    return context

  def setContextForFKs(self, context)->dict:
  # Si hay FKs cargo Codigo/Descripción
    if self.hayFKs:
      if isinstance(self.objDB_CRUD.objFKs, tuple):
        for objFK in self.objDB_CRUD.objFKs:
          k = "lista" + objFK.getTablaFK().capitalize()
          # mostrarInfoXConsola(f"setContextForFKs() Cargué la lista: {k} \n {context[k]=}")
          mostrarInfoXConsola(f"\nsetContextForFKs() Cargué la lista: {k}")
          context[k] = objFK.getObjFK().obtenerTodos()
      elif isinstance(self.objDB_CRUD.objFKs.getObjFK(), CS_WEB_CRUD_Entidad):
        k = "lista" + self.objDB_CRUD.objFKs.getTablaFK().capitalize()
        mostrarInfoXConsola(f"setContextForFKs() Cargué la lista: {k}")
        context[k] = self.objDB_CRUD.objFKs.getObjFK().obtenerTodos()
      else:
        mostrarInfoXConsola(f"setContextForFKs() self.objDB_CRUD.objFKs no es un Objeto CS_WEB_CRUD_Entidad, ni una Lista de CS_WEB_CRUD_Entidad {self.objDB_CRUD.objFKs=} {type(self.objDB_CRUD.objFKs)=}")
    return context

  def getContextBase(self)->dict:
    context = {}
    context["fechaHoy"] = date.today()
    context["fechaAyer"] = date.today() - timedelta(days=1)
    return context

  def retornarA(self, accion: str)->redirect:
    return redirect(self.getRetornarA(accion))

  def getRetornarA(self, accion: str)->str:
    if accion == "listar":
      return self.retornos[0]
    elif accion == "crear":
      return self.retornos[1]
    elif accion == "modificar":
      return self.retornos[2] 
    elif accion == "borrar":
      return self.retornos[3]
    else:
      return accion

  def requestToDatos(self, request, id=None)->tuple:
    campos = self.objDB_CRUD.getFieldsFromScreen()
    lista = []
    if isinstance(campos, str):
      lista.append(request.form[campos])
      print(f"\n\n*****************{request.form[campos]}\n\n")
    else:
      print()
      print()
      for campo in campos:
        lista.append(request.form[campo])
        print(f"*****************{request.form[campo]}")
      print()
      print()
    if id != None:
      lista.append(id)
    return tuple(lista)
