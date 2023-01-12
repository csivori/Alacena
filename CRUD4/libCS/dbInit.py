from flask import render_template, request
from pymysql import Connection, OperationalError

from libCS.utils import mostrarInfoXConsola

class CS_DB_Initialization():
  """El objeto CS_DB_Initialization implementa una serie de métodos para facilitar la instalación de la aplicación en un nuevo server Web y de Base de Datos. Habitualmente se dificulta la definición de la cadena de conexión con la DB, para lo cual implementa un endpoint /testDB que lograrlo.
  
  Adicionalmente permitiría correr un script para inicializar la DB. El objetivo es ir haciéndolo crecer a medida que aparecen situaciones que haya que salvar y/o mejorar.
  """

  def __init__(self, appFlask, mysql):
    self.appFlask = appFlask
    self.dbMySQL = mysql
    self.appFlask.add_url_rule(f"/testDB", "TestDB", self.iniciarTestDB)
    self.appFlask.add_url_rule(f"/testDB/resultado", "TestDB_resultados", self.testearDB, methods=['POST'])
    self.appFlask.add_url_rule(f"/testDB/ejecucion", "TestDB_ejecucion", self.ejecutarDB)
    self.appFlask.add_url_rule(f"/testDB/ejecucion2", "TestDB_ejecucion2", self.ejecutarDB2, methods=['POST'])

  def iniciarTestDB(self):
    return render_template('comunes/testDB.html')

  def ejecutarDB(self):
    return render_template('comunes/initDB.html')

  def ejecutarDB2(self):
    mostrarInfoXConsola(self.dbMySQL.getCurrentConnectionString(), "dbInit.py", "ejecutarDB2")
    dbQuery=request.form['queryAEjecutar']
    mostrarInfoXConsola(f"Query a ejecutar {dbQuery=}", "dbInit.py", "ejecutarDB2")
    mostrarInfoXConsola(f"Connexion string: "+ self.dbMySQL.getCurrentConnectionString(), "dbInit.py", "ejecutarDB2")
    resultado = self.dbMySQL.ejecutarUnitario(dbQuery, None)
    err = self.dbMySQL.getUltimaExcepcion()
    mostrarInfoXConsola(f"Resultado del Query ejecutado {resultado=}", "dbInit.py", "ejecutarDB2")
    context = {}
    context["detalle5"] = self.dbMySQL.getCurrentConnectionString()
    context["ejecucion"] = resultado
    context["detalle6"] = f"Ultimo Error: {err[0]} ({err[1]}) {err[2]}"
    return render_template("comunes/initDB.html", **context)

  def testearDB(self):
    host=request.form['host']
    usuario=request.form['user']
    contrasena=request.form['pwd']
    port=int(request.form['port'])
    db=request.form['db']
    context = {}
    if self.dbMySQL.instanciarMySQL(host=host, usr=usuario, pwd=contrasena, port=port, db=db):
      context["resultado"] = "success"
      context["titulo"] = "OK"
      context["detalle1"] = ""
      context["detalle2"] = ""
      context["detalle3"] = ""
      context["detalle4"] = ""
    else:
      err = self.dbMySQL.getUltimaExcepcion()
      context["resultado"] = "danger"
      context["titulo"] = "ERROR"
      context["detalle1"] = f"Connection String usado: {host=}/{usuario=}/{contrasena=}/{port=}/{db=}"
      context["detalle2"] = f"Ultimo Error: {err[0]} ({err[1]}) {err[2]}"
      context["detalle3"] = f""
      context["detalle4"] = f""
    return render_template("comunes/testDB.html", **context)