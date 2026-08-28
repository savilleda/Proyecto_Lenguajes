import os #Comprueba la existencia de archivos
import re #Expresiones regulares (hace el parsing del .txt)
import sys #Salida controlada del programa (sys.exist)
from typing import Dict, List, Optional, Set, Tuple # Solo anotaciones de tipo documentación

#Utilidad de colores en consola

class colores:
    """
    Tiene codigos de escapa ANSI que son utilizados para dar una visualización clara al usuario en la consola
    el verde es para marcar aceptación, rojo algún error, amarillo adventencia
    cian para menus.
    """
    RESET = "\033[0m"
    NEGRITA = "\033[1m"
    VERDE = "\033[92m"
    ROJO = "\033[91m"
    AMARILLO = "\033[93m"
    CIAN = "\033[96m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    GRIS = "\033[90m"
    @staticmethod
    def ok(texto: str) -> str:
        return f"{Colores.VERDE}{texto}{Colores.RESET}"
 
    @staticmethod
    def error(texto: str) -> str:
        return f"{Colores.ROJO}{texto}{Colores.RESET}"
 
    @staticmethod
    def advertencia(texto: str) -> str:
        return f"{Colores.AMARILLO}{texto}{Colores.RESET}"
 
    @staticmethod
    def titulo(texto: str) -> str:
        return f"{Colores.CIAN}{Colores.NEGRITA}{texto}{Colores.RESET}"
 
    @staticmethod
    def info(texto: str) -> str:
        return f"{Colores.AZUL}{texto}{Colores.RESET}"