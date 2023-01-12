def asegurarLista(s):
  if isinstance(s, str) or isinstance(s, tuple) or isinstance(s, set):
    return list(s)
  elif isinstance(s, list):
    return s
  else:
    mostrarErrorXConsola("asegurarLista(s)", f"No es un tipo convertible, ni Lista: {s=} {type(s)=}")

def asegurarTupla(s):
  if isinstance(s, str) or isinstance(s, list) or isinstance(s, set):
    return tuple(s)
  elif isinstance(s, tuple):
    return s
  else:
    mostrarErrorXConsola("asegurarTupla(s)", f"No es un tipo convertible, ni Tupla: {s=} {type(s)=}")

def tuplaToStr(tupla, prefijo, posfijo, separador, sinSeparadorAlFinal)->str:
  if not isinstance(tupla, tuple):
    if not isinstance(tupla, str):
      mostrarErrorXConsola("tuplaToStr()", f"No es un tipo Tupla: {tupla=} {type(tupla)=}")
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
  if not isinstance(tupla, tuple):
    if not isinstance(tupla, str):
      mostrarErrorXConsola("tuplaToTupla()", f"No es un tipo Tupla: {tupla=} {type(tupla)=}")
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

def listaToStr(lista, anexo, separador, sinSeparadorAlFinal)->str:
  if not isinstance(lista, list):
    if not isinstance(lista, str):
      mostrarErrorXConsola("listaToStr()", f"No es un tipo Lista: {lista=} {type(lista)=}")
    else:
      s = lista + anexo + separador
  else:
    if len(lista) == 1:
      s = str(lista[0]) + anexo + separador
    elif len(lista) > 1:
      s = ""
      for l in lista:
        s += l + anexo + separador

  if sinSeparadorAlFinal:
    s = s[:len(s)-len(separador)]

  return s

#################################################
# Rutinas para controlar los mensajes x Consola #
#################################################
def mostrarErrorXConsola(accion, excepcion)->None:
    print(f"****** ERROR {accion}: {excepcion}")

def mostrarInfoXConsola(mensaje)->None:
    print(f"****** INFORMACION {mensaje}")
