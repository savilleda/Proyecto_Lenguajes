from typing import Optional

from afd import AFD
from afnd import AFND
from cargador import CargadorAutomata
from conversor import ConversorAFND
from simulador import Simulador
from validador import ValidadorAutomata


class EspacioAutomata:
    """Conserva todos los datos asociados a un autómata cargado"""

    def __init__(self, original, afd_actual, conversor, simulador):
        self.original = original
        self.afd_actual = afd_actual
        self.conversor = conversor
        self.simulador = simulador

    @classmethod
    def crear(cls, automata):
        conversor = ConversorAFND()
        afd_actual = automata
        if isinstance(automata, AFND):
            afd_actual = conversor.convertir(automata)
        return cls(automata, afd_actual, conversor, Simulador())

    @property
    def tipo(self):
        return "AFND" if isinstance(self.original, AFND) else "AFD"


class AplicacionAFD:
    def __init__(self):
        self.espacios: list[Optional[EspacioAutomata]] = [None, None]
        self.activo: Optional[int] = None
        self.cargador = CargadorAutomata()
        self.validador = ValidadorAutomata()

    def espacio_activo(self):
        if self.activo is None or self.espacios[self.activo] is None:
            raise ValueError("Primero cree o cargue un autómata.")
        return self.espacios[self.activo]

    def mostrar_espacios(self):
        print("\nAUTÓMATAS CARGADOS")
        for indice, espacio in enumerate(self.espacios, start=1):
            if espacio is None:
                print(f" Espacio {indice}: vacío")
            else:
                marca = " (ACTIVO)" if indice - 1 == self.activo else ""
                print(f" Espacio {indice}: {espacio.original.nombre} "
                      f"[{espacio.tipo}]{marca}")

    def _espacio_libre(self):
        return next((i for i, espacio in enumerate(self.espacios)
                     if espacio is None), None)

    def instalar(self, automata):
        indice = self._espacio_libre()
        if indice is None:
            print("\n[!] Los dos espacios están ocupados. Quite uno antes de cargar otro.")
            return False
        try:
            espacio = EspacioAutomata.crear(automata)
        except (ValueError, TypeError) as error:
            print(f"[!] No se pudo cargar el autómata: {error}")
            return False

        self.espacios[indice] = espacio
        self.activo = indice
        print(f"\nCargado en el espacio {indice + 1}: {automata.nombre}")
        print(self.validador.clasificar(automata))
        if isinstance(automata, AFND):
            print(automata.tabla_transicion())
            self.convertir()
        return True

    def cargar(self, tipo, archivo=False):
        if self._espacio_libre() is None:
            print("\n[!] Los dos espacios están ocupados. Quite uno antes de cargar otro.")
            return
        if archivo:
            ruta = input(f"Ruta del archivo {tipo}: ")
            automata, errores = self.cargador.desde_archivo(ruta, tipo)
            for error in errores:
                print(f"[!] {error}")
        else:
            automata = self.cargador.manual(tipo)
        if automata is not None:
            self.instalar(automata)

    def exigir_afd(self):
        espacio = self.espacio_activo()
        self.validador.exigir_afd(espacio.afd_actual)
        return espacio

    def mostrar(self):
        espacio = self.espacio_activo()
        print("\nAUTÓMATA ORIGINAL")
        print(espacio.original.quintupla_formal())
        print(espacio.original.tabla_transicion())
        if isinstance(espacio.original, AFND):
            print("\nAFD EQUIVALENTE")
            print(espacio.afd_actual.quintupla_formal())
            print(espacio.afd_actual.tabla_transicion())

    def validar(self):
        espacio = self.espacio_activo()
        print(self.validador.clasificar(espacio.original))
        for error in self.validador.errores(espacio.original):
            print(f"[!] {error}")
        print(espacio.afd_actual.generar_reporte_validacion())
        if (self.validador.clasificar(espacio.afd_actual) == "AFD incompleto"
                and input("¿Completar con estado trampa? (s/n): ").strip().lower() == "s"):
            trampa = espacio.afd_actual.completar_con_estado_trampa()
            print(f"Se agregó {trampa}.")

    def convertir(self):
        espacio = self.espacio_activo()
        if not isinstance(espacio.original, AFND):
            raise ValueError("La opción 7 requiere un AFND válido cargado.")
        if not espacio.conversor.equivalencias:
            espacio.afd_actual = espacio.conversor.convertir(espacio.original)
        print("Conversión terminada.")
        print(espacio.conversor.tabla_equivalencias())
        print(espacio.afd_actual.tabla_transicion())

    def equivalencias(self):
        espacio = self.espacio_activo()
        print(espacio.conversor.tabla_equivalencias())

    def tabla_generada(self):
        espacio = self.espacio_activo()
        if not isinstance(espacio.original, AFND):
            raise ValueError("No hay un AFD generado a partir de un AFND.")
        print(espacio.afd_actual.tabla_transicion())

    def evaluar(self):
        espacio = self.exigir_afd()
        cadena = input("Cadena (ENTER: cadena vacía): ")
        espacio.simulador.evaluar_cadena(espacio.afd_actual, cadena)

    def lote(self):
        espacio = self.exigir_afd()
        ruta = input("Archivo de cadenas (cada línea vacía representa epsilon): ")
        resultados, errores = espacio.simulador.evaluar_lote(
            espacio.afd_actual, ruta.strip().strip('"'))
        for error in errores:
            print(f"[!] {error}")
        print(espacio.simulador.generar_reporte_lote(resultados))

    def historial(self):
        print(self.exigir_afd().simulador.mostrar_historial())

    def analisis(self):
        espacio = self.exigir_afd()
        print(espacio.afd_actual.generar_reporte_validacion())

    def seleccionar(self):
        self.mostrar_espacios()
        opcion = input("Número del espacio a seleccionar (ENTER: cancelar): ").strip()
        if not opcion:
            return
        if opcion not in {"1", "2"} or self.espacios[int(opcion) - 1] is None:
            print("[!] Seleccione un espacio ocupado")
            return
        self.activo = int(opcion) - 1
        print(f"Espacio {opcion} seleccionado.")

    def quitar(self):
        self.mostrar_espacios()
        opcion = input("Número del espacio a quitar (ENTER: cancelar): ").strip()
        if not opcion:
            return
        if opcion not in {"1", "2"} or self.espacios[int(opcion) - 1] is None:
            print("[!] Seleccione un espacio ocupado")
            return
        indice = int(opcion) - 1
        nombre = self.espacios[indice].original.nombre
        confirmacion = input(f"¿Quitar '{nombre}'? (s/n): ").strip().lower()
        if confirmacion != "s":
            print("Operación cancelada.")
            return
        self.espacios[indice] = None
        if self.activo == indice:
            restantes = [i for i, espacio in enumerate(self.espacios)
                         if espacio is not None]
            self.activo = restantes[0] if restantes else None
        print("Autómata quitado.")

    def otro(self):
        while True:
            self.mostrar_espacios()
            print("\n1. Cargar AFD manualmente")
            print("2. Cargar AFD desde archivo")
            print("3. Cargar AFND manualmente")
            print("4. Cargar AFND desde archivo")
            print("5. Seleccionar autómata activo")
            print("6. Quitar autómata")
            print("7. Consultar espacios")
            print("8. Regresar al menú principal")
            opcion = input("Opción: ").strip()
            acciones = {
                "1": lambda: self.cargar("AFD"),
                "2": lambda: self.cargar("AFD", True),
                "3": lambda: self.cargar("AFND"),
                "4": lambda: self.cargar("AFND", True),
                "5": self.seleccionar,
                "6": self.quitar,
                "7": self.mostrar_espacios,
            }
            if opcion == "8":
                return
            accion = acciones.get(opcion)
            if accion is None:
                print("[!] Seleccione una opción del 1 al 8.")
            else:
                accion()

    def ejecutar(self):
        acciones = {
            "1": lambda: self.cargar("AFD"),
            "2": lambda: self.cargar("AFD", True),
            "3": lambda: self.cargar("AFND"),
            "4": lambda: self.cargar("AFND", True),
            "5": self.mostrar, "6": self.validar, "7": self.convertir,
            "8": self.equivalencias, "9": self.tabla_generada,
            "10": self.evaluar, "11": self.lote, "12": self.historial,
            "13": self.analisis, "14": self.otro,
        }
        menu = """
=== MOTOR DE AUTÓMATAS: FASES 1 Y 2 ===
 1. Crear AFD manualmente
 2. Cargar AFD desde archivo
 3. Crear AFND manualmente
 4. Cargar AFND desde archivo
 5. Definición formal y tabla del autómata
 6. Validar estructura / completar AFD con trampa
 7. Convertir AFND a AFD
 8. Tabla de equivalencias de macroestados
 9. Tabla del AFD generado
10. Evaluar cadena
11. Evaluar archivo de cadenas
12. Historial de evaluaciones
13. Análisis estructural del AFD
14. Administrar autómatas
15. Salir"""
        while True:
            try:
                self.mostrar_espacios()
                print(menu)
                opcion = input("Opción: ").strip()
                if opcion == "15":
                    break
                accion = acciones.get(opcion)
                if accion is None:
                    print("[!] Seleccione un número del 1 al 15.")
                else:
                    accion()
            except (EOFError, KeyboardInterrupt):
                print("\nSesión finalizada.")
                break
            except (ValueError, OSError, UnicodeError) as error:
                print(f"[!] {error}")


def main():
    AplicacionAFD().ejecutar()


if __name__ == "__main__":
    main()
