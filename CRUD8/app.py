from flask import Flask, request
from flask import render_template
import libCS
from libCS.utils import mostrarInfoXConsola
from libCS.db import CS_MySQL
from libCS.dbEntidad import CS_DB_CRUD_Entidad2_FK
from libCS.dbInit import CS_DB_Initialization
from libCS.webEntidad import CS_WEB_CRUD_Entidad

#Creo la app Flask
app = Flask(__name__)

#Creo la conexión a la DB
# mysql = CS_MySQL(appFlask=app, host='localhost', usr='root', pwd='', port=3306, db='crud_python_tf')
mysql = CS_MySQL(appFlask=app, host='sql10.freemysqlhosting.net', usr='sql10588086', pwd='3tQCvx6VMZ', port=3306, db='sql10588086')
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
        columnas=("descripcion", "fotoBase64", "stock_min"), columnasSelect="(SELECT IFNULL(SUM(cantidad_total), 0) FROM prod_pres WHERE prod_pres.id_producto = productos.id)", 
        orderBy="productos.descripcion", whereBuscar="productos.descripcion like %s",
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
        columnas="cantidad", columnasSelect="(SELECT abreviatura FROM unidades WHERE unidades.id = productos.id_unidad)", orderBy="productos.descripcion, envases.cantidad desc",
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
        orderBy="prod_pres.descripcion, fecha_vencimiento",
        whereBuscar="prod_pres.descripcion like %s",
        objFKs=CS_DB_CRUD_Entidad2_FK(
                    tabla="stock", colFK="id_envase", tablaFK="prod_pres", descripcionFK="descripcion",
                    whereJoinFK="stock.id_envase = prod_pres.id", objFK=prod_pres),
        retornos=["/", "/Stock/listar"])

@app.route('/')
def login():
  return render_template('index.html', accesoATablas="hidden") 

@app.route('/Producto/listarXGrupo/<int:idGrupo>')
def listarProductosXGrupo(idGrupo):
  return prod.accionBuscarEspecial(datos=str(idGrupo), condicionWhere="productos.id_grupo = %s")

@app.route('/Envase/listarXProducto/<int:idProducto>')
def listarEnvaseXProducto(idProducto):
  context = {}
  context["tituloEspecial"] = "del Producto: " + str(idProducto)
  context["productoEspecial"] = idProducto
  return e.accionBuscarEspecial(datos=str(idProducto), 
            condicionWhere="envases.id_producto = %s",
            contextoEspecial=context)

@app.route('/Stock/consumirStock')
def listarStockAConsumir():
  context = {}
  context["tituloEspecial"] = "a Consumir"
  context["retornarAEspecial"] = "/Stock/consumirStock"
  context["noMostarFechaUso"] = True
  return t.accionBuscarEspecial(
            datos="", condicionWhere="(stock.fecha_uso is NULL OR stock.fecha_uso = '0000-00-00')", 
            newOrderBy="prod_pres.descripcion, fecha_vencimiento asc",
            contextoEspecial=context)

@app.route('/Producto/consumir')
def consumirProductos():
  mostrarInfoXConsola("****** Entró en Acción Consumir Productos!!!")
  context = {}
  context["tituloEspecial"] = "a Consumir"
  context["retornarAEspecial"] = "/Producto/consumir"
  return prod.accionBuscarEspecial(datos=None, condicionWhere="", newOrderBy="",
            contextoEspecial=context, newTemplateHTML="principal.html")

@app.route('/Producto/consumir/<int:idProducto>')
def consumirXProducto(idProducto):
  mostrarInfoXConsola("****** Entró en Acción Consumir X Producto!!!")
  context = {}
  context["tituloEspecial"] = "a Consumir"
  context["retornarAEspecial"] = "/Producto/consumir/" + str(idProducto)
  context["noMostarFechaUso"] = True
  return t.accionBuscarEspecial(
            datos=str(idProducto), condicionWhere="(stock.fecha_uso is NULL OR stock.fecha_uso = '0000-00-00') AND prod_pres.id_producto = %s", 
            newOrderBy="prod_pres.descripcion, fecha_vencimiento asc",
            contextoEspecial=context)

@app.route('/Stock/consumir/<int:idStock>')
def consumirStock(idStock):
  mostrarInfoXConsola("****** Entró en Acción Consumir !!!")
  stmt = "UPDATE stock SET fecha_uso=NOW() WHERE id=%s"
  retornarAEspecial = request.args.get('retornarA')
  mostrarInfoXConsola(f"{retornarAEspecial=}")
  if t.ejecutarUnitario(idStock, "seleccionado", stmt, "Consumido"):
    mostrarInfoXConsola("****** Consumido EXITOSAMENTE")
  else:
    return t.render_templateErrorDB("modificar")
  if retornarAEspecial != "":
    return t.retornarA(retornarAEspecial)
  else:
    return t.retornarA("modificar")

@app.route('/Stock/duplicar/<int:idStock>')
def duplicarStock(idStock):
  mostrarInfoXConsola("****** Entró en Acción Duplicar !!!")
  stmt = "INSERT INTO stock (id, id_envase, fecha_vencimiento, fecha_compra, fecha_uso) SELECT NULL, id_envase, fecha_vencimiento, fecha_compra, NULL FROM stock WHERE id=%s"
  retornarAEspecial = request.args.get('retornarA')
  if t.ejecutarUnitario(idStock, "seleccionado", stmt, "Duplicado"):
    mostrarInfoXConsola("****** Duplicado EXITOSAMENTE")
  else:
    return t.render_templateErrorDB("crear")
  if retornarAEspecial != "":
    return t.retornarA(retornarAEspecial)
  else:
    return t.retornarA("crear")

@app.route('/Stock/listarXVencer')
def listarStockXVencer():
  context = {}
  context["tituloEspecial"] = "a Vencer"
  context["retornarAEspecial"] = "/Stock/listarXVencer"
  context["noMostarFechaUso"] = True
  return t.accionBuscarEspecial(
            datos="", condicionWhere="(stock.fecha_uso is NULL OR stock.fecha_uso = '0000-00-00')", 
            newOrderBy="fecha_vencimiento, id_producto",
            contextoEspecial=context)

@app.route('/Stock/listarConsumido')
def listarStockConsumido():
  context = {}
  context["tituloEspecial"] = "Consumidos"
  context["retornarAEspecial"] = "/Stock/listarConsumido"
  return t.accionBuscarEspecial(datos="", 
            condicionWhere="stock.fecha_uso is not NULL AND stock.fecha_uso <> '0000-00-00'",
            newOrderBy="fecha_uso, id_producto",
            contextoEspecial=context)

@app.route('/Stock/listarXProducto/<int:idProducto>')
def listarStockXProducto(idProducto):
  context = {}
  context["tituloEspecial"] = "del Producto: " + str(idProducto)
  context["productoEspecial"] = idProducto
  context["retornarAEspecial"] = "/Stock/listarXProducto/" + str(idProducto)
  return t.accionBuscarEspecial(datos=str(idProducto), 
            condicionWhere="prod_pres.id_producto = %s",
            contextoEspecial=context)

@app.route('/Stock/listarXEnvase/<int:idEnvase>')
def listarStockXEnvase(idEnvase):
  context = {}
  context["tituloEspecial"] = "del Envase: " + str(idEnvase)
  context["envaseEspecial"] = idEnvase
  context["retornarAEspecial"] = "/Stock/listarXEnvase/" + str(idEnvase)
  return t.accionBuscarEspecial(datos=str(idEnvase), 
            condicionWhere="prod_pres.id = %s",
            contextoEspecial=context)

# @app.template_filter('strftime')
# def _filter_datetime(date, fmt=None):
#     mostrarInfoXConsola(f"\n\n************************ strftime {date=}\n\n")
#     date = dateutil.parser.parse(date)
#     native = date.replace(tzinfo=None)
#     if not ftm:
#         ftm='%Y-%m-%d'
#     return native.strftime(ftm)

if __name__ == '__main__':
  app.run(debug=True, host='localhost', port=5000)
  # app.run(debug=False, host='localhost', port=5000)
