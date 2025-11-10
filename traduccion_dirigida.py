# ESQUEMA DE TRADUCCIÓN DIRIGIDO POR LA SINTAXIS (EDTS)
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

"""
GRAMÁTICA DE ATRIBUTOS:

E → E₁ + T    { E.val = E₁.val + T.val }
E → E₁ - T    { E.val = E₁.val - T.val }
E → T         { E.val = T.val }

T → T₁ * F    { T.val = T₁.val * F.val }
T → T₁ / F    { T.val = T₁.val / F.val }
T → F         { T.val = F.val }

F → (E)       { F.val = E.val }
F → num       { F.val = num.lexval }
F → id        { F.val = tabla[id.lexema] }

ATRIBUTOS:
- val: atributo sintetizado (valor calculado)
- lexema: atributo sintetizado (identificador o número)
"""

# 2. TABLA DE SÍMBOLOS

@dataclass
class Simbolo:
    """Entrada en la tabla de símbolos"""
    nombre: str
    tipo: str
    valor: Any
    linea: int
    
class TablaSimbolos:
    def __init__(self):
        self.simbolos: Dict[str, Simbolo] = {}
    
    def insertar(self, nombre: str, tipo: str, valor: Any, linea: int):
        self.simbolos[nombre] = Simbolo(nombre, tipo, valor, linea)
    
    def buscar(self, nombre: str) -> Optional[Simbolo]:
        return self.simbolos.get(nombre)
    
    def actualizar(self, nombre: str, valor: Any):
        if nombre in self.simbolos:
            self.simbolos[nombre].valor = valor
    
    def imprimir(self):
        print("TABLA DE SÍMBOLOS")
        if not self.simbolos:
            print("(vacía - no hay variables definidas)")
        else:
            print(f"{'Nombre':<15} {'Tipo':<10} {'Valor':<15} {'Línea':<10}")
            for sym in self.simbolos.values():
                print(f"{sym.nombre:<15} {sym.tipo:<10} {str(sym.valor):<15} {sym.linea:<10}")

# 3. NODOS DEL AST (Árbol de Sintaxis Abstracta)
@dataclass
class NodoAST:
    """Clase base para nodos del AST"""
    tipo: str
    
    def evaluar(self, tabla: TablaSimbolos) -> Any:
        raise NotImplementedError
    
    def imprimir_arbol(self, prefijo="", es_ultimo=True, con_valores=True, tabla=None):
        """Imprime el árbol en formato visual ASCII"""
        raise NotImplementedError

@dataclass
class NodoNumero(NodoAST):
    """Nodo hoja: número"""
    valor: float
    
    def __init__(self, valor: float):
        super().__init__("numero")
        self.valor = valor
    
    def evaluar(self, tabla: TablaSimbolos) -> float:
        return self.valor
    
    def imprimir_arbol(self, prefijo="", es_ultimo=True, con_valores=True, tabla=None):
        conector = "└── " if es_ultimo else "├── "
        if con_valores:
            print(f"{prefijo}{conector}NUM: {self.valor} → val={self.valor}")
        else:
            print(f"{prefijo}{conector}NUM: {self.valor}")

@dataclass
class NodoVariable(NodoAST):
    """Nodo hoja: variable"""
    nombre: str
    linea: int
    
    def __init__(self, nombre: str, linea: int):
        super().__init__("variable")
        self.nombre = nombre
        self.linea = linea
    
    def evaluar(self, tabla: TablaSimbolos) -> float:
        sym = tabla.buscar(self.nombre)
        if sym is None:
            raise Exception(f"Variable '{self.nombre}' no definida (línea {self.linea})")
        return sym.valor
    
    def imprimir_arbol(self, prefijo="", es_ultimo=True, con_valores=True, tabla=None):
        conector = "└── " if es_ultimo else "├── "
        if con_valores and tabla:
            try:
                val = self.evaluar(tabla)
                print(f"{prefijo}{conector}VAR: {self.nombre} → val={val}")
            except:
                print(f"{prefijo}{conector}VAR: {self.nombre} → (no definida)")
        else:
            print(f"{prefijo}{conector}VAR: {self.nombre}")

@dataclass
class NodoBinario(NodoAST):
    """Nodo interno: operación binaria"""
    operador: str
    izq: NodoAST
    der: NodoAST
    
    def __init__(self, operador: str, izq: NodoAST, der: NodoAST):
        super().__init__("binario")
        self.operador = operador
        self.izq = izq
        self.der = der
    
    def evaluar(self, tabla: TablaSimbolos) -> float:
        val_izq = self.izq.evaluar(tabla)
        val_der = self.der.evaluar(tabla)
        
        if self.operador == '+':
            return val_izq + val_der
        elif self.operador == '-':
            return val_izq - val_der
        elif self.operador == '*':
            return val_izq * val_der
        elif self.operador == '/':
            if val_der == 0:
                raise Exception("División por cero")
            return val_izq / val_der
        else:
            raise Exception(f"Operador desconocido: {self.operador}")
    
    def imprimir_arbol(self, prefijo="", es_ultimo=True, con_valores=True, tabla=None):
        conector = "└── " if es_ultimo else "├── "
        if con_valores and tabla:
            try:
                val = self.evaluar(tabla)
                print(f"{prefijo}{conector}OP({self.operador}) → val={val}")
            except Exception as e:
                print(f"{prefijo}{conector}OP({self.operador}) → ERROR: {e}")
        else:
            print(f"{prefijo}{conector}OP({self.operador})")
        
        # Extensión del prefijo para los hijos
        extension = "    " if es_ultimo else "│   "
        
        # Imprimir hijo izquierdo
        self.izq.imprimir_arbol(prefijo + extension, False, con_valores, tabla)
        
        # Imprimir hijo derecho
        self.der.imprimir_arbol(prefijo + extension, True, con_valores, tabla)

@dataclass
class NodoAsignacion(NodoAST):
    """Nodo de asignación"""
    variable: str
    expresion: NodoAST
    linea: int
    
    def __init__(self, variable: str, expresion: NodoAST, linea: int):
        super().__init__("asignacion")
        self.variable = variable
        self.expresion = expresion
        self.linea = linea
    
    def evaluar(self, tabla: TablaSimbolos) -> float:
        valor = self.expresion.evaluar(tabla)
        tabla.insertar(self.variable, "float", valor, self.linea)
        return valor
    
    def imprimir_arbol(self, prefijo="", es_ultimo=True, con_valores=True, tabla=None):
        conector = "└── " if es_ultimo else "├── "
        if con_valores and tabla:
            try:
                val = self.evaluar(tabla)
                print(f"{prefijo}{conector}ASIG: {self.variable} → val={val}")
            except Exception as e:
                print(f"{prefijo}{conector}ASIG: {self.variable} → ERROR: {e}")
        else:
            print(f"{prefijo}{conector}ASIG: {self.variable}")
        
        # Extensión del prefijo para el hijo
        extension = "    " if es_ultimo else "│   "
        self.expresion.imprimir_arbol(prefijo + extension, True, con_valores, tabla)

# 4. ANALIZADOR LÉXICO

class Token:
    def __init__(self, tipo: str, valor: Any, linea: int):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
    
    def __repr__(self):
        return f"Token({self.tipo}, {self.valor}, L{self.linea})"

class AnalizadorLexico:
    def __init__(self, texto: str):
        self.texto = texto
        self.pos = 0
        self.linea = 1
        self.tokens = []
    
    def tokenizar(self) -> List[Token]:
        while self.pos < len(self.texto):
            char = self.texto[self.pos]
            
            # Espacios en blanco
            if char.isspace():
                if char == '\n':
                    self.linea += 1
                self.pos += 1
                continue
            
            # Números
            if char.isdigit():
                self.tokens.append(self.leer_numero())
                continue
            
            # Identificadores
            if char.isalpha() or char == '_':
                self.tokens.append(self.leer_identificador())
                continue
            
            # Operadores y símbolos
            if char in '+-*/()=':
                self.tokens.append(Token(char, char, self.linea))
                self.pos += 1
                continue
            
            raise Exception(f"Carácter no reconocido: '{char}' (línea {self.linea})")
        
        self.tokens.append(Token('EOF', None, self.linea))
        return self.tokens
    
    def leer_numero(self) -> Token:
        inicio = self.pos
        while self.pos < len(self.texto) and (self.texto[self.pos].isdigit() or self.texto[self.pos] == '.'):
            self.pos += 1
        valor = float(self.texto[inicio:self.pos])
        return Token('NUM', valor, self.linea)
    
    def leer_identificador(self) -> Token:
        inicio = self.pos
        while self.pos < len(self.texto) and (self.texto[self.pos].isalnum() or self.texto[self.pos] == '_'):
            self.pos += 1
        valor = self.texto[inicio:self.pos]
        return Token('ID', valor, self.linea)

# 5. ANALIZADOR SINTÁCTICO CON ACCIONES SEMÁNTICAS

class AnalizadorSintactico:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.token_actual = tokens[0]
    
    def avanzar(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_actual = self.tokens[self.pos]
    
    def coincidir(self, tipo: str):
        if self.token_actual.tipo == tipo:
            token = self.token_actual
            self.avanzar()
            return token
        else:
            raise Exception(f"Se esperaba '{tipo}', se encontró '{self.token_actual.tipo}' (línea {self.token_actual.linea})")
    
    # Programa → Sentencia | Sentencia Programa
    def programa(self) -> List[NodoAST]:
        sentencias = []
        while self.token_actual.tipo != 'EOF':
            sentencias.append(self.sentencia())
        return sentencias
    
    # Sentencia → ID = E | E
    def sentencia(self) -> NodoAST:
        if self.token_actual.tipo == 'ID':
            # Mirar adelante para ver si es asignación
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].tipo == '=':
                nombre = self.token_actual.valor
                linea = self.token_actual.linea
                self.avanzar()  # ID
                self.coincidir('=')
                expr = self.E()
                return NodoAsignacion(nombre, expr, linea)
        
        return self.E()
    
    # E → T E'
    def E(self) -> NodoAST:
        nodo = self.T()
        return self.E_prima(nodo)
    
    # E' → + T E' | - T E' | ε
    def E_prima(self, izq: NodoAST) -> NodoAST:
        if self.token_actual.tipo in ['+', '-']:
            op = self.token_actual.tipo
            self.avanzar()
            der = self.T()
            nodo = NodoBinario(op, izq, der)
            return self.E_prima(nodo)
        return izq
    
    # T → F T'
    def T(self) -> NodoAST:
        nodo = self.F()
        return self.T_prima(nodo)
    
    # T' → * F T' | / F T' | ε
    def T_prima(self, izq: NodoAST) -> NodoAST:
        if self.token_actual.tipo in ['*', '/']:
            op = self.token_actual.tipo
            self.avanzar()
            der = self.F()
            nodo = NodoBinario(op, izq, der)
            return self.T_prima(nodo)
        return izq
    
    # F → (E) | NUM | ID
    def F(self) -> NodoAST:
        if self.token_actual.tipo == '(':
            self.avanzar()
            nodo = self.E()
            self.coincidir(')')
            return nodo
        elif self.token_actual.tipo == 'NUM':
            valor = self.token_actual.valor
            self.avanzar()
            return NodoNumero(valor)
        elif self.token_actual.tipo == 'ID':
            nombre = self.token_actual.valor
            linea = self.token_actual.linea
            self.avanzar()
            return NodoVariable(nombre, linea)
        else:
            raise Exception(f"Factor inválido: {self.token_actual.tipo} (línea {self.token_actual.linea})")

# 6. CONJUNTOS PRIMEROS, SIGUIENTES Y PRODUCCIONES

PRIMEROS = {
    'E': {'(', 'NUM', 'ID'},
    "E'": {'+', '-', 'ε'},
    'T': {'(', 'NUM', 'ID'},
    "T'": {'*', '/', 'ε'},
    'F': {'(', 'NUM', 'ID'}
}
SIGUIENTES = {
    'E': {')', 'EOF', '$'},
    "E'": {')', 'EOF', '$'},
    'T': {'+', '-', ')', 'EOF', '$'},
    "T'": {'+', '-', ')', 'EOF', '$'},
    'F': {'+', '-', '*', '/', ')', 'EOF', '$'}
}
PRODUCCIONES = {
    'E': [['T', "E'"]],
    "E'": [['+', 'T', "E'"], ['-', 'T', "E'"], ['ε']],
    'T': [['F', "T'"]],
    "T'": [['*', 'F', "T'"], ['/', 'F', "T'"], ['ε']],
    'F': [['(', 'E', ')'], ['NUM'], ['ID']]
} 

# 7. PROGRAMA PRINCIPAL
def main():

    # Entrada del usuario
    print("\nIngrese expresiones (línea vacía para terminar):")
    
    lineas = []
    while True:
        linea = input("> ")
        if not linea.strip():
            break
        lineas.append(linea)
    
    codigo = '\n'.join(lineas)
    
    if not codigo.strip():
        print("No se ingresó código.")
        return
    
    try:
        # Análisis léxico
        print("TOKENS GENERADOS")
        lexico = AnalizadorLexico(codigo)
        tokens = lexico.tokenizar()
        for token in tokens:
            if token.tipo != 'EOF':
                print(f"  {token}")
        
        # Análisis sintáctico y construcción del AST
        print("AST (Árbol de Sintaxis Abstracta)")
        sintactico = AnalizadorSintactico(tokens)
        sentencias = sintactico.programa()
        
        # Imprimir árbol sin valores (estructura sintáctica)
        if len(sentencias) == 1:
            print("\nEstructura del árbol:")
            sentencias[0].imprimir_arbol(con_valores=False)
        else:
            print("\nEstructura del árbol:")
            print("PROGRAMA")
            for i, ast in enumerate(sentencias, 1):
                print(f"├── Sentencia {i}:")
                ast.imprimir_arbol("│   ", i == len(sentencias), con_valores=False)
        
        # Evaluación semántica
        print("EVALUACIÓN SEMÁNTICA")
        tabla = TablaSimbolos()
        
        resultados = []
        for i, ast in enumerate(sentencias, 1):
            try:
                resultado = ast.evaluar(tabla)
                resultados.append(resultado)
                print(f"Sentencia {i}: {resultado}")
            except Exception as e:
                resultados.append(None)
                print(f"Sentencia {i}: ERROR - {e}")
        
        # AST Decorado (con valores calculados)
        print("AST DECORADO (con atributos sintetizados)")
        
        if len(sentencias) == 1:
            print("\nÁrbol decorado con valores:")
            sentencias[0].imprimir_arbol(con_valores=True, tabla=tabla)
        else:
            print("\nÁrbol decorado con valores:")
            print("PROGRAMA")
            for i, ast in enumerate(sentencias, 1):
                print(f"├── Sentencia {i} (resultado={resultados[i-1]}):")
                ast.imprimir_arbol("│   ", i == len(sentencias), con_valores=True, tabla=tabla)
        
        # Tabla de símbolos final
        tabla.imprimir()
        
        print("\n Análisis completado exitosamente")
        
    except Exception as e:
        print(f"\n ERROR: {e}")

if __name__ == "__main__":
    main()