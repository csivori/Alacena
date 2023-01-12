import libCS
from libCS.dbEntidad2 import CS_CRUD_Entidad2

class Grupo():
  def __init__(self, appFlask, objDB) -> None:
    self.objEntidad = CS_CRUD_Entidad2(appFlask, objDB, "Grupo", True, \
                        "grupos", "id", "descripcion", "descripcion") 

  def obtenerTodos(self):
    return self.objEntidad.obtenerTodos()

  def obtenerUno(self, datos):
    return self.objEntidad.obtenerUno(datos)

  def crear(self, request):
    # datos = self.requestToGrupo(request)
    datos = self.objEntidad.requestToDatos(request)
    return self.objEntidad.crear(datos, 0)

  def modificar(self, id, request):
    # datos = self.requestToGrupo(request, id)
    datos = self.objEntidad.requestToDatos(request, id)
    return self.objEntidad.modificar(datos, 0)

  def borrar(self, id):
    return self.objEntidad.borrar(id)

######################
# Funciones Privadas #
######################

  # def requestToGrupo(self, request, id = None):
  #   descripcion = request.form['descripcion']
  #   if id == None:
  #     return (descripcion)
  #   else:
  #     return (descripcion, id)
