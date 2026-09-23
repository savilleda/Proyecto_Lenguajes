from afnd import AFND


class ValidadorAutomata:
    EPSILON = {"", "epsilon", "eps", "ε", "landa", "λ", "lambda"}

    def errores(self, automata):
        """Incompletitud y no determinismo se clasifican aparte de invalidez."""
        errores = []
        if not automata.estados:
            errores.append("Q debe contener al menos un estado.")
        if automata.estado_inicial not in automata.estados:
            errores.append("El estado inicial no pertenece a Q.")
        if not automata.estados_finales <= automata.estados:
            errores.append("Existen estados finales fuera de Q.")
        for simbolo in sorted(automata.alfabeto):
            if simbolo.lower() in self.EPSILON:
                errores.append("Las transiciones epsilon no forman parte de esta fase.")
            elif len(simbolo) != 1 or simbolo.isspace() or simbolo in {",", "|", "∅"}:
                errores.append(f"Símbolo inválido {simbolo!r}: use un carácter, "
                               "sin espacios, coma, | ni ∅.")
        for (origen, simbolo), destino in automata.transiciones.items():
            destinos = destino if isinstance(automata, AFND) else {destino}
            if origen not in automata.estados:
                errores.append(f"Estado origen inexistente: {origen}.")
            if simbolo.lower() in self.EPSILON:
                errores.append(f"Transición epsilon en {origen}: fuera del alcance.")
            elif simbolo not in automata.alfabeto:
                errores.append(f"Símbolo inexistente: {simbolo}.")
            if not destinos <= automata.estados:
                errores.append(f"Destinos inexistentes desde {origen}: "
                               f"{sorted(destinos - automata.estados)}.")
        for destinos in getattr(automata, "transiciones_conflictivas", {}).values():
            if not destinos <= automata.estados:
                errores.append("Una transición múltiple contiene estados inexistentes.")
        return errores

    def clasificar(self, automata):
        if self.errores(automata):
            return "Definición inválida"
        if isinstance(automata, AFND):
            return "AFND válido (sin epsilon)"
        if getattr(automata, "transiciones_conflictivas", {}):
            return "Definición no determinista: cárguela como AFND"
        if not automata.verificar_determinismo()[0]:
            return "AFD incompleto"
        return "AFD válido y completo"

    def exigir_afd(self, automata, completo=True):
        """Impide simular o completar una definición estructuralmente inválida."""
        errores = self.errores(automata)
        if isinstance(automata, AFND):
            errores.append("Primero convierta el AFND a AFD.")
        if getattr(automata, "transiciones_conflictivas", {}):
            errores.append("La definición tiene varios destinos: cárguela como AFND.")
        if errores:
            raise ValueError("\n".join(errores))
        if completo and not automata.verificar_determinismo()[0]:
            raise ValueError("AFD incompleto: complete sus transiciones con la opción 6.")
