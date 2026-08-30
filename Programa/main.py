#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo 4: Interfaz de Consola y Menú Principal.

Punto de entrada de la aplicación. Orquesta los módulos `cargador`,
`afd` y `simulador` a través de un menú interactivo de 10 opciones.

Ejecución:
    python main.py

Solo se emplea la biblioteca estándar de Python (os, sys, typing, re
indirectamente a través de `cargador`).
"""

import sys
from typing import Optional

from afd import AFD
from cargador import leer_afd_manual, leer_afd_desde_archivo
from simulador import Simulador


class AplicacionAFD:
    """Controlador principal de la aplicación de consola.

    Attributes:
        afd_actual (Optional[AFD]): AFD actualmente cargado en memoria.
        simulador (Simulador): Instancia única del motor de simulación,
            que conserva el historial de evaluaciones de la sesión.
    """

    def __init__(self) -> None:
        """Inicializa la aplicación sin ningún AFD cargado."""
        self.afd_actual: Optional[AFD] = None
        self.simulador: Simulador = Simulador()

    # ------------------------------------------------------------------
    # UTILIDADES DE PRESENTACIÓN
    # ------------------------------------------------------------------
    @staticmethod
    def imprimir_menu() -> None:
        """Imprime el menú principal de 10 opciones en consola."""
        print("\n" + "=" * 55)
        print("   SIMULADOR DE AUTÓMATA FINITO DETERMINISTA (AFD)")
        print("=" * 55)
        print(" 1. Crear un AFD manualmente")
        print(" 2. Cargar un AFD desde un archivo .txt")
        print(" 3. Mostrar la definición formal del AFD (Quíntupla)")
        print(" 4. Mostrar la tabla de transición")
        print(" 5. Validar la estructura del autómata")
        print(" 6. Evaluar una cadena (con traza paso a paso)")
        print(" 7. Evaluar un archivo de cadenas en lote")
        print(" 8. Consultar el historial de evaluaciones")
        print(" 9. Cargar o crear otro autómata")
        print("10. Salir")
        print("=" * 55)

    def _hay_afd_cargado(self) -> bool:
        """Verifica si existe un AFD cargado, informando al usuario si no.

        Returns:
            bool: True si `self.afd_actual` no es None.
        """
        if self.afd_actual is None:
            print("\n[!] No hay ningún AFD cargado. Use la opción 1 o 2 primero.")
            return False
        return True

    # ------------------------------------------------------------------
    # OPCIONES DEL MENÚ
    # ------------------------------------------------------------------
    def opcion_crear_manual(self) -> None:
        """Opción 1: Crea un AFD mediante entrada manual por consola."""
        nuevo_afd = leer_afd_manual()
        if nuevo_afd is not None:
            self.afd_actual = nuevo_afd
            self.simulador = Simulador()  # Se reinicia el historial al cambiar de AFD.

    def opcion_cargar_desde_archivo(self) -> None:
        """Opción 2: Carga un AFD desde un archivo .txt especificado por el usuario."""
        try:
            ruta = input("\nRuta del archivo .txt a cargar: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[!] Operación cancelada.")
            return

        afd_cargado, advertencias = leer_afd_desde_archivo(ruta)

        for advertencia in advertencias:
            print(f"  [!] {advertencia}")

        if afd_cargado is None:
            print("\n[ERROR] No fue posible construir el AFD a partir del archivo.")
            return

        self.afd_actual = afd_cargado
        self.simulador = Simulador()
        print(f"\n[OK] AFD '{afd_cargado.nombre}' cargado correctamente desde '{ruta}'.")

    def opcion_mostrar_quintupla(self) -> None:
        """Opción 3: Muestra la definición formal (quíntupla) del AFD activo."""
        if not self._hay_afd_cargado():
            return
        print("\n" + self.afd_actual.quintupla_formal())

    def opcion_mostrar_tabla(self) -> None:
        """Opción 4: Muestra la tabla de transición en formato matriz."""
        if not self._hay_afd_cargado():
            return
        print("\n" + self.afd_actual.tabla_transicion())

    def opcion_validar_estructura(self) -> None:
        """Opción 5: Ejecuta y muestra el reporte completo de validación estructural."""
        if not self._hay_afd_cargado():
            return
        print("\n" + self.afd_actual.generar_reporte_validacion())

        _, faltantes = self.afd_actual.verificar_determinismo()
        hay_incompletas = any("faltante" in r for r in faltantes)
        if hay_incompletas:
            resp = input("\n¿Desea completar el AFD con un estado trampa? (s/n): ").strip().lower()
            if resp == "s":
                trampa = self.afd_actual.completar_con_estado_trampa()
                if trampa:
                    print(f"[OK] Se agregó el estado trampa '{trampa}'. El AFD ahora es completo.")

    def opcion_evaluar_cadena(self) -> None:
        """Opción 6: Solicita una cadena y muestra su traza de evaluación paso a paso."""
        if not self._hay_afd_cargado():
            return
        try:
            cadena = input(
                "\nIngrese la cadena a evaluar (ENTER para cadena vacía ε): "
            )
        except (EOFError, KeyboardInterrupt):
            print("\n[!] Operación cancelada.")
            return
        self.simulador.evaluar_cadena(self.afd_actual, cadena, mostrar_traza=True)

    def opcion_evaluar_lote(self) -> None:
        """Opción 7: Evalúa un archivo de cadenas y muestra el reporte consolidado."""
        if not self._hay_afd_cargado():
            return
        try:
            ruta = input("\nRuta del archivo de cadenas a evaluar en lote: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[!] Operación cancelada.")
            return

        resultados, advertencias = self.simulador.evaluar_lote(self.afd_actual, ruta)
        for advertencia in advertencias:
            print(f"  [!] {advertencia}")

        print("\n" + self.simulador.generar_reporte_lote(resultados))

    def opcion_mostrar_historial(self) -> None:
        """Opción 8: Muestra el historial acumulado de evaluaciones de la sesión."""
        print("\n" + self.simulador.mostrar_historial())

    def opcion_cargar_otro(self) -> None:
        """Opción 9: Permite descartar el AFD actual y crear/cargar uno nuevo."""
        print("\n--- CARGAR O CREAR OTRO AUTÓMATA ---")
        print(" a) Crear manualmente")
        print(" b) Cargar desde archivo .txt")
        try:
            sub_opcion = input("Seleccione una sub-opción (a/b): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n[!] Operación cancelada.")
            return

        if sub_opcion == "a":
            self.opcion_crear_manual()
        elif sub_opcion == "b":
            self.opcion_cargar_desde_archivo()
        else:
            print("  [!] Sub-opción inválida. Regresando al menú principal.")

    # ------------------------------------------------------------------
    # BUCLE PRINCIPAL
    # ------------------------------------------------------------------
    def ejecutar(self) -> None:
        """Ejecuta el bucle principal del menú hasta que el usuario elige salir."""
        # Diccionario de despacho: mapea cada opción numérica a su método
        # correspondiente, evitando una larga cadena de if/elif.
        acciones = {
            "1": self.opcion_crear_manual,
            "2": self.opcion_cargar_desde_archivo,
            "3": self.opcion_mostrar_quintupla,
            "4": self.opcion_mostrar_tabla,
            "5": self.opcion_validar_estructura,
            "6": self.opcion_evaluar_cadena,
            "7": self.opcion_evaluar_lote,
            "8": self.opcion_mostrar_historial,
            "9": self.opcion_cargar_otro,
        }

        while True:
            self.imprimir_menu()
            try:
                opcion = input("Seleccione una opción (1-10): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nSaliendo del programa. ¡Hasta luego!")
                break

            if opcion == "10":
                print("\nSaliendo del programa. ¡Hasta luego!")
                break

            accion = acciones.get(opcion)
            if accion is None:
                print("\n[!] Opción inválida. Por favor, seleccione un número del 1 al 10.")
                continue

            # Cada acción está protegida individualmente: un error inesperado
            # en una opción no debe colapsar el bucle principal de la app.
            try:
                accion()
            except Exception as error:
                print(f"\n[ERROR INESPERADO] {error}")
                print("La aplicación continúa en ejecución.")


def main() -> None:
    """Función de entrada del programa."""
    try:
        app = AplicacionAFD()
        app.ejecutar()
    except Exception as error:
        # Red de seguridad de último nivel: ni siquiera un fallo catastrófico
        # debería producir un traceback sin control ante el usuario final.
        print(f"[ERROR FATAL] La aplicación se detuvo de forma inesperada: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
