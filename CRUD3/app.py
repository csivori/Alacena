from flask import Flask
from flask import render_template
import libCS
from libCS.db import CS_MySQL
from libCS.dbEntidad2 import CS_CRUD_Entidad2

#Creo la app Flask
app = Flask(__name__)

#Creo la conexión a la DB
mysql = CS_MySQL(app, 'localhost', 'root', '', 3306, 'crud_python')

#Creo los Objetos de la aplicación
g = CS_CRUD_Entidad2(appFlask=app, objDB=mysql, entidad="Grupo", esEL=True,
                     tabla="grupos", PKs="id", columnas="descripcion", orderBy="descripcion", retornos=["/", "/Grupo/listar"])

p = CS_CRUD_Entidad2(appFlask=app, objDB=mysql, entidad="Producto", esEL=True,
                     tabla="productos", PKs="id",
                     columnas=("descripcion", "stock", "fotoBase64"),
                     orderBy="productos.descripcion",
                     whereBuscar="productos.descripcion like %s",
                     FKs="id_grupo", FKsDescripcion="descripcion", 
                     FKsTabla="grupos",
                     FKsWhereJoin="grupos.id = productos.id_grupo",
                     FKsObj=g, retornos=["/", "/Producto/listar"])

t = CS_CRUD_Entidad2(appFlask=app, objDB=mysql, entidad="Tenencia", esEL=True,
                     tabla="tenencia", PKs="id",
                     columnas=("fecha_vencimiento", "fecha_compra", "fecha_uso"),
                     orderBy="id_producto, fecha_vencimiento",
                     FKs="id_producto", FKsDescripcion="descripcion", 
                     FKsTabla="productos",
                     FKsWhereJoin="tenencia.id_producto = productos.id",
                     FKsObj=p, retornos=["/", "/Tenencia/listar"])

@app.route('/')
def login():
  return render_template('index.html', accesoATablas="hidden") 
  
@app.route('/Tenencia/listarXVencer')
def listarTenenciaXVencer():
  t.setOrderBy("fecha_vencimiento, id_producto")
  return t.accionListar()

@app.route('/Tenencia/listarXProducto/<int:idProducto>')
def listarTenenciaXProducto(idProducto):
  return t.accionBuscarEspecial("tenencia.id_producto = %s", str(idProducto))

@app.route('/Producto/listarXGrupo/<int:idGrupo>')
def listarProductosXGrupo(idGrupo):
  return p.accionBuscarEspecial("productos.id_grupo = %s", str(idGrupo))

if __name__ == '__main__':
  app.run(debug=True)