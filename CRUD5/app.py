from flask import Flask
from flask import render_template
import libCS
from libCS.db import CS_MySQL
from libCS.dbEntidad import CS_DB_CRUD_Entidad2_FK
from libCS.dbInit import CS_DB_Initialization
from libCS.webEntidad import CS_WEB_CRUD_Entidad

#Creo la app Flask
app = Flask(__name__)

#Creo la conexión a la DB
mysql = CS_MySQL(appFlask=app, host='localhost', usr='root', pwd='', port=3306, db='crud_python_tf')
test = CS_DB_Initialization(appFlask=app, mysql=mysql)

# Prod_pres
prod_pres = CS_WEB_CRUD_Entidad(
        appFlask=app, objDB=mysql, entidad="Prod_pres", esEL=False, tabla="prod_pres", PKs="id",
        columnas="descripcion", orderBy="descripcion", retornos=["/"])

#Creo los Objetos de la aplicación
# Unidades
u = CS_WEB_CRUD_Entidad(
        appFlask=app, objDB=mysql, entidad="Unidad", esEL=False, tabla="unidades", PKs="id",
        columnas=("descripcion", "abreviatura"), orderBy="descripcion", retornos=["/", "/Unidad/listar"])
# Presentaciones
pres = CS_WEB_CRUD_Entidad(
        appFlask=app, objDB=mysql, entidad="Presentacion", esEL=False, tabla="presentaciones", PKs="id",
        columnas=("descripcion"), orderBy="descripcion", retornos=["/", "/Presentacion/listar"])
# Grupos
g = CS_WEB_CRUD_Entidad(
        appFlask=app, objDB=mysql, entidad="Grupo", esEL=True, tabla="grupos", PKs="id",
        columnas="descripcion", orderBy="descripcion", retornos=["/", "/Grupo/listar"])
# Productos
prod = CS_WEB_CRUD_Entidad(
        appFlask=app, objDB=mysql, entidad="Producto", esEL=True, tabla="productos", PKs="id",
        columnas=("descripcion", "fotoBase64", "stock_min"), orderBy="productos.descripcion",
        whereBuscar="productos.descripcion like %s",
        objFKs=(CS_DB_CRUD_Entidad2_FK(
                    tabla="productos", colFK="id_grupo", tablaFK="grupos", descripcionFK="descripcion",
                    whereJoinFK="productos.id_grupo = grupos.id", objFK=g),
                CS_DB_CRUD_Entidad2_FK(
                    tabla="productos", colFK="id_unidad", tablaFK="unidades", descripcionFK="abreviatura",
                    whereJoinFK="productos.id_unidad = unidades.id", objFK=u)
               ), retornos=["/", "/Producto/listar"])
# Envases
e = CS_WEB_CRUD_Entidad(
        appFlask=app, objDB=mysql, entidad="Envase", esEL=True, tabla="envases", PKs="id",
        columnas="cantidad", orderBy="productos.descripcion, presentaciones.descripcion",
        objFKs=(CS_DB_CRUD_Entidad2_FK(
                    tabla="envases", colFK="id_producto", tablaFK="productos", descripcionFK="descripcion",
                    whereJoinFK="envases.id_producto = productos.id", objFK=prod),
                CS_DB_CRUD_Entidad2_FK(
                    tabla="envases", colFK="id_presentacion", tablaFK="presentaciones", descripcionFK="descripcion",
                    whereJoinFK="envases.id_presentacion = presentaciones.id", objFK=pres)), 
                    retornos=["/", "/Envase/listar"])
# Stock
t = CS_WEB_CRUD_Entidad(
        appFlask=app, objDB=mysql, entidad="Stock", esEL=True, tabla="stock", PKs="id",
        columnas=("fecha_vencimiento", "fecha_compra", "fecha_uso"),
        orderBy="fecha_vencimiento, prod_pres.descripcion",
        objFKs=CS_DB_CRUD_Entidad2_FK(
                    tabla="stock", colFK="id_envase", tablaFK="prod_pres", descripcionFK="descripcion",
                    whereJoinFK="stock.id_envase = prod_pres.id", objFK=prod_pres),
        retornos=["/", "/Stock/listar"])

@app.route('/')
def login():
  return render_template('index.html', accesoATablas="hidden") 

@app.route('/Stock/listarXVencer')
def listarTenenciaXVencer():
  return t.accionBuscarEspecial(datos="", condicionWhere="", newOrderBy="fecha_vencimiento, id_producto")

@app.route('/Stock/listarXProducto/<int:idProducto>')
def listarTenenciaXProducto(idProducto):
  return t.accionBuscarEspecial(datos=str(idProducto), condicionWhere="stock.id_producto = %s")

@app.route('/Stock/listarXEnvase/<int:idEnvase>')
def listarTenenciaXEnvase(idEnvase):
  return t.accionBuscarEspecial(datos=str(idEnvase), condicionWhere="stock.id_envase = %s")

@app.route('/Envase/listarXProducto/<int:idProducto>')
def listarEnvaseXProducto(idProducto):
  return e.accionBuscarEspecial(datos=str(idProducto), condicionWhere="envases.id_producto = %s")

@app.route('/Producto/listarXGrupo/<int:idGrupo>')
def listarProductosXGrupo(idGrupo):
  return p.accionBuscarEspecial(datos=str(idGrupo), condicionWhere="productos.id_grupo = %s")

if __name__ == '__main__':
  app.run(debug=True, host='localhost', port=5000)
  # app.run(debug=False, host='localhost', port=5000)
