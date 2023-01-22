from flask import Flask, request
# import libCS
from libCS.db import CS_MySQL
from libCS.utils import mostrarInfoXConsola
from libCS.dbEntidad import CS_DB_CRUD_Entidad2_FK
from libCS.webEntidad import CS_WEB_CRUD_Entidad

class Gastos():
  def __init__(self, appFlask: Flask, objDB: CS_MySQL,) -> None:
    self.appFlask = appFlask
    self.objDB = objDB
    self.inicializoObjetos()

  def inicializoObjetos(self):
    #Creo los Objetos de la aplicación



    # Prod_pres
    self.prod_pres = CS_WEB_CRUD_Entidad(
        appFlask=self.appFlask, objDB=self.objDB, entidad="Prod_pres", esEL=False, tabla="prod_pres", PKs="id",
        columnas="descripcion", orderBy="descripcion", retornos=["/"])

    # Unidades
    self.u = CS_WEB_CRUD_Entidad(
            appFlask=self.appFlask, objDB=self.objDB, entidad="Unidad", esEL=False, tabla="unidades", PKs="id",
            columnas=("descripcion", "abreviatura"), orderBy="descripcion", retornos=["/", "/Unidad/listar"])
    # Presentaciones
    self.pres = CS_WEB_CRUD_Entidad(
            appFlask=self.appFlask, objDB=self.objDB, entidad="Presentacion", esEL=False, tabla="presentaciones", PKs="id",
            columnas=("descripcion"), orderBy="descripcion", retornos=["/", "/Presentacion/listar"])
    # Grupos
    self.g = CS_WEB_CRUD_Entidad(
            appFlask=self.appFlask, objDB=self.objDB, entidad="Grupo", esEL=True, tabla="grupos", PKs="id",
            columnas="descripcion", orderBy="descripcion", retornos=["/", "/Grupo/listar"])
    # Productos
    self.prod = CS_WEB_CRUD_Entidad(
            appFlask=self.appFlask, objDB=self.objDB, entidad="Producto", esEL=True, tabla="productos", PKs="id",
            columnas=("descripcion", "fotoBase64", "stock_min"), columnasSelect="(SELECT IFNULL(SUM(cantidad_total), 0) FROM prod_pres WHERE prod_pres.id_producto = productos.id)", 
            orderBy="productos.descripcion", whereBuscar="productos.descripcion like %s",
            objFKs=(CS_DB_CRUD_Entidad2_FK(
                        tabla="productos", colFK="id_grupo", tablaFK="grupos", descripcionFK="descripcion",
                        whereJoinFK="productos.id_grupo = grupos.id", objFK=self.g),
                    CS_DB_CRUD_Entidad2_FK(
                        tabla="productos", colFK="id_unidad", tablaFK="unidades", descripcionFK="abreviatura",
                        whereJoinFK="productos.id_unidad = unidades.id", objFK=self.u)
                  ), 
            retornos=["/", "/Envase/listarXProducto/0", "/Producto/listar"])
    # Envases
    self.e = CS_WEB_CRUD_Entidad(
            appFlask=self.appFlask, objDB=self.objDB, entidad="Envase", esEL=True, tabla="envases", PKs="id",
            columnas="cantidad", columnasSelect="(SELECT abreviatura FROM unidades WHERE unidades.id = productos.id_unidad)", orderBy="productos.descripcion, envases.cantidad desc",
            objFKs=(CS_DB_CRUD_Entidad2_FK(
                        tabla="envases", colFK="id_producto", tablaFK="productos", descripcionFK="descripcion",
                        whereJoinFK="envases.id_producto = productos.id", objFK=self.prod),
                    CS_DB_CRUD_Entidad2_FK(
                        tabla="envases", colFK="id_presentacion", tablaFK="presentaciones", descripcionFK="descripcion",
                        whereJoinFK="envases.id_presentacion = presentaciones.id", objFK=self.pres)), 
                        retornos=["/", "/Envase/listar"])
    # Stock
    self.t = CS_WEB_CRUD_Entidad(
            appFlask=self.appFlask, objDB=self.objDB, entidad="Stock", esEL=True, tabla="stock", PKs="id",
            columnas=("fecha_vencimiento", "fecha_compra", "fecha_uso"),
            orderBy="prod_pres.descripcion, fecha_vencimiento",
            whereBuscar="prod_pres.descripcion like %s",
            objFKs=CS_DB_CRUD_Entidad2_FK(
                        tabla="stock", colFK="id_envase", tablaFK="prod_pres", descripcionFK="descripcion",
                        whereJoinFK="stock.id_envase = prod_pres.id", objFK=self.prod_pres),
            retornos=["/", "/Stock/listar"])
    self.agregarEndpointsExtras()

  def agregarEndpointsExtras(self):
    self.appFlask.add_url_rule("/Producto/listarXGrupo/<int:idGrupo>", "Producto_ListarXGrupo", self.listarProductosXGrupo)
    self.appFlask.add_url_rule("/Envase/listarXProducto/<int:idProducto>", "Envase_ListarXProducto", self.listarEnvaseXProducto)
    self.appFlask.add_url_rule("/Stock/consumirStock", "Stock_ConsumirStock", self.listarStockAConsumir)
    self.appFlask.add_url_rule("/Producto/consumir", "Producto_Consumir", self.consumirProductos)
    self.appFlask.add_url_rule("/Producto/consumir/<int:idProducto>", "ConsumirXProducto", self.consumirXProducto)
    self.appFlask.add_url_rule("/Stock/consumir/<int:idStock>", "ConsumirStock", self.consumirStock)
    self.appFlask.add_url_rule("/Stock/duplicar/<int:idStock>", "DuplicarStock", self.duplicarStock)
    self.appFlask.add_url_rule("/Stock/listarXVencer", "Stock_ListarXVencer", self.listarStockXVencer)
    self.appFlask.add_url_rule("/Stock/listarConsumido", "Stock_ListarConsumido", self.listarStockConsumido)
    self.appFlask.add_url_rule("/Stock/listarFaltante", "Stock_ListarFaltante", self.listarStockFaltante)
    self.appFlask.add_url_rule("/Stock/listarXProducto/<int:idProducto>", "Stock_ListarXProducto", self.listarStockXProducto)
    self.appFlask.add_url_rule("/Stock/listarXEnvase/<int:idEnvase>", "Stock_ListarXEnvase", self.listarStockXEnvase)
    # self.appFlask.add_url_rule(f"/{ruta}/modificar/<int:id>", ruta+"_Modificar", self.accionModificar)
    # self.appFlask.add_url_rule(f"/{ruta}/modificar2/<int:id>", ruta+"_Modificar2", self.accionModificar2, methods=['POST'])

  def listarProductosXGrupo(self, idGrupo):
    return self.prod.accionBuscarEspecial(datos=str(idGrupo), condicionWhere="productos.id_grupo = %s")

  def listarEnvaseXProducto(self, idProducto):
    if (idProducto == 0):
      idProducto = self.prod.obtenerUltimoId()
    context = {}
    context["tituloEspecial"] = "del Producto: " + str(idProducto)
    context["productoEspecial"] = idProducto
    return self.e.accionBuscarEspecial(datos=str(idProducto), 
              condicionWhere="envases.id_producto = %s",
              contextoEspecial=context)

  def listarStockAConsumir(self):
    context = {}
    context["tituloEspecial"] = "a Consumir"
    context["retornarAEspecial"] = "/Stock/consumirStock"
    context["noMostarFechaUso"] = True
    return self.t.accionBuscarEspecial(
              datos="", condicionWhere="(stock.fecha_uso is NULL OR stock.fecha_uso = '0000-00-00')", 
              newOrderBy="prod_pres.descripcion, fecha_vencimiento asc",
              contextoEspecial=context)

  def consumirProductos(self):
    mostrarInfoXConsola(f"\n****** Entró en Acción Consumir Productos!!!")
    context = {}
    context["tituloEspecial"] = "a Consumir"
    context["retornarAEspecial"] = "/Producto/listar"
    return self.prod.accionBuscarEspecial(datos=None, newOrderBy="",
              condicionWhere="", 
              contextoEspecial=context, newTemplateHTML="principal.html")

  def consumirXProducto(self, idProducto):
    mostrarInfoXConsola(f"\n****** Entró en Acción Consumir X Producto!!!")
    context = {}
    context["tituloEspecial"] = "a Consumir"
    context["retornarAEspecial"] = "/Producto/consumir"
    context["noMostarFechaUso"] = True
    return self.t.accionBuscarEspecial(
              datos=str(idProducto), condicionWhere="(stock.fecha_uso is NULL OR stock.fecha_uso = '0000-00-00') AND prod_pres.id_producto = %s", 
              newOrderBy="prod_pres.descripcion, fecha_vencimiento asc",
              contextoEspecial=context
              , newTemplateHTML="principal.html"
              )

  def consumirStock(self, idStock):
    mostrarInfoXConsola(f"\n****** Entró en Acción Consumir !!!")
    stmt = "UPDATE stock SET fecha_uso=NOW() WHERE id=%s"
    retornarAEspecial = request.args.get('retornarA')
    mostrarInfoXConsola(f"{retornarAEspecial=}")
    if self.t.ejecutarUnitario(idStock, "seleccionado", stmt, "Consumido"):
      mostrarInfoXConsola("****** Consumido EXITOSAMENTE")
    else:
      return self.t.render_templateErrorDB("modificar")
    if retornarAEspecial != "":
      return self.t.retornarA(retornarAEspecial)
    else:
      return self.t.retornarA("modificar")

  def duplicarStock(self, idStock):
    mostrarInfoXConsola(f"\n****** Entró en Acción Duplicar !!!")
    stmt = "INSERT INTO stock (id, id_envase, fecha_vencimiento, fecha_compra, fecha_uso) SELECT NULL, id_envase, fecha_vencimiento, fecha_compra, NULL FROM stock WHERE id=%s"
    retornarAEspecial = request.args.get('retornarA')
    if self.t.ejecutarUnitario(idStock, "seleccionado", stmt, "Duplicado"):
      mostrarInfoXConsola("****** Duplicado EXITOSAMENTE")
    else:
      return self.t.render_templateErrorDB("crear")
    if retornarAEspecial != "":
      return self.t.retornarA(retornarAEspecial)
    else:
      return self.t.retornarA("crear")

  def listarStockXVencer(self):
    context = {}
    context["tituloEspecial"] = "a Vencer"
    context["retornarAEspecial"] = "/Stock/listarXVencer"
    context["noMostarFechaUso"] = True
    return self.t.accionBuscarEspecial(
              datos="", condicionWhere="(stock.fecha_uso is NULL OR stock.fecha_uso = '0000-00-00')", 
              newOrderBy="fecha_vencimiento, id_producto",
              contextoEspecial=context)

  def listarStockConsumido(self):
    context = {}
    context["tituloEspecial"] = "Consumidos"
    context["retornarAEspecial"] = "/Stock/listarConsumido"
    return self.t.accionBuscarEspecial(datos="", 
              condicionWhere="stock.fecha_uso is not NULL AND stock.fecha_uso <> '0000-00-00'",
              newOrderBy="fecha_uso, id_producto",
              contextoEspecial=context)

  def listarStockFaltante(self):
    context = {}
    context["tituloEspecial"] = "Faltantes"
    context["retornarAEspecial"] = "/Stock/listarFaltante"
    # return self.t.accionBuscarEspecial(datos="", 
    #           condicionWhere="stock.fecha_uso is not NULL AND stock.fecha_uso <> '0000-00-00'",
    #           newOrderBy="fecha_uso, id_producto",
    #           contextoEspecial=context)
    return self.t.enConstruccion(contextoEspecial=context)

  def listarStockXProducto(self, idProducto):
    context = {}
    context["tituloEspecial"] = "del Producto: " + str(idProducto)
    context["productoEspecial"] = idProducto
    context["retornarAEspecial"] = "/Stock/listarXProducto/" + str(idProducto)
    return self.t.accionBuscarEspecial(datos=str(idProducto), 
              condicionWhere="prod_pres.id_producto = %s",
              contextoEspecial=context)

  def listarStockXEnvase(self, idEnvase):
    context = {}
    context["tituloEspecial"] = "del Envase: " + str(idEnvase)
    context["envaseEspecial"] = idEnvase
    context["retornarAEspecial"] = "/Stock/listarXEnvase/" + str(idEnvase)
    return self.t.accionBuscarEspecial(datos=str(idEnvase), 
              condicionWhere="prod_pres.id = %s",
              contextoEspecial=context)

# @appFlask.template_filter('strftime')
# def _filter_datetime(date, fmt=None):
#     mostrarInfoXConsola(f"\n\n************************ strftime {date=}\n\n")
#     date = dateutil.parser.parse(date)
#     native = date.replace(tzinfo=None)
#     if not ftm:
#         ftm='%Y-%m-%d'
#     return native.strftime(ftm)
