from flask import Flask, send_from_directory
from flask import render_template, request, redirect
import libCS
from libCS.db import CS_MySQL
from libCS.dbEntidad2 import CS_CRUD_Entidad2
from producto import Producto

#Creo la app Flask
app = Flask(__name__)

#Creo la conexión a la DB
mysql = CS_MySQL(app, 'localhost', 'root', '', 3306, 'crud_python')

#Creo los Objetos de la aplicación
g = CS_CRUD_Entidad2(appFlask=app, objDB=mysql, entidad="Grupo", esEL=True,
                     tabla="grupos", PKs="id", columnas="descripcion", orderBy="descripcion", retornos=["/app", "/Grupo/listar"])
p = Producto(appFlask=app, objDB=mysql)
# p = CS_CRUD_Entidad2(appFlask=app, objDB=mysql, entidad="Producto", esEL=True,
#                      tabla="productos", PKs="id",
#                      columnas=("descripcion", "stock", "foto"),
#                      orderBy="descripcion",
#                      FKs="id_grupo", FKsDescripcion="descripcion", 
#                      FKsTabla="grupos",
#                      FKsWhereJoin="grupos.id = productos.id_grupo",
#                      FKsObj=p, retornos=["/app", "/Producto/listar"])
t = CS_CRUD_Entidad2(appFlask=app, objDB=mysql, entidad="Tenencia", esEL=True,
                     tabla="tenencia", PKs="id",
                     columnas=("fecha_vencimiento", "fecha_compra", "fecha_uso"),
                     orderBy="id_producto, fecha_vencimiento",
                     FKs="id_producto", FKsDescripcion="descripcion", 
                     FKsTabla="productos",
                     FKsWhereJoin="tenencia.id_producto = productos.id",
                     FKsObj=p, retornos=["/app", "/Tenencia/listar"])

@app.route('/')
def login():
  # return render_template('index.html', empleados=listar()) # va a buscar dentro del directorio "templates"
  return render_template('index.html') 

@app.route('/Producto/buscar', methods=['POST'])
def buscar():
  listaProductos = p.buscarXNombre(request)
  context = {}
  context["lista"] = listaProductos
  context["listaGrupos"] = g.obtenerTodos()
  context["listaVacia"] = (len(listaProductos) == 0)
  context["entidad"] = "Producto"
  return render_template('Producto/listado.html', **context) 
  
@app.route('/Producto/listar')
def main():
  listaProductos = p.obtenerTodos()
  context = {}
  context["lista"] = listaProductos
  context["listaGrupos"] = g.obtenerTodos()
  context["listaVacia"] = (len(listaProductos) == 0)
  context["entidad"] = "Producto"
  return render_template('Producto/listado.html', **context) 

@app.route('/Producto/crear', methods=['POST'])
def crearProducto():
    p.crear(request)
    return retornarAPaginaPrincipal()

@app.route('/Producto/modificar/<int:id>')
def modificar(id: str):
  context = {}
  context["itemAEditar"] = p.obtenerUno(id)
  context["listaGrupos"] = g.obtenerTodos()
  context["yaTieneFoto"] = (context["itemAEditar"][5] != "")
  context["entidad"] = "Producto"
  context["retornarA"] = "/Producto/listar"
  return render_template('Producto/modificar.html', **context)

@app.route('/Producto/modificar2/<int:id>', methods=['POST'])
def modificar2(id: str):
  p.modificar(id, request)
  return retornarAPaginaPrincipal()

@app.route('/Producto/borrar/<int:id>')
def borrar(id: str):
  context = {}
  context["itemABorrar"] = p.obtenerUno(id)
  context["entidad"] = "Producto"
  context["retornarA"] = "/Producto/listar"
  return render_template('Producto/borrar.html', **context)

@app.route('/Producto/borrar2/<int:id>', methods=['POST'])
def borrar2(id: str):
    p.borrar(id)
    return retornarAPaginaPrincipal()

# ######################
# # Funciones Privadas #
# ######################

def retornarAPaginaPrincipal()->redirect:
  return redirect('/Producto/listar')

if __name__ == '__main__':
  app.run(debug=True)