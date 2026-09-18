# -*- coding: utf-8 -*-
"""Módulo 2: Modelo y Motor de Validación Estructural.

Este módulo define la clase `AFD`, que encapsula la quíntupla formal
M = (Q, Sigma, delta, q0, F) de un Autómata Finito Determinista, así como
todas las operaciones de validación estructural y análisis de alcanzabilidad
requeridas para certificar que el autómata está correctamente definido.

Estructuras de datos utilizadas (obligatorio por especificación):
    - Q (estados) y Sigma (alfabeto): conjuntos (set) -> permiten pertenencia
      O(1) amortizado y evitan duplicados de forma natural.
    - delta (transiciones): diccionario (dict) cuya clave es la tupla
      (estado_actual, simbolo) y cuyo valor es el estado_siguiente. Esto
      representa una función matemática delta: Q x Sigma -> Q sin recurrir
      a estructuras condicionales extensas (if/elif encadenados)
"""

from typing import Dict, List, Set, Tuple


class ErrorValidacionAFD(Exception):
    """Excepción específica para errores de validación estructural del AFD.

    Se lanza cuando la quíntupla no cumple las condiciones formales de un
    Autómata Finito Determinista (por ejemplo, q0 fuera de Q, F no
    subconjunto de Q, transiciones inconsistentes, etc.).
    """
    pass


class AFD:
    """Representa un Autómata Finito Determinista mediante su quíntupla formal.

    M = (Q, Sigma, delta, q0, F)

    Attributes:
        nombre (str): Nombre identificador del autómata (uso descriptivo).
        estados (Set[str]): Conjunto Q de todos los estados del autómata.
        alfabeto (Set[str]): Conjunto Sigma de símbolos válidos de entrada.
        transiciones (Dict[Tuple[str, str], str]): Función delta representada
            como diccionario {(estado_actual, simbolo): estado_siguiente}.
        estado_inicial (str): Estado q0, punto de partida de la computación.
        estados_finales (Set[str]): Conjunto F de estados de aceptación.
    """
    
    def __init__(
        self,
        nombre: str = "AFD_Sin_Nombre",
        estados: Set[str] = None,
        alfabeto: Set[str] = None,
        transiciones: Dict[Tuple[str, str], str] = None,
        estado_inicial: str = "",
        estados_finales: Set[str] = None,
    ) -> None:
        """Inicializa la quíntupla del autómata.

        Args:
            nombre: Nombre descriptivo del AFD.
            estados: Conjunto Q de estados. Si es None, se inicializa vacío.
            alfabeto: Conjunto Sigma de símbolos. Si es None, se inicializa vacío.
            transiciones: Diccionario delta (estado, simbolo) -> estado.
                Si es None, se inicializa vacío.
            estado_inicial: Estado q0.
            estados_finales: Conjunto F de estados de aceptación. Si es None,
                se inicializa vacío.
        """
        self.nombre: str = nombre
        # Se usan sets para garantizar unicidad automática de elementos.
        self.estados: Set[str] = set(estados) if estados is not None else set()
        self.alfabeto: Set[str] = set(alfabeto) if alfabeto is not None else set()
        # El diccionario modela directamente delta: (Q x Sigma) -> Q
        self.transiciones: Dict[Tuple[str, str], str] = (
            dict(transiciones) if transiciones is not None else {}
        )
        self.estado_inicial: str = estado_inicial
        self.estados_finales: Set[str] = (
            set(estados_finales) if estados_finales is not None else set()
        )

    # ------------------------------------------------------------------
    # VALIDACIÓN DE LA QUÍNTUPLA FORMAL
    # ------------------------------------------------------------------
    def validar_quintupla(self) -> List[str]:
        """Valida las condiciones formales básicas de la quíntupla M.

        Verifica, en orden:
            1. q0 pertenece a Q.
            2. F es subconjunto de Q.
            3. Toda transición usa estados de origen/destino en Q y
               símbolos en Sigma (consistencia de dominio y codominio).

        Returns:
            List[str]: Lista de mensajes de error encontrados. Una lista
            vacía indica que la quíntupla es formalmente consistente.
        """
        # Se centralizan las reglas para usarlas también con AFND.
        from validador import ValidadorAutomata
        return ValidadorAutomata().errores(self)

    # ------------------------------------------------------------------
    # VERIFICACIÓN DE DETERMINISTICIDAD
    # ------------------------------------------------------------------
    def verificar_determinismo(self) -> Tuple[bool, List[str]]:
        """Verifica que delta esté totalmente definida y sea determinista.

        Un AFD válido requiere que, para CADA estado q en Q y CADA símbolo
        a en Sigma, exista EXACTAMENTE una transición delta(q, a). Como se
        usa un diccionario (una clave -> un único valor), la multiplicidad
        de transiciones (característica de un AFND) no puede representarse
        directamente en `self.transiciones`; por ello, la detección de
        transiciones múltiples se realiza durante la carga de datos
        (Módulo 1), y aquí se reportan como advertencias registradas en
        `self.transiciones_conflictivas` si dicho atributo existe.

        Returns:
            Tuple[bool, List[str]]: Una tupla (es_determinista, reportes)
            donde `es_determinista` es True si delta está completamente
            definida sin ambigüedades, y `reportes` contiene el detalle
            de cada anomalía encontrada (faltantes o conflictos).
        """
        reportes: List[str] = []

        # Se recorre cada combinación posible (q, a) en Q x Sigma para
        # comprobar que exista una transición definida.
        for estado in sorted(self.estados):
            for simbolo in sorted(self.alfabeto):
                clave = (estado, simbolo)
                if clave not in self.transiciones:
                    reportes.append(
                        f"Transición faltante: delta('{estado}', '{simbolo}') "
                        f"no está definida (autómata incompleto)."
                    )

        # Se reportan conflictos de multiplicidad detectados en la carga,
        # si el cargador los registró explícitamente (ver cargador.py).
        conflictos = getattr(self, "transiciones_conflictivas", {})
        for (estado, simbolo), destinos in conflictos.items():
            reportes.append(
                f"Transición múltiple (no determinista): desde '{estado}' "
                f"con '{simbolo}' existen varios destinos posibles: "
                f"{sorted(destinos)}. Esto corresponde a un AFND, no a un AFD."
            )

        es_determinista = len(reportes) == 0
        return es_determinista, reportes

    def completar_con_estado_trampa(self, nombre_trampa: str = "q_trampa") -> str:
        """Agrega un estado sumidero para completar un AFD parcial sin
        alterar el lenguaje reconocido. Devuelve "" si ya estaba completo"""
        from validador import ValidadorAutomata
        ValidadorAutomata().exigir_afd(self, completo=False)
        base, contador = nombre_trampa, 0
        while nombre_trampa in self.estados:
            contador += 1
            nombre_trampa = f"{base}_{contador}"

        faltantes = [
            (q, a) for q in self.estados for a in self.alfabeto
            if (q, a) not in self.transiciones
        ]
        if not faltantes:
            return ""

        self.estados.add(nombre_trampa)
        for (q, a) in faltantes:
            self.transiciones[(q, a)] = nombre_trampa
        for a in self.alfabeto:
            self.transiciones[(nombre_trampa, a)] = nombre_trampa
        return nombre_trampa

    # ------------------------------------------------------------------
    # ANÁLISIS ESTRUCTURAL AVANZADO (ALCANZABILIDAD)
    # ------------------------------------------------------------------
    def estados_alcanzables(self) -> Set[str]:
        """Calcula el conjunto de estados alcanzables desde q0 mediante BFS.

        Se recorre el grafo de transiciones en anchura (BFS) partiendo del
        estado inicial, siguiendo cada símbolo del alfabeto disponible desde
        el estado actual.

        Returns:
            Set[str]: Conjunto de estados alcanzables desde el estado inicial
        """
        if self.estado_inicial not in self.estados:
            # Si q0 no es válido, no hay estados alcanzables definibles.
            return set()

        visitados: Set[str] = set()
        cola: List[str] = [self.estado_inicial]
        visitados.add(self.estado_inicial)

        # Cola con índice: no desplaza todos los elementos al sacar uno.
        indice = 0
        while indice < len(cola):
            actual = cola[indice]
            indice += 1
            for simbolo in self.alfabeto:
                siguiente = self.transiciones.get((actual, simbolo))
                if siguiente in self.estados and siguiente not in visitados:
                    visitados.add(siguiente)
                    cola.append(siguiente)

        return visitados

    def estados_inaccesibles(self) -> Set[str]:
        """Calcula los estados que jamás pueden alcanzarse desde q0.

        Returns:
            Set[str]: Q menos el conjunto de estados alcanzables (Q - alcanzables).
        """
        return self.estados - self.estados_alcanzables()

    def estados_finales_alcanzables(self) -> Set[str]:
        """Calcula la intersección entre estados finales y estados alcanzables.

        Returns:
            Set[str]: Estados finales que sí pueden ser alcanzados desde q0
        """
        return self.estados_finales & self.estados_alcanzables()

    def lenguaje_vacio(self) -> bool:
        """Determina si el lenguaje reconocido por el autómata es vacío.

        El lenguaje L(M) es vacío si y solo si ningún estado final es
        alcanzable desde el estado inicial q0

        Returns:
            bool: True si L(M) = vacío (ningún estado final es alcanzable)
        """
        return len(self.estados_finales_alcanzables()) == 0

    # ------------------------------------------------------------------
    # REPRESENTACIONES TEXTUALES (QUÍNTUPLA Y TABLA DE TRANSICIÓN)
    # ------------------------------------------------------------------
    def quintupla_formal(self) -> str:
        """Genera una representación textual formal de M = (Q, Sigma, delta, q0, F).

        Returns:
            str: Cadena formateada mostrando cada componente de la quíntupla
        """
        lineas = [
            f"Autómata: {self.nombre}",
            f"Q  (Estados)        = {{{', '.join(sorted(self.estados))}}}",
            f"Sigma (Alfabeto)    = {{{', '.join(sorted(self.alfabeto))}}}",
            f"q0 (Estado inicial) = {self.estado_inicial}",
            f"F  (Estados finales)= {{{', '.join(sorted(self.estados_finales))}}}",
            "delta (Transiciones):",
        ]
        for (origen, simbolo), destino in sorted(self.transiciones.items()):
            lineas.append(f"    delta({origen}, {simbolo}) = {destino}")
        return "\n".join(lineas)

    def tabla_transicion(self) -> str:
        """Construye la tabla de transición en formato de matriz legible.

        Returns:
            str: Tabla con filas = estados, columnas = símbolos del alfabeto.
            El estado inicial se marca con '->' y los finales con '*'
        """
        estados_ordenados = sorted(self.estados)
        simbolos_ordenados = sorted(self.alfabeto)

        # Se calcula el ancho de columna para alinear la tabla.
        ancho_estado = max([len("ESTADO")] + [len(e) for e in estados_ordenados]) + 4
        ancho_columna = max(
            [8] + [len(s) for s in simbolos_ordenados] + [len(e) for e in estados_ordenados]
        ) + 4

        encabezado = "ESTADO".ljust(ancho_estado)
        for simbolo in simbolos_ordenados:
            encabezado += simbolo.center(ancho_columna)
        lineas = [encabezado, "-" * len(encabezado)]

        for estado in estados_ordenados:
            marca = ""
            if estado == self.estado_inicial:
                marca += "->"
            if estado in self.estados_finales:
                marca += "*"
            etiqueta = f"{marca}{estado}"
            fila = etiqueta.ljust(ancho_estado)
            for simbolo in simbolos_ordenados:
                destino = self.transiciones.get((estado, simbolo), "-")
                fila += str(destino).center(ancho_columna)
            lineas.append(fila)

        lineas.append("")
        lineas.append("Leyenda: '->' estado inicial, '*' estado final, '-' transición no definida")
        return "\n".join(lineas)

    def generar_reporte_validacion(self) -> str:
        """Genera un reporte textual completo de validación estructural

        Integra: validación de quíntupla, determinismo, alcanzabilidad y
        vacuidad del lenguaje. Pensado para mostrarse directamente en la
        opción 6 del menú principal

        Returns:
            str: Reporte completo formateado en texto plano.
        """
        secciones: List[str] = []
        secciones.append(f"=== REPORTE DE VALIDACIÓN: {self.nombre} ===\n")

        from validador import ValidadorAutomata
        secciones.append("[CLASIFICACIÓN] " + ValidadorAutomata().clasificar(self))
        errores_quintupla = self.validar_quintupla()
        if errores_quintupla:
            secciones.append("[QUÍNTUPLA] Se encontraron INCONSISTENCIAS:")
            secciones.extend(f"  - {e}" for e in errores_quintupla)
        else:
            secciones.append("[QUÍNTUPLA] Consistente: q0 ∈ Q, F ⊆ Q, transiciones válidas.")

        secciones.append("")
        es_determinista, reportes_det = self.verificar_determinismo()
        if es_determinista and not errores_quintupla:
            secciones.append("[DETERMINISMO] El autómata es un AFD válido y completo.")
        else:
            secciones.append("[DETERMINISMO] Se encontraron PROBLEMAS:")
            secciones.extend(f"  - {r}" for r in reportes_det)

        secciones.append("")
        if errores_quintupla or getattr(self, "transiciones_conflictivas", {}):
            secciones.append("[ANÁLISIS] Corrija la definición antes de analizar su lenguaje.")
            return "\n".join(secciones)
        alcanzables = self.estados_alcanzables()
        inaccesibles = self.estados - alcanzables
        finales_alcanzables = self.estados_finales & alcanzables
        secciones.append(f"[ALCANZABILIDAD] Estados alcanzables desde q0: {sorted(alcanzables)}")
        secciones.append(f"[ALCANZABILIDAD] Estados inaccesibles (Q - alcanzables): {sorted(inaccesibles)}")
        secciones.append(f"[ALCANZABILIDAD] Estados finales alcanzables: {sorted(finales_alcanzables)}")

        secciones.append("")
        if not finales_alcanzables:
            secciones.append("[LENGUAJE] L(M) es VACÍO: ningún estado final es alcanzable desde q0.")
        else:
            secciones.append("[LENGUAJE] L(M) NO es vacío: existe al menos un estado final alcanzable.")

        return "\n".join(secciones)

    def __str__(self) -> str:
        """Representación en cadena del AFD (equivalente a la quíntupla formal).

        Returns:
            str: Ver `quintupla_formal`.
        """
        return self.quintupla_formal()
