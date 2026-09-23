from afd import AFD
from afnd import AFND
from cargador import CargadorAutomata
from conversor import ConversorAFND
from simulador import Simulador
from validador import ValidadorAutomata


class AplicacionAFD:
    def __init__(self):
        self.original = None
        self.afd_actual = None
        self.cargador = CargadorAutomata()
        self.validador = ValidadorAutomata()
        self.conversor = ConversorAFND()
        self.simulador = Simulador()

    def instalar(self, automata):
        """Solo una carga exitosa sustituye la sesión anterior."""
        self.original = automata
        self.afd_actual = automata if isinstance(automata, AFD) else None
        self.conversor = ConversorAFND()
        self.simulador = Simulador()
        print(f"\nCargado: {automata.nombre}")
        print(self.validador.clasificar(automata))
        if isinstance(automata, AFND):
            print(automata.tabla_transicion())
            self.convertir()  # Conversión automática exigida en la Fase 2.

    def cargar(self, tipo, archivo=False):
        if archivo:
            ruta = input(f"Ruta del archivo {tipo}: ")
            automata, errores = self.cargador.desde_archivo(ruta, tipo)
            for error in errores:
                print(f"[!] {error}")
        else:
            automata = self.cargador.manual(tipo)
        if automata is not None:
            self.instalar(automata)

    def exigir_original(self):
        if self.original is None:
            raise ValueError("Primero cree o cargue un autómata.")

    def exigir_afd(self):
        if self.afd_actual is None:
            raise ValueError("Primero cargue un AFD o complete la conversión del AFND.")
        self.validador.exigir_afd(self.afd_actual)

    def mostrar(self):
        self.exigir_original()
        print("\nAUTÓMATA ORIGINAL")
        print(self.original.quintupla_formal())
        print(self.original.tabla_transicion())
        if isinstance(self.original, AFND) and self.afd_actual is not None:
            print("\nAFD EQUIVALENTE")
            print(self.afd_actual.quintupla_formal())
            print(self.afd_actual.tabla_transicion())

    def validar(self):
        self.exigir_original()
        print(self.validador.clasificar(self.original))
        for error in self.validador.errores(self.original):
            print(f"[!] {error}")
        if self.afd_actual is not None:
            print(self.afd_actual.generar_reporte_validacion())
            if self.validador.clasificar(self.afd_actual) == "AFD incompleto":
                respuesta = input("¿Completar con estado trampa? (s/n): ").strip().lower()
                if respuesta == "s":
                    trampa = self.afd_actual.completar_con_estado_trampa()
                    print(f"Se agregó {trampa}.")

    def convertir(self):
        self.exigir_original()
        if not isinstance(self.original, AFND):
            raise ValueError("La opción 7 requiere un AFND válido cargado.")
        # Repetir la consulta no borra un historial de evaluaciones ya realizadas.
        if self.afd_actual is None:
            self.afd_actual = self.conversor.convertir(self.original)
        print("Conversión terminada.")
        print(self.conversor.tabla_equivalencias())
        print(self.afd_actual.tabla_transicion())

    def equivalencias(self):
        print(self.conversor.tabla_equivalencias())

    def tabla_generada(self):
        if not isinstance(self.original, AFND) or self.afd_actual is None:
            raise ValueError("No hay un AFD generado a partir de un AFND.")
        print(self.afd_actual.tabla_transicion())

    def evaluar(self):
        self.exigir_afd()
        cadena = input("Cadena (ENTER: cadena vacía): ")
        self.simulador.evaluar_cadena(self.afd_actual, cadena)

    def lote(self):
        self.exigir_afd()
        ruta = input("Archivo de cadenas (cada línea vacía representa epsilon): ")
        resultados, errores = self.simulador.evaluar_lote(self.afd_actual, ruta.strip().strip('"'))
        for error in errores:
            print(f"[!] {error}")
        print(self.simulador.generar_reporte_lote(resultados))

    def historial(self):
        print(self.simulador.mostrar_historial())

    def analisis(self):
        self.exigir_afd()
        print(self.afd_actual.generar_reporte_validacion())

    def otro(self):
        print("1. AFD manual\n2. Archivo AFD\n3. AFND manual\n4. Archivo AFND")
        opcion = input("Opción: ").strip()
        opciones = {"1": ("AFD", False), "2": ("AFD", True),
                    "3": ("AFND", False), "4": ("AFND", True)}
        if opcion not in opciones:
            raise ValueError("Seleccione una opción del 1 al 4.")
        self.cargar(*opciones[opcion])

    def ejecutar(self):
        acciones = {"1": lambda: self.cargar("AFD"),
                    "2": lambda: self.cargar("AFD", True),
                    "3": lambda: self.cargar("AFND"),
                    "4": lambda: self.cargar("AFND", True),
                    "5": self.mostrar, "6": self.validar, "7": self.convertir,
                    "8": self.equivalencias, "9": self.tabla_generada,
                    "10": self.evaluar, "11": self.lote, "12": self.historial,
                    "13": self.analisis, "14": self.otro}
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
14. Cargar o crear otro autómata
15. Salir"""
        while True:
            try:
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
