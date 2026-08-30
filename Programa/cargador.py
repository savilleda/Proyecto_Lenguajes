# -*- coding: utf-8 -*-
"""Módulo 1: Motor de Expresiones Regulares y Carga.

Contiene las funciones responsables de construir objetos `AFD` a partir de
dos fuentes de entrada:
    1. Entrada manual interactiva por consola (con validación de duplicados).
    2. Archivos de texto plano (.txt), parseados estrictamente mediante
       expresiones regulares (módulo `re` de la biblioteca estándar).

Ningún error de sintaxis, formato o E/S debe detener la ejecución del
programa: todas las funciones públicas devuelven `None` (o una tupla con
un mensaje de error) en caso de fallo, permitiendo que `main.py` informe
al usuario y regrese al menú.
"""

import os
import re
from typing import Dict, Optional, Set, Tuple

from afd import AFD


# ----------------------------------------------------------------------
# EXPRESIONES REGULARES PARA EL PARSEO ESTRICTO DEL ARCHIVO .txt
# ----------------------------------------------------------------------
# Cada patrón captura el contenido de una sección específica del archivo.
# Se usa re.IGNORECASE para tolerar variaciones de mayúsculas/minúsculas
# en las etiquetas, y re.MULTILINE para anclar '^' al inicio de cada línea.
PATRON_NOMBRE = re.compile(r"^\s*NOMBRE\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE)
PATRON_ESTADOS = re.compile(r"^\s*ESTADOS\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE)
PATRON_ALFABETO = re.compile(r"^\s*ALFABETO\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE)
PATRON_INICIAL = re.compile(r"^\s*INICIAL\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE)
PATRON_FINALES = re.compile(r"^\s*FINALES\s*:\s*(.+)\s*$", re.IGNORECASE | re.MULTILINE)
# La sección de transiciones se marca con "TRANSICIONES:" y se extiende
# hasta el final del archivo (o hasta otra sección en mayúsculas, si la
# hubiera). Se captura todo el bloque para procesarlo línea por línea.
PATRON_BLOQUE_TRANSICIONES = re.compile(
    r"^\s*TRANSICIONES\s*:\s*$(.*)", re.IGNORECASE | re.MULTILINE | re.DOTALL
)
# Cada línea de transición individual: origen,simbolo,destino
PATRON_LINEA_TRANSICION = re.compile(
    r"^\s*([^,\s]+)\s*,\s*([^,\s]+)\s*,\s*([^,\s]+)\s*$"
)
TOKENS_EPSILON = {"", "epsilon", "eps", "ε", "landa", "λ", "lambda"}
PATRON_ID = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PATRON_SIMBOLO_ALFABETO = re.compile(r"^[^,\s]+$")


def _dividir_lista(
    texto: str, advertencias: list = None, tipo: str = "estado"
) -> Set[str]:
    """Convierte una cadena separada por comas en un conjunto de tokens limpios.

    Args:
        texto: Cadena tipo "q0, q1,q2" tal como aparece en el archivo.
        advertencias: Lista opcional donde registrar tokens inválidos.
        tipo: Tipo de validación a aplicar: 'estado' o 'alfabeto'.

    Returns:
        Set[str]: Conjunto de elementos sin espacios en blanco y sin
        elementos vacíos.
    """
    resultado = set()
    patron = PATRON_ID if tipo == "estado" else PATRON_SIMBOLO_ALFABETO
    etiqueta = "Identificador" if tipo == "estado" else "Símbolo del alfabeto"

    for token in texto.split(","):
        token = token.strip()
        if token == "":
            continue
        if not patron.match(token):
            if advertencias is not None:
                advertencias.append(f"{etiqueta} inválido ignorado: '{token}'.")
            continue
        resultado.add(token)
    return resultado


# ----------------------------------------------------------------------
# CARGA DESDE ARCHIVO .txt
# ----------------------------------------------------------------------
def leer_afd_desde_archivo(ruta: str) -> Tuple[Optional[AFD], list]:
    """Parsea un archivo .txt con la definición de un AFD usando regex.

    Formato esperado del archivo::

        NOMBRE: MiAutomata
        ESTADOS: q0,q1,q2
        ALFABETO: a,b
        INICIAL: q0
        FINALES: q2
        TRANSICIONES:
        q0,a,q1
        q0,b,q0
        q1,a,q1
        q1,b,q2
        q2,a,q2
        q2,b,q2

    Args:
        ruta: Ruta del archivo .txt a leer.

    Returns:
        Tuple[Optional[AFD], list]: Una tupla (afd, advertencias). `afd`
        es None si el archivo no pudo abrirse o le faltan secciones
        obligatorias; en ese caso, la lista de advertencias contiene el
        motivo del fallo. Si `afd` no es None, puede seguir teniendo
        advertencias no críticas (por ejemplo, líneas de transición mal
        formateadas que fueron ignoradas).
    """
    advertencias: list = []

    # --- Manejo robusto de errores de E/S ---
    if not os.path.isfile(ruta):
        return None, [f"El archivo '{ruta}' no existe o no es un archivo válido."]

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
    except (OSError, IOError, UnicodeDecodeError) as error:
        return None, [f"No fue posible leer el archivo '{ruta}': {error}"]

    # --- Extracción de secciones simples mediante regex ---
    coincidencia_nombre = PATRON_NOMBRE.search(contenido)
    coincidencia_estados = PATRON_ESTADOS.search(contenido)
    coincidencia_alfabeto = PATRON_ALFABETO.search(contenido)
    coincidencia_inicial = PATRON_INICIAL.search(contenido)
    coincidencia_finales = PATRON_FINALES.search(contenido)
    coincidencia_transiciones = PATRON_BLOQUE_TRANSICIONES.search(contenido)

    # Las secciones ESTADOS, ALFABETO e INICIAL son obligatorias para
    # construir un AFD mínimamente utilizable.
    if not coincidencia_estados:
        return None, ["Falta la sección obligatoria 'ESTADOS:' en el archivo."]
    if not coincidencia_alfabeto:
        return None, ["Falta la sección obligatoria 'ALFABETO:' en el archivo."]
    if not coincidencia_inicial:
        return None, ["Falta la sección obligatoria 'INICIAL:' en el archivo."]

    nombre = coincidencia_nombre.group(1).strip() if coincidencia_nombre else "AFD_Importado"
    estados = _dividir_lista(coincidencia_estados.group(1), advertencias, tipo="estado")
    alfabeto = _dividir_lista(coincidencia_alfabeto.group(1), advertencias, tipo="alfabeto")
    estado_inicial = coincidencia_inicial.group(1).strip()
    estados_finales = (
        _dividir_lista(coincidencia_finales.group(1), advertencias, tipo="estado")
        if coincidencia_finales
        else set()
    )

    if not coincidencia_finales:
        advertencias.append(
            "No se encontró la sección 'FINALES:'; se asume conjunto F vacío."
        )

    # --- Parseo línea por línea del bloque de transiciones ---
    transiciones: Dict[Tuple[str, str], str] = {}
    conflictos: Dict[Tuple[str, str], Set[str]] = {}

    if not coincidencia_transiciones:
        advertencias.append(
            "No se encontró la sección 'TRANSICIONES:'; delta quedará vacía."
        )
    else:
        bloque = coincidencia_transiciones.group(1)
        offset_lineas = contenido[:coincidencia_transiciones.start(1)].count("\n")

        for numero_linea, linea in enumerate(bloque.splitlines(), start=1):
            numero_linea_real = offset_lineas + numero_linea
            linea_limpia = linea.strip()
            if linea_limpia == "" or linea_limpia.startswith("#"):
                # Se ignoran líneas vacías y comentarios (prefijo '#').
                continue

            coincidencia = PATRON_LINEA_TRANSICION.match(linea_limpia)
            if not coincidencia:
                advertencias.append(
                    f"[Línea {numero_linea_real}] Transición mal formada (ignorada): '{linea_limpia}' "
                    f"(se esperaba 'origen,simbolo,destino')."
                )
                continue

            origen, simbolo, destino = coincidencia.groups()
            if simbolo.strip().lower() in TOKENS_EPSILON:
                advertencias.append(
                    f"[Línea {numero_linea_real}] Transición-ε detectada en '{linea_limpia}': "
                    f"un AFD no admite transiciones que no consuman símbolo "
                    f"(esto corresponde a un AFND/AFN-ε, no a un AFD)."
                )
                continue

            clave = (origen, simbolo)

            if clave in transiciones and transiciones[clave] != destino:
                # Se detecta una transición múltiple (posible AFND): se
                # registra el conflicto en lugar de sobrescribir en silencio.
                conflictos.setdefault(clave, {transiciones[clave]})
                conflictos[clave].add(destino)
                advertencias.append(
                    f"[Línea {numero_linea_real}] Transición múltiple detectada para {clave}: ya existía "
                    f"destino '{transiciones[clave]}', se ignora el nuevo "
                    f"destino '{destino}' (se conserva el primero registrado)."
                )
                continue

            transiciones[clave] = destino

    afd = AFD(
        nombre=nombre,
        estados=estados,
        alfabeto=alfabeto,
        transiciones=transiciones,
        estado_inicial=estado_inicial,
        estados_finales=estados_finales,
    )
    # Se anexa el registro de conflictos de determinismo detectados durante
    # el parseo, consumido posteriormente por `AFD.verificar_determinismo`.
    afd.transiciones_conflictivas = conflictos

    return afd, advertencias


# ----------------------------------------------------------------------
# CARGA MANUAL INTERACTIVA POR CONSOLA
# ----------------------------------------------------------------------
def _solicitar_lista_no_vacia(mensaje: str, tipo: str = "estado") -> Set[str]:
    """Solicita al usuario una lista separada por comas, sin permitir vacío.

    Args:
        mensaje: Texto de solicitud mostrado al usuario.
        tipo: Tipo de validación a aplicar: 'estado' o 'alfabeto'.

    Returns:
        Set[str]: Conjunto de elementos ingresados.
    """
    while True:
        try:
            entrada = input(mensaje).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada cancelada. Se usará una lista vacía.")
            return set()

        elementos = _dividir_lista(entrada, tipo=tipo)
        if not elementos:
            print("  [!] Debe ingresar al menos un elemento. Intente de nuevo.")
            continue
        if len(elementos) != len(entrada.split(",")):
            print("  [!] Se detectaron y eliminaron elementos duplicados o vacíos.")
        return elementos


def leer_afd_manual() -> Optional[AFD]:
    """Construye un AFD mediante entrada interactiva por consola.

    Solicita nombre, estados, alfabeto, estado inicial, estados finales y,
    finalmente, las transiciones una por una, validando en cada paso que
    no existan duplicados ni referencias a estados/símbolos inexistentes.

    Returns:
        Optional[AFD]: El AFD construido, o None si el usuario cancela la
        operación (Ctrl+C / EOF) antes de completarla.
    """
    print("\n--- CREACIÓN MANUAL DE UN AFD ---")
    try:
        nombre = input("Nombre del AFD: ").strip() or "AFD_Manual"

        estados = _solicitar_lista_no_vacia("Estados (separados por comas), ej. q0,q1,q2: ", tipo="estado")
        alfabeto = _solicitar_lista_no_vacia("Alfabeto (separados por comas), ej. a,b o 0,1: ", tipo="alfabeto")

        # --- Validación del estado inicial contra el conjunto Q ---
        while True:
            estado_inicial = input(f"Estado inicial (debe estar en {sorted(estados)}): ").strip()
            if estado_inicial in estados:
                break
            print(f"  [!] '{estado_inicial}' no pertenece a los estados definidos. Intente de nuevo.")

        # --- Validación de F como subconjunto de Q ---
        while True:
            entrada_finales = input(
                f"Estados finales (separados por comas, subconjunto de {sorted(estados)}): "
            ).strip()
            estados_finales = _dividir_lista(entrada_finales, tipo="estado")
            invalidos = estados_finales - estados
            if invalidos:
                print(f"  [!] Los siguientes estados no existen en Q: {sorted(invalidos)}. Intente de nuevo.")
                continue
            break

        # --- Captura de transiciones, una por combinación (estado, símbolo) ---
        print("\nDefinición de transiciones delta(estado, símbolo) = estado_destino.")
        print("Presione ENTER sin texto para omitir una transición (quedará indefinida).\n")
        transiciones: Dict[Tuple[str, str], str] = {}
        for estado in sorted(estados):
            for simbolo in sorted(alfabeto):
                while True:
                    destino = input(f"  delta({estado}, {simbolo}) = ").strip()
                    if destino == "":
                        print("    -> Transición omitida (quedará indefinida).")
                        break
                    if destino not in estados:
                        print(f"    [!] '{destino}' no pertenece a Q. Intente de nuevo.")
                        continue
                    transiciones[(estado, simbolo)] = destino
                    break

        afd = AFD(
            nombre=nombre,
            estados=estados,
            alfabeto=alfabeto,
            transiciones=transiciones,
            estado_inicial=estado_inicial,
            estados_finales=estados_finales,
        )
        afd.transiciones_conflictivas = {}  # No hay conflictos posibles en modo manual.
        print(f"\n[OK] AFD '{nombre}' creado exitosamente.\n")
        return afd

    except (EOFError, KeyboardInterrupt):
        print("\n[!] Creación cancelada por el usuario.")
        return None
    except Exception as error:  # Red de seguridad final: nunca debe colapsar.
        print(f"\n[ERROR] Ocurrió un problema inesperado durante la creación manual: {error}")
        return None
