"""Modelo AFND sin transiciones epsilon. Cada destino es un conjunto"""


class AFND:
    def __init__(self, nombre, estados, alfabeto, transiciones,
                 estado_inicial, estados_finales):
        self.nombre = nombre
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        # Copiamos también los conjuntos interiores para no compartir cambios
        self.transiciones = {clave: set(destinos)
                             for clave, destinos in transiciones.items()}
        self.estado_inicial = estado_inicial
        self.estados_finales = set(estados_finales)

    def destinos(self, estado, simbolo):
        """Una transición omitida equivale al conjunto vacío, no a epsilon"""
        return self.transiciones.get((estado, simbolo), set())

    @staticmethod
    def mostrar_conjunto(estados):
        return "{" + ", ".join(sorted(estados)) + "}" if estados else "∅"

    def quintupla_formal(self):
        conjunto = self.mostrar_conjunto
        lineas = [f"AFND: {self.nombre}", f"Q = {conjunto(self.estados)}",
                  f"Sigma = {conjunto(self.alfabeto)}",
                  f"q0 = {self.estado_inicial}",
                  f"F = {conjunto(self.estados_finales)}", "delta:"]
        for estado in sorted(self.estados):
            for simbolo in sorted(self.alfabeto):
                lineas.append(f"  delta({estado}, {simbolo}) = "
                              + conjunto(self.destinos(estado, simbolo)))
        return "\n".join(lineas)

    def tabla_transicion(self):
        simbolos = sorted(self.alfabeto)
        filas = [["ESTADO"] + simbolos]
        for estado in sorted(self.estados):
            marca = "->" if estado == self.estado_inicial else ""
            marca += "*" if estado in self.estados_finales else ""
            filas.append([marca + estado] + [self.mostrar_conjunto(
                self.destinos(estado, simbolo)) for simbolo in simbolos])
        anchos = [max(len(fila[i]) for fila in filas)
                  for i in range(len(filas[0]))]
        return "\n".join(" | ".join(celda.ljust(anchos[i])
                                   for i, celda in enumerate(fila))
                         for fila in filas) + "\n-> inicial; * final; ∅ sin destinos"