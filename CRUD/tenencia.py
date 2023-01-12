import libCS
from libCS.dbEntidad2 import CS_CRUD_Entidad2

class Tenencia():
  def __init__(self, appFlask, objDB) -> None:
    self.objEntidad = CS_CRUD_Entidad2(appFlask: Flask(), objDB, "Tenencia", False, 
                          "tenencia", "id", \
                          ["id_producto", "fecha_vencimiento", \
                           "fecha_compra", "fecha_uso"], 
                          ["id_producto", "fecha_vencimiento"])
    appFlask.add_url("")

  def obtenerTodos(self):
    return self.objEntidad.obtenerTodos()

  def obtenerUno(self, datos):
    return self.objEntidad.obtenerUno(datos)

  def crear(self, request):
    datos = self.objEntidad.requestToDatos(request)
    return self.objEntidad.crear(datos, 0)

  def modificar(self, id, request):
    datos = self.objEntidad.requestToDatos(request, id)
    return self.objEntidad.modificar(datos, 0)

  def borrar(self, id):
    return self.objEntidad.borrar(id)

######################
# Funciones Privadas #
######################

  # def requestToGrupo(self, request, id = None):
  #   id_producto = request.form['id_producto']
  #   fecha_vencimiento = request.form['fecha_vencimiento']
  #   fecha_compra = request.form['fecha_compra']
  #   fecha_uso = request.form['fecha_uso']

  #   if id == None:
  #     return (id_producto, fecha_vencimiento, fecha_compra, fecha_uso)
  #   else:
  #     return (id_producto, fecha_vencimiento, fecha_compra, fecha_uso, id)
