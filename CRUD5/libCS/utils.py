from datetime import datetime

def asegurarLista(s):
  """Asegura que el tipo es una Lista o Convierte a Lista una Tupla, Set, o String. Caso contrario mostrará un error x Consola.

  :param s: objeto que se desea convertir a Lista
  """

  if isinstance(s, str) or isinstance(s, tuple) or isinstance(s, set):
    return list(s)
  elif isinstance(s, list):
    return s
  else:
    mostrarErrorXConsola("utils.py", "asegurarLista()", f"No es un tipo convertible, ni Lista: {s=} {type(s)=}")

def asegurarTupla(s):
  """Asegura que el tipo es una Tupla o Convierte a Tupla una Lista, Set, o String. Caso contrario mostrará un error x Consola.

  :param s: objeto que se desea convertir a Tupla
  """

  if isinstance(s, str) or isinstance(s, list) or isinstance(s, set):
    return tuple(s)
  elif isinstance(s, tuple):
    return s
  else:
    mostrarErrorXConsola("utils.py", "asegurarTupla()", f"No es un tipo convertible, ni Tupla: {s=} {type(s)=}")

def tuplaToStr(tupla, prefijo, posfijo, separador, sinSeparadorAlFinal)->str:
  """Convierte una Tupla tipicamente de strings, concatenando cada item con un  separador informado. Opcionalmente puede agregar prefijos o posfijos a cada item. También puede especificar que si el último item debe o no incluir el separador.

  :param tupla: Tupla origen que se desea convertir a String
  :param prefijo: String que se desea incluir antes de cada Item
  :param posfijo: String que se desea incluir después de cada Item
  :param separador: String con el que se desea separar cada Item
  :param sinSeparadorAlFinal: Boolean indicando si debe incluir o no
  """

  if not isinstance(tupla, tuple):
    if not isinstance(tupla, str):
      mostrarErrorXConsola("utils.py", "tuplaToStr()", f"No es un tipo Tupla: {tupla=} {type(tupla)=}")
      return None
    else:
      s = prefijo + str(tupla) + posfijo + separador
  else:
    lista = list(tupla)
    if len(lista) == 1:
      s = prefijo + str(lista[0]) + posfijo + separador
    elif len(lista) > 1:
      s = ""
      for t in lista:
        s += prefijo + t + posfijo + separador

  if sinSeparadorAlFinal:
    s = s[:len(s)-len(separador)]

  return s

def tuplaToTupla(tupla, prefijo, posfijo)->tuple:
  """Permite agregar prefijos o posfijos a cada item de una Tupla, retornando la Tupla modificada.

  :param tupla: Tupla origen que se desea modificar
  :param prefijo: String que se desea incluir antes de cada Item
  :param posfijo: String que se desea incluir después de cada Item
  """
  if not isinstance(tupla, tuple):
    if not isinstance(tupla, str):
      mostrarErrorXConsola("utils.py", "tuplaToTupla()", f"No es un tipo Tupla: {tupla=} {type(tupla)=}")
      return None
    else:
      s = prefijo + tupla + posfijo
    return s
  else:
    lista = list(tupla)
    if len(lista) == 1:
      s = prefijo + str(lista[0]) + posfijo
      return s
    elif len(lista) > 1:
      s = ""
      listaNueva = []
      for t in lista:
        listaNueva.append(prefijo + t + posfijo)
      return tuple(listaNueva)

def listaToStr(lista, prefijo, posfijo, separador, sinSeparadorAlFinal)->str:
  """Convierte una Lista tipicamente de strings, concatenando cada item con un separador informado. Opcionalmente puede agregar prefijos o posfijos a cada item. También puede especificar que si el último item debe o no incluir el separador.

  :param lista: Lista origen que se desea convertir a String
  :param prefijo: String que se desea incluir antes de cada Item
  :param posfijo: String que se desea incluir después de cada Item
  :param separador: String con el que se desea separar cada Item
  :param sinSeparadorAlFinal: Boolean indicando si debe incluir o no
  """

  if not isinstance(lista, list):
    if not isinstance(lista, str):
      mostrarErrorXConsola("utils.py", "listaToStr()", f"No es un tipo Lista: {lista=} {type(lista)=}")
    else:
      s = prefijo + lista + posfijo + separador
  else:
    if len(lista) == 1:
      s = prefijo + str(lista[0]) + posfijo + separador
    elif len(lista) > 1:
      s = ""
      for l in lista:
        s += prefijo + l + posfijo + separador

  if sinSeparadorAlFinal:
    s = s[:len(s)-len(separador)]

  return s

#################################################
# Rutinas para controlar los mensajes x Consola #
#################################################
def mostrarErrorXConsola(modulo, funcion, excepcion)->None:
  """Muestra un Error x la Consola y puede incluir la funcion llamadora y en que fuente se encuentra.

  :param modulo: Archivo fuente donde se encuentra la función llamadora
  :param funcion: Función que desea mostrar el error
  :param excepcion: Mensaje indicando el error ocurrido
  """
  print("*"*6)
  print("*"*6, " "*5, datetime.now().time())
  print("*"*6, f"ERROR {_formatearMsgXConsola(excepcion, modulo, funcion)}")
  print("*"*6)

def mostrarInfoXConsola(mensaje, modulo="", funcion="")->None:
  """Muestra un Mensaje Informativo x la Consola. Opcionalmente puede incluir la funcion llamadora y en que fuente se encuentra.

  :param modulo: Archivo fuente donde se encuentra la función llamadora
  :param funcion: Función que desea mostrar el error
  :param excepcion: Mensaje Informativo a Mostrar
  """
  print(f"****** INFORMACION {_formatearMsgXConsola(mensaje, modulo, funcion)}")

def _formatearMsgXConsola(mensaje, modulo="", funcion="")->str:
  """Formatea un Mensaje de Error o Informativo a mostrar x la Consola. Opcionalmente puede incluir la funcion llamadora y en que fuente se encuentra.

  :param modulo: Archivo fuente donde se encuentra la función llamadora
  :param funcion: Función que desea mostrar el error
  :param excepcion: Mensaje de Error o Informativo a Mostrar
  """
  # Agrego "()" si no se especificó en origen
  if funcion != "":
    if funcion[-1] != ")":
      if funcion[-1] != "(":
        funcion += "()"
      else:
        funcion += ")"
  
  # Sintaxis: modulo.funcion(): mensaje
  msgPath = ""
  if modulo != "":
    msgPath += modulo
    if funcion != "":
      msgPath += "." + funcion
  elif funcion != "":
      msgPath += funcion
  if msgPath != "":
      msgPath += ": "       
  return msgPath + mensaje

  a = MySQL()
  