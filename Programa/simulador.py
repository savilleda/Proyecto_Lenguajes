# -*- coding: utf-8 -*-
"""Módulo 3: Motor de Evaluación y Simulación Paso a Paso.

Implementa la clase `Simulador`, responsable de:
    - Evaluar una cadena individual sobre un AFD, imprimiendo la traza
      completa de la computación (estado por estado).
    - Evaluar un lote de cadenas leídas desde un archivo de texto,
      generando un reporte consolidado.
    - Mantener un historial en memoria de todas las evaluaciones
      realizadas durante la sesión (opción 8 del menú).
"""

import os
from typing import List, Tuple

from afd import AFD


class ResultadoEvaluacion:
    """Representa el resultado de evaluar una única cadena sobre un AFD.

    Atributos:
        cadena (str): Cadena de entrada evaluada.
        aceptada (bool): True si la cadena fue aceptada por el autómata.
        traza (List[str]): Lista de pasos de la computación, en formato
            legible "[Estado] --(símbolo)--> [Estado]".
        motivo (str): Explicación adicional (p. ej. símbolo inválido,
            transición no definida, o estado final alcanzado).
    """

    def __init__(self, cadena: str, aceptada: bool, traza: List[str], motivo: str) -> None:
        """Inicializa el resultado de una evaluación

            cadena: Cadena evaluada.
            aceptada: Veredicto final (True = aceptada, False = rechazada)
            traza: Lista de líneas que documentan cada paso de la simulación
            motivo: Texto explicando el veredicto
        """
        self.cadena = cadena
        self.aceptada = aceptada
        self.traza = traza
        self.motivo = motivo

    def __str__(self) -> str:
        """Representación legible en una sola línea del resultado

        Returns:
            str: Cadena con el veredicto resumido
        """
        veredicto = "ACEPTADA" if self.aceptada else "RECHAZADA"
        cadena_mostrar = self.cadena if self.cadena != "" else "ε (cadena vacía)"
        return f"'{cadena_mostrar}' -> {veredicto} ({self.motivo})"


class Simulador:
    """Motor de simulación de un AFD sobre cadenas de entrada

    Atributos:
        historial (List[ResultadoEvaluacion]): Registro acumulado de todas
            las evaluaciones realizadas (individuales y en lote) durante
            la sesión actual del programa
    """

    def __init__(self) -> None:
        """Inicializa el simulador con un historial vacío"""
        self.historial: List[ResultadoEvaluacion] = []

    def evaluar_cadena(self, afd: AFD, cadena: str, mostrar_traza: bool = True) -> ResultadoEvaluacion:
        """Evalúa una cadena sobre el AFD dado, generando la traza de ejecución

        Algoritmo:
            1. Se verifica que todos los símbolos de la cadena pertenezcan
               a Sigma; si no, se rechaza inmediatamente sin simular.
            2. Se inicia en el estado q0
            3. Por cada símbolo de la cadena, se consulta delta(estado, símbolo)
               en el diccionario de transiciones. Si no existe, la cadena se
               rechaza (autómata incompleto / trampa implícita)
            4. Al finalizar la cadena, se acepta si el estado final de la
               computación pertenece a F; en caso contrario, se rechaza

            afd: Instancia de `AFD` sobre la cual se simula la cadena
            cadena: Cadena de símbolos a evaluar (puede ser vacía, ε)
            mostrar_traza: Si True, imprime la traza paso a paso en consola

      
            ResultadoEvaluacion: Objeto con el veredicto, la traza y el motivo
        """
        from validador import ValidadorAutomata
        ValidadorAutomata().exigir_afd(afd)
        traza: List[str] = []

    
        simbolos_invalidos = [s for s in cadena if s not in afd.alfabeto]
        if simbolos_invalidos:
            motivo = (
                f"La cadena contiene símbolos fuera del alfabeto Sigma: "
                f"{sorted(set(simbolos_invalidos))}."
            )
            resultado = ResultadoEvaluacion(cadena, False, traza, motivo)
            if mostrar_traza:
                self._imprimir_traza(resultado)
            self.historial.append(resultado)
            return resultado

        
        estado_actual = afd.estado_inicial
        for simbolo in cadena:
            siguiente = afd.transiciones.get((estado_actual, simbolo))
            if siguiente is None:
                traza.append(
                    f"[{estado_actual}] --({simbolo})--> [SIN TRANSICIÓN DEFINIDA]"
                )
                motivo = (
                    f"No existe transición delta('{estado_actual}', '{simbolo}'); "
                    f"la cadena se rechaza por autómata incompleto."
                )
                resultado = ResultadoEvaluacion(cadena, False, traza, motivo)
                if mostrar_traza:
                    self._imprimir_traza(resultado)
                self.historial.append(resultado)
                return resultado

            traza.append(f"[{estado_actual}] --({simbolo})--> [{siguiente}]")
            estado_actual = siguiente

        aceptada = estado_actual in afd.estados_finales
        if aceptada:
            motivo = f"El estado final de la computación '{estado_actual}' pertenece a F."
        else:
            motivo = f"El estado final de la computación '{estado_actual}' NO pertenece a F."

        resultado = ResultadoEvaluacion(cadena, aceptada, traza, motivo)
        if mostrar_traza:
            self._imprimir_traza(resultado)
        self.historial.append(resultado)
        return resultado

    def _imprimir_traza(self, resultado: ResultadoEvaluacion) -> None:
        """Imprime en consola la traza paso a paso de una evaluación
        """
        cadena_mostrar = resultado.cadena if resultado.cadena != "" else "ε (cadena vacía)"
        print(f"\n--- TRAZA DE EJECUCIÓN: '{cadena_mostrar}' ---")
        if not resultado.traza:
            print("  (Sin pasos: la cadena es vacía o fue rechazada antes de simular)")
        for paso in resultado.traza:
            print(f"  {paso}")
        veredicto = "ACEPTADA" if resultado.aceptada else "RECHAZADA"
        print(f"Veredicto final: {veredicto}")
        print(f"Motivo: {resultado.motivo}\n")


    def evaluar_lote(self, afd: AFD, ruta: str) -> Tuple[List[ResultadoEvaluacion], List[str]]:
        """Evalúa un conjunto de cadenas leídas desde un archivo de texto

        Se espera una cadena por línea. Una línea vacía representa epsilon.
        Un archivo de cero bytes no contiene cadenas. No se quitan espacios:
        forman parte de la entrada y se rechazan si no pertenecen al alfabeto

            afd: Instancia de `AFD` sobre la cual se evaluará cada cadena
            ruta: Ruta del archivo de cadenas a procesar
        """
        resultados: List[ResultadoEvaluacion] = []
        advertencias: List[str] = []

        if not os.path.isfile(ruta):
            advertencias.append(f"El archivo '{ruta}' no existe o no es válido")
            return resultados, advertencias

        try:
            with open(ruta, "r", encoding="utf-8-sig") as f:
                lineas = f.readlines()
        except (OSError, IOError, UnicodeDecodeError) as error:
            advertencias.append(f"No fue posible leer el archivo '{ruta}': {error}")
            return resultados, advertencias

        if not lineas:
            advertencias.append("El archivo de cadenas está vacío")
            return resultados, advertencias

        for numero_linea, linea in enumerate(lineas, start=1):
            cadena = linea.rstrip("\n").rstrip("\r")
            try:
                resultado = self.evaluar_cadena(afd, cadena, mostrar_traza=False)
                resultados.append(resultado)
            except Exception as error:
                # Ningún error de una cadena individual debe detener el lote.
                advertencias.append(
                    f"Error al evaluar la línea {numero_linea} ('{cadena}'): {error}"
                )

        return resultados, advertencias

    def generar_reporte_lote(self, resultados: List[ResultadoEvaluacion]) -> str:
        """Genera un reporte textual resumido de una evaluación por lote
        """
        if not resultados:
            return "No hay resultados que reportar (lote vacío o no procesado)"

        lineas = ["=== REPORTE DE EVALUACIÓN POR LOTE ==="]
        aceptadas = 0
        for resultado in resultados:
            lineas.append(f"  {resultado}")
            if resultado.aceptada:
                aceptadas += 1

        total = len(resultados)
        lineas.append("")
        lineas.append(f"Total de cadenas evaluadas: {total}")
        lineas.append(f"Aceptadas: {aceptadas}")
        lineas.append(f"Rechazadas: {total - aceptadas}")
        return "\n".join(lineas)

    def mostrar_historial(self) -> str:
        """Genera un reporte textual de todas las evaluaciones realizadas

        Returns:
            str: Historial completo de la sesión, numerado cronológicamente
        """
        if not self.historial:
            return "El historial de evaluaciones está vacío"

        lineas = ["=== HISTORIAL DE EVALUACIONES DE LA SESIÓN ==="]
        for indice, resultado in enumerate(self.historial, start=1):
            lineas.append(f"  {indice}. {resultado}")
        return "\n".join(lineas)
