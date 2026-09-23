
from afd import AFD
from afnd import AFND
from validador import ValidadorAutomata


class ConversorAFND:
    def __init__(self):
        self.equivalencias = {}

    def convertir(self, afnd):
        if not isinstance(afnd, AFND):
            raise ValueError("Debe cargar un AFND antes de convertir.")
        errores = ValidadorAutomata().errores(afnd)
        if errores:
            raise ValueError("\n".join(errores))
        # frozenset es un conjunto nativo inmutable. Sirve de clave sin importar
        # el orden: {q0,q1} y {q1,q0} representan el mismo macroestado.
        inicial = frozenset({afnd.estado_inicial})
        nombres = {inicial: "S0"}
        pendientes = [inicial]
        delta, finales, equivalencias = {}, set(), {}
        indice = 0
        simbolos = sorted(afnd.alfabeto)
        # La lista con índice funciona como cola sin el costo de pop(0).
        while indice < len(pendientes):
            conjunto = pendientes[indice]
            indice += 1
            nombre = nombres[conjunto]
            equivalencias[nombre] = conjunto
            if conjunto & afnd.estados_finales:
                finales.add(nombre)
            for simbolo in simbolos:
                union = set()
                for estado in conjunto:
                    union.update(afnd.destinos(estado, simbolo))
                destino = frozenset(union)
                if destino not in nombres:
                    nombres[destino] = f"S{len(nombres)}"
                    pendientes.append(destino)
                delta[(nombre, simbolo)] = nombres[destino]
                # Si destino es vacío, también se procesa: sus uniones vuelven
                # a ser vacías y quedan construidos todos sus bucles de trampa.
        resultado = AFD(afnd.nombre + "_AFD", set(nombres.values()),
                        set(afnd.alfabeto), delta, "S0", finales)
        self.equivalencias = equivalencias
        return resultado

    def tabla_equivalencias(self):
        if not self.equivalencias:
            return "Todavía no hay una conversión."
        lineas = ["MACROESTADO | ESTADOS DEL AFND"]
        for nombre, conjunto in self.equivalencias.items():
            lineas.append(f"{nombre:<11}| {AFND.mostrar_conjunto(conjunto)}")
        return "\n".join(lineas)
