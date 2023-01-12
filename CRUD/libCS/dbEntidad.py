from libCS.db import CS_MySQL
from libCS.utils import mostrarInfoXConsola

class CS_CRUD_Entidad():
  def __init__(self, objDB: CS_MySQL, entidad, esEL, stmtSEL_ALL, stmtSEL_ONE, stmtINS, stmtUPD, stmtDEL) -> None:
    self.objDB = objDB
    self.entidad = entidad
    self.esEL = esEL
    self.stmtINS = stmtINS
    self.stmtUPD = stmtUPD
    self.stmtDEL = stmtDEL
    self.stmtSEL_ALL = stmtSEL_ALL
    self.stmtSEL_ONE = stmtSEL_ONE

  def obtenerTodos(self):
    return self.objDB.obtenerTodos(self.stmtSEL_ALL)

  def obtenerUno(self, datos):
    return self.objDB.obtenerUno(self.stmtSEL_ONE, datos)

  def crear(self, datos, posDescripcion)->bool:
    if self.objDB.ejecutar(self.stmtINS, datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} {datos[posDescripcion]} se ha Creado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Crear {self.strEntidad()} {datos[posDescripcion]}")
      return False

  def modificar(self, datos, posDescripcion)->bool:
    if self.objDB.ejecutar(self.stmtUPD, datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} {datos[posDescripcion]} se ha Modificado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Modificar {self.strEntidad()} {datos[posDescripcion]}")
      return False

  def borrar(self, datos)->bool:
    if self.objDB.ejecutar(self.stmtDEL, datos):
      mostrarInfoXConsola(f"{self.strEntidad().capitalize()} con clave {datos} se ha Borrado EXITOSAMENTE!")
      return True
    else:
      mostrarInfoXConsola(f"No se pudo Borrar {self.strEntidad()} con clave {datos}")
      return False

######################
# Funciones Privadas #
######################

  def strEntidad(self)->str:
    if self.esEL:
      return "el " + self.entidad
    else:
      return "la " + self.entidad
