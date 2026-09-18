"""Lectura de archivos y entrada manual; la sintaxis se delega al analizador"""

from analizador import AnalizadorSintactico
from validador import ValidadorAutomata
from afd import AFD
from afnd import AFND


class CargadorAutomata:
    def __init__(self):
        self.analizador = AnalizadorSintactico()

    def desde_archivo(self, ruta, tipo=None):
        try:
            # utf-8-sig acepta también archivos guardados con BOM en Windows.
            with open(ruta.strip().strip('"'), encoding="utf-8-sig") as archivo:
                return self.analizador.analizar(archivo.read(), tipo)
        except (OSError, UnicodeError) as error:
            return None, [f"No se pudo leer el archivo: {error}"]

    def _pedir_conjunto(self, mensaje, alfabeto=False, permitir_vacio=False):
        while True:
            try:
                texto = input(mensaje).strip()
                conjunto = self.analizador.lista(texto, not alfabeto)
                if not conjunto and not permitir_vacio:
                    raise ValueError("Ingrese al menos un elemento.")
                if alfabeto:
                    temporal = AFD(estados={"q0"}, alfabeto=conjunto, estado_inicial="q0")
                    errores = ValidadorAutomata().errores(temporal)
                    if errores:
                        raise ValueError(" ".join(errores))
                if texto and texto != "∅" and len(texto.split(",")) != len(conjunto):
                    print("Los elementos repetidos se guardarán una sola vez.")
                return conjunto
            except ValueError as error:
                print(f"[!] {error}")

    def manual(self, tipo):
        """Solicita cada componente y permite corregir entradas sin reiniciar."""
        if tipo not in {"AFD", "AFND"}:
            raise ValueError("Tipo desconocido.")
        try:
            nombre = input(f"Nombre del {tipo}: ").strip() or tipo + "_Manual"
            estados = self._pedir_conjunto("Estados separados por comas: ")
            alfabeto = self._pedir_conjunto("Alfabeto separado por comas (ENTER: vacío): ",
                                           alfabeto=True, permitir_vacio=True)
            while True:
                inicial = input("Estado inicial: ").strip()
                if inicial in estados:
                    break
                print("[!] El estado inicial debe pertenecer a Q.")
            while True:
                finales = self._pedir_conjunto("Finales separados por comas (ENTER: ninguno): ",
                                              permitir_vacio=True)
                if finales <= estados:
                    break
                print("[!] Todos los finales deben pertenecer a Q.")
            print("Use | para varios destinos del AFND. ENTER o ∅: sin destino.")
            delta = {}
            for estado in sorted(estados):
                for simbolo in sorted(alfabeto):
                    while True:
                        texto = input(f"delta({estado}, {simbolo}) = ").strip()
                        destinos = set() if texto in {"", "∅"} else {p.strip() for p in texto.split("|")}
                        if not destinos <= estados:
                            print("[!] Hay destinos que no pertenecen a Q.")
                            continue
                        if tipo == "AFD" and len(destinos) > 1:
                            print("[!] Un AFD admite un solo destino por transición.")
                            continue
                        if tipo == "AFND":
                            delta[(estado, simbolo)] = destinos
                        elif destinos:
                            delta[(estado, simbolo)] = next(iter(destinos))
                        break
            clase = AFND if tipo == "AFND" else AFD
            return clase(nombre, estados, alfabeto, delta, inicial, finales)
        except (EOFError, KeyboardInterrupt):
            print("\nCreación cancelada.")
            return None


# Estos accesos conservan los nombres usados por el código de la Fase 1.
def leer_afd_desde_archivo(ruta):
    return CargadorAutomata().desde_archivo(ruta, "AFD")


def leer_afd_manual():
    return CargadorAutomata().manual("AFD")
