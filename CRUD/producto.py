import libCS
from libCS.dbEntidad import CS_CRUD_Entidad

class Producto():
  DB_SEL_ALL = "SELECT p.id, p.id_grupo, g.descripcion, p.descripcion, p.stock, p.fotoBase64 " \
                "FROM productos p, grupos g " \
                "WHERE p.id_grupo = g.id " \
                "ORDER BY p.descripcion"
  DB_SEL_X_DESC = "SELECT p.id, p.id_grupo, g.descripcion, p.descripcion, p.stock, p.fotoBase64 "\
                "FROM productos p, grupos g " \
                "WHERE p.id_grupo = g.id AND p.descripcion like %s" \
                "ORDER BY p.descripcion"
  DB_SEL_ONE = "SELECT p.id, g.id, g.descripcion, p.descripcion, p.stock, p.fotoBase64 " \
                "FROM `crud_python`.`productos` p, `crud_python`.`grupos` g " \
                "WHERE p.id = %s and p.id_grupo = g.id"
  DB_INS = "INSERT INTO productos " \
            "(`id`, `id_grupo`, `descripcion`, `stock`, `fotoBase64`) " \
            "VALUES (NULL, %s, %s, %s, %s)"
  DB_UPD = "UPDATE `crud_python`.`productos` " \
            "SET id_grupo = %s, descripcion = %s, stock = %s, fotoBase64 = %s " \
            "WHERE id = %s"
  DB_DEL = "DELETE FROM `crud_python`.`productos` " \
            "WHERE id = %s"

  def __init__(self, appFlask, objDB) -> None:
    self.objEntidad = CS_CRUD_Entidad(objDB, "Producto", True, \
                                      self.DB_SEL_ALL, \
                                      self.DB_SEL_ONE, \
                                      self.DB_INS, \
                                      self.DB_UPD, \
                                      self.DB_DEL) 

  def obtenerTodos(self):
    return self.objEntidad.obtenerTodos()

  def obtenerUno(self, datos):
    return self.objEntidad.obtenerUno(datos)

  def buscarXNombre(self, request):
    productoABuscar = request.form['buscar']
    if productoABuscar[0] != "%":
      productoABuscar = "%" + productoABuscar
    if productoABuscar[-1] != "%":
      productoABuscar = productoABuscar + "%"
    return self.objEntidad.objDB.obtenerAlgunos(self.DB_SEL_X_DESC, productoABuscar)

  def crear(self, request):
    datos = self.requestToProducto(request)
    return self.objEntidad.crear(datos, 1)

  def modificar(self, id, request):
    datos = self.requestToProducto(request, id)
    return self.objEntidad.modificar(datos, 1)

  def borrar(self, id):
    return self.objEntidad.borrar(id)

######################
# Funciones Privadas #
######################

  def requestToProducto(self, request, id = None):
    id_grupo = request.form['id_grupo']
    descripcion = request.form['descripcion']
    stock = request.form['stock']
    foto = request.form['fotoBase64']
    if id == None:
      return (id_grupo, descripcion, stock, foto)
    else:
      return (id_grupo, descripcion, stock, foto, id)
