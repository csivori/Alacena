from flask import Flask
from flask import render_template
import libCS
from libCS.db import CS_MySQL
from libCS.dbInit import CS_DB_Initialization
from libCS.webEntidad import CS_WEB_CRUD_Entidad

#Creo la app Flask
app = Flask(__name__)

#Creo la conexión a la DB
mysql = CS_MySQL(appFlask=app, host='localhost', usr='root', pwd='Mardel&&4796', port=3306, db='sistema22516')
test = CS_DB_Initialization(appFlask=app, mysql=mysql)

#Creo los Objetos de la aplicación
u = CS_WEB_CRUD_Entidad(appFlask=app, objDB=mysql, entidad="Unidad", esEL=False,
                        tabla="unidades", PKs="id", columnas=("descripcion", "abreviatura"), orderBy="descripcion", retornos=["/", "/Unidad/listar"])

g = CS_WEB_CRUD_Entidad(appFlask=app, objDB=mysql, entidad="Grupo", esEL=True,
                        tabla="grupos", PKs="id", columnas="descripcion", orderBy="descripcion", retornos=["/", "/Grupo/listar"])

p = CS_WEB_CRUD_Entidad(appFlask=app, objDB=mysql, entidad="Producto", esEL=True,
                        tabla="productos", PKs="id",
                        columnas=("descripcion", "unidad", "fotoBase64"),
                        orderBy="productos.descripcion",
                        whereBuscar="productos.descripcion like %s",
                        FKs="id_grupo", FKsDescripcion="descripcion", FKsTabla="grupos",
                        FKsWhereJoin="productos.id_grupo = grupos.id",
                        FKsObj=g, retornos=["/", "/Producto/listar"])

e = CS_WEB_CRUD_Entidad(appFlask=app, objDB=mysql, entidad="Envase", esEL=True,
                        tabla="envases", PKs="id",
                        columnas="presentacion",
                        orderBy="presentacion",
                        FKs="id_producto", FKsDescripcion="descripcion", FKsTabla="productos",
                        FKsWhereJoin="envases.id_producto = productos.id",
                        FKsObj=p, retornos=["/", "/Envase/listar"])

t = CS_WEB_CRUD_Entidad(appFlask=app, objDB=mysql, entidad="Stock", esEL=True,
                        tabla="stock", PKs="id",
                        columnas=("fecha_vencimiento", "fecha_compra", "fecha_uso"),
                        orderBy="id_envase, fecha_vencimiento",
                        FKs="id_envase", FKsDescripcion="presentacion", FKsTabla="envases",
                        FKsWhereJoin="stock.id_envase = envases.id",
                        FKsObj=p, retornos=["/", "/Stock/listar"])

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
