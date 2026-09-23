
import re

from afd import AFD
from afnd import AFND
from validador import ValidadorAutomata


class AnalizadorSintactico:
   
    CABECERA = re.compile(r"(NOMBRE|TIPO|ESTADOS|ALFABETO|INICIAL|FINALES)\s*[:=]\s*(.*)", re.I)
    BLOQUE = re.compile(r"TRANSICIONES\s*:\s*", re.I)
    TRANSICION = re.compile(r"([^,\s]+)\s*,\s*([^,\s]*)\s*,\s*(.*?)")
    IDENTIFICADOR = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

    def lista(self, texto, identificadores=True):
        """No descarta datos malos silenciosamente; elimina solo duplicados."""
        if not texto.strip() or texto.strip() == "∅":
            return set()
        elementos = [elemento.strip() for elemento in texto.split(",")]
        if any(not elemento for elemento in elementos):
            raise ValueError("Hay un elemento vacío entre separadores.")
        if identificadores and any(not self.IDENTIFICADOR.fullmatch(e) for e in elementos):
            raise ValueError("Los estados deben empezar con letra o _ y continuar "
                             "con letras, dígitos o _.")
        return set(elementos)

    def analizar(self, texto, tipo_esperado=None):
        campos, lineas_campos, transiciones, errores = {}, {}, [], []
        en_transiciones = False
        for numero, linea in enumerate(texto.splitlines(), 1):
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if self.BLOQUE.fullmatch(linea):
                if en_transiciones:
                    errores.append(f"Línea {numero}: sección TRANSICIONES repetida.")
                en_transiciones = True
                continue
            cabecera = self.CABECERA.fullmatch(linea)
            if cabecera:
                clave, valor = cabecera.groups()
                clave = clave.upper()
                if en_transiciones or clave in campos:
                    errores.append(f"Línea {numero}: sección {clave} repetida o fuera de lugar.")
                else:
                    campos[clave], lineas_campos[clave] = valor.strip(), numero
                continue
            coincidencia = self.TRANSICION.fullmatch(linea) if en_transiciones else None
            if not coincidencia:
                errores.append(f"Línea {numero}: sintaxis inválida: {linea!r}.")
            else:
                transiciones.append((numero, coincidencia.groups()))

        for campo in ("NOMBRE", "ESTADOS", "ALFABETO", "INICIAL", "FINALES"):
            if campo not in campos:
                errores.append(f"Falta la sección {campo}.")
        if not en_transiciones:
            errores.append("Falta la sección TRANSICIONES:.")
        tipo = campos.get("TIPO", tipo_esperado or "AFD").upper()
        if tipo not in {"AFD", "AFND"}:
            errores.append("TIPO debe ser AFD o AFND.")
        if tipo_esperado and tipo != tipo_esperado:
            errores.append(f"El archivo declara {tipo}; use la opción de carga correspondiente.")
        if errores:
            return None, errores
        conjuntos = {}
        for campo in ("ESTADOS", "ALFABETO", "FINALES"):
            try:
                conjuntos[campo] = self.lista(campos[campo], campo != "ALFABETO")
            except ValueError as error:
                errores.append(f"Línea {lineas_campos[campo]}: {error}")
        if errores:
            return None, errores
        if not campos["NOMBRE"]:
            errores.append("NOMBRE no puede estar vacío.")
        acumuladas = {}
        for numero, (origen, simbolo, texto_destinos) in transiciones:
            try:
                if not self.IDENTIFICADOR.fullmatch(origen):
                    raise ValueError("Identificador de origen inválido.")
                if simbolo.lower() in ValidadorAutomata.EPSILON:
                    raise ValueError("Transiciones epsilon fuera del alcance de esta fase.")
                if texto_destinos == "∅":
                    destinos = set()
                else:
                    # q0|q1 y líneas repetidas se unen, nunca se sobrescriben
                    partes = [p.strip() for p in texto_destinos.split("|")]
                    if any(not self.IDENTIFICADOR.fullmatch(p) for p in partes):
                        raise ValueError("Destinos inválidos; use q0|q1 o ∅.")
                    destinos = set(partes)
                if origen not in conjuntos["ESTADOS"]:
                    raise ValueError(f"Estado origen inexistente: {origen}.")
                if simbolo not in conjuntos["ALFABETO"]:
                    raise ValueError(f"Símbolo inexistente: {simbolo}.")
                if not destinos <= conjuntos["ESTADOS"]:
                    raise ValueError(f"Estados destino inexistentes: {sorted(destinos - conjuntos['ESTADOS'])}.")
                acumuladas.setdefault((origen, simbolo), set()).update(destinos)
            except ValueError as error:
                errores.append(f"Línea {numero}: {error}")
        if errores:
            return None, errores
        argumentos = dict(nombre=campos["NOMBRE"], estados=conjuntos["ESTADOS"],
                          alfabeto=conjuntos["ALFABETO"], estado_inicial=campos["INICIAL"],
                          estados_finales=conjuntos["FINALES"])
        if tipo == "AFND":
            automata = AFND(transiciones=acumuladas, **argumentos)
        else:
            # Se conserva el registro de conflictos de la Fase 1, pero se bloquea
            # la simulación hasta que el archivo se cargue correctamente como AFND
            delta = {clave: sorted(destinos)[0] for clave, destinos in acumuladas.items() if destinos}
            automata = AFD(transiciones=delta, **argumentos)
            automata.transiciones_conflictivas = {c: d for c, d in acumuladas.items() if len(d) > 1}
        errores = ValidadorAutomata().errores(automata)
        return (None, errores) if errores else (automata, [])
