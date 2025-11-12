from dataclasses import dataclass
from typing import Any, Dict, List, Optional

#TABLA DE SÍMBOLOS
@dataclass
class Simbolo:
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
            print("(no hay variables definidas)")
        else:
            print(f"{'Nombre':<15} {'Tipo':<10} {'Valor':<15} {'Línea':<10}")
            for sym in self.simbolos.values():
                print(f"{sym.nombre:<15} {sym.tipo:<10} {str(sym.valor):<15} {sym.linea:<10}")


# 2. NODOS DEL AST (Árbol de Sintaxis Abstracta)
@dataclass
class NodoAST:
    tipo: str
    def evaluar(self, tabla: TablaSimbolos) -> Any:
        raise NotImplementedError
    
    def imprimir_arbol(self, prefijo="", es_ultimo=True, con_valores=True, tabla=None):
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
        
        extension = "    " if es_ultimo else "│   "
        self.izq.imprimir_arbol(prefijo + extension, False, con_valores, tabla)
        self.der.imprimir_arbol(prefijo + extension, True, con_valores, tabla)

@dataclass
class NodoAsignacion(NodoAST):
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
        
        extension = "    " if es_ultimo else "│   "
        self.expresion.imprimir_arbol(prefijo + extension, True, con_valores, tabla)


# 3. ANALIZADOR LÉXICO
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
            
            if char.isspace():
                if char == '\n':
                    self.linea += 1
                self.pos += 1
                continue
            
            if char.isdigit():
                self.tokens.append(self.leer_numero())
                continue
            
            if char.isalpha() or char == '_':
                self.tokens.append(self.leer_identificador())
                continue
            
            if char in '+-*/()=':
                self.tokens.append(Token(char, char, self.linea))
                self.pos += 1
                continue
            
            raise Exception(f"Carácter no reconocido: '{char}'")
        
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


# 4. ANALIZADOR SINTÁCTICO
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
    
    def sentencia(self) -> NodoAST:
        if self.token_actual.tipo == 'ID':
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].tipo == '=':
                nombre = self.token_actual.valor
                linea = self.token_actual.linea
                self.avanzar()
                self.coincidir('=')
                expr = self.E()
                return NodoAsignacion(nombre, expr, linea)
        
        return self.E()
    
    def E(self) -> NodoAST:
        nodo = self.T()
        return self.E_prima(nodo)
    
    def E_prima(self, izq: NodoAST) -> NodoAST:
        if self.token_actual.tipo in ['+', '-']:
            op = self.token_actual.tipo
            self.avanzar()
            der = self.T()
            nodo = NodoBinario(op, izq, der)
            return self.E_prima(nodo)
        return izq
    
    def T(self) -> NodoAST:
        nodo = self.F()
        return self.T_prima(nodo)
    
    def T_prima(self, izq: NodoAST) -> NodoAST:
        if self.token_actual.tipo in ['*', '/']:
            op = self.token_actual.tipo
            self.avanzar()
            der = self.F()
            nodo = NodoBinario(op, izq, der)
            return self.T_prima(nodo)
        return izq
    
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


# PROCESADOR EDTS 
def procesar_sentencia(expresion: str, tabla: TablaSimbolos):
     
    # PASO 1: Análisis Léxico
    print("\n[1] ANÁLISIS LÉXICO")
    lexico = AnalizadorLexico(expresion)
    tokens = lexico.tokenizar()
    for token in tokens:
        if token.tipo != 'EOF':
            print(f"  {token}")
    
    # PASO 2: Análisis Sintáctico
    sintactico = AnalizadorSintactico(tokens)
    ast = sintactico.sentencia()
    
    # PASO 3: AST sin decorar
    print("\nAST")
    ast.imprimir_arbol(con_valores=False, tabla=None)
    
    # PASO 4: Evaluación Semántica
    print("\n EVALUACIÓN SEMÁNTICA")
    resultado = ast.evaluar(tabla)
    print(f"Resultado= {resultado}")
    
    # PASO 5: AST Decorado
    print("\nAST DECORADO")
    ast.imprimir_arbol(con_valores=True, tabla=tabla)

    # PASO 6: Tabla de Símbolos
    tabla.imprimir()    
    return resultado

def main():
    tabla = TablaSimbolos()
    while True:
        try:
            # Solicitar entrada
            expresion = input(" > ").strip()          
            # Ignorar líneas vacías
            if not expresion:
                continue           
            # Procesar la sentencia
            procesar_sentencia(expresion, tabla)
            
        except Exception as e:
            print(f"\n ERROR: {e}")


if __name__ == "__main__":
    main()
