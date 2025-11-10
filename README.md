# Implementación de un EDTS para una GIC que suma, resta, multiplica y divide.

## Desarrollo:

### Diseño de la gramática

    E → E₁ + T    
    E → E₁ - T  
    E → T
    
    T → T₁ * F  
    T → T₁ / F
    T → F 
    
    F → (E) 
    F → num 
    F → id

### Definir atributos

    - val: atributo sintetizado (valor calculado)
    - lexema: atributo sintetizado (identificador o número)

### Calcular los conjuntos: F,S,P,

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

### Generar el AST decorado(impreso por consola)

### Generar la tabla de símbolos (definir las estructuras)

### Generar la gramática de atributos

    E → E₁ + T    { E.val = E₁.val + T.val }
    E → E₁ - T    { E.val = E₁.val - T.val }
    E → T         { E.val = T.val }
    
    T → T₁ * F    { T.val = T₁.val * F.val }
    T → T₁ / F    { T.val = T₁.val / F.val }
    T → F         { T.val = F.val }
    
    F → (E)       { F.val = E.val }
    F → num       { F.val = num.lexval }
    F → id        { F.val = tabla[id.lexema] }

### Generar la ETDS.



    
## Casos de prueba



---
## Referencias 



