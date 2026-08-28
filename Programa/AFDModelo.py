class AFDModelo:
    """
     Representa la forma M = (Q, Σ, δ, q0, F)
 
    Estructuras de datos utilizadas:
        - Q      : set[str]                       -> conjunto de estados
        - sigma  : set[str]                       -> alfabeto (conjunto de símbolos)
        - delta  : Dict[Tuple[str, str], str]     -> función de transición
        - q0     : str                            -> estado inicial
        - F      : set[str]                       -> estados de aceptación
 
    Usar set para Q, Σ y F evita automáticamente elementos duplicados
    """
    def __init__(self, nombre: str = "AFD_SIN_NOMBRE"):
        # init se utiliza como un constructor cuando alguien pone el nombre de la clase para llamarla
        # El parametro que tiene es por defecto, por lo que si se crea un objeto es opcional el nombre
        self.nombre: str = nombre #Es un texto
        self.Q: Set[str] = set() # Representa el conjunto de estados 
        self.sigma: Set[str] = set() # Representa el alfabeto Σ
        #Evita la sobreescritura de la función de transición, ya que es un diccionario que mapea pares (estado, símbolo) a un estado
        self.delta: Dict[Tuple[str, str], str] = {} # Representa la función de transición δ
        self.q0 : Optional[str] = None # Es el estado inicial y todavía no se ha definido
        self.F: Set[str] = set() #Son los estados de aceptación que tiene

    #Estos metodos se utilizan para construir el AFD
    #ya que todos reciben self, por lo que necesitan leer/modificar los datos del objeto
    #self es una referencia al objeto actual, y permite acceder a sus atributos y métodos
    # por ejemplo, self.Q hace referencia al conjunto de estados del AFD actual

    def agregar_estado(self, estado: str) -> None:
        """
        Se agrega un estado a Q por medio de set.add sin duplicados
        y si este el estado ya estaba no pasa nada ya que los sets no repiten valores
        """
        self.Q.add(estado)

    def agregar_simbolo(self, simbolo: str) -> None:
        """
        Agrega un símbolo a Σ, y gracias al set.add se evitan duplicados
        """
        self.sigma.add(simbolo)

    def agregar_transicion(self, estado_origen: str, simbolo: str, estado_destino: str) -> None:
        """
        Registra la transición como su origen y símbolo, si ya existía una transición para el mismo par (origen, símbolo)
        Se acumula en la lista en lugar de sobrescribirla
        De forma que el AFDValidator puede detectar las múltiples transiciones múltiples
        """
        clave = (origen, simbolo) #La clave es una tupla, y en phyton las tuplas se pueden usar como llave en un diccionario
        # sí clave no existe todavía en self.delta. se crea con una lista vacía [], luego en cualquier caso, se devuelve la lista
        #Y para terminar con append se agrega el nuevo destino a esa lista
        self.delta.setdefault(clave, []).append(destino)

    def establecer_inicial(self, estado: str) -> None:
        self.q0 = estado

    def agregar_final(self, estado: str) -> None:
        self.F.add(estado)

    def delta_simple(self) -> Dict[Tuple[str, str], str]:
        """
        Devuelve una versión simplificada de delta
        donde cada par (estado, símbolo) se mapea a un único estado de destino
        se toma el primer destino registrado para cada par, se utiliza en la simulación
        una vez que el automata es validado como determinista
        """
        #Construye un nuevo diccionario donde se reccore self.delta.items() que son los pares clave-valor
        #Para cada uno se queda con destinos[0], lo que equivale al primer elemento de la lista.
        #el if destinos al final lo que es es descartar cualquier entrada cuya lista este vacía
        return{clave: destinos[0] for clave, destinos in self.delta.items().items() if destinos}
    
