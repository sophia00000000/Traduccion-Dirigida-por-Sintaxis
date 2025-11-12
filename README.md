# Implementación de un EDTS para una GIC que suma, resta, multiplica y divide.

## Como ejecutar:

    python3 traduccion_dirigida.py 


### Diseño de la gramática GIC

        E  → T E'
        E' → + T E' | - T E' | ε
        T  → F T'
        T' → * F T' | / F T' | ε
        F  → (E) | num | id

Precedencia: () > * / > + -

### Definir atributos

| Atributo | Tipo | Descripción |
| :--- | :--- | :--- |
| **.val** | Sintetizado | Valor numérico calculado (float) |
| **.nodo** | Sintetizado | Nodo del AST construido |
| **.nombre** | Sintetizado | Nombre de variable (string) |
| **.izq** | Heredado | Valor acumulado en recursión |
| **.nodo_izq** | Heredado | Nodo acumulado en recursión |


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


    
## Casos de prueba
- 5+8-7 = 6 
- Resultado obtenido = 6

<img width="358" height="452" alt="imagen" src="https://github.com/user-attachments/assets/a395eadf-7880-4700-8c98-925c736362db" />

---

- 7+8-57/0+(2-4) = error
- Resultado obtenido =  ERROR: División por cero

<img width="268" height="531" alt="imagen" src="https://github.com/user-attachments/assets/951d3927-58eb-4e9a-9b06-b0ad9c41d73e" />

---

-  7-(2+4)*6+3 = -26
- Resultado obtenido = -26

<img width="259" height="537" alt="imagen" src="https://github.com/user-attachments/assets/4d175d94-61e3-4f4a-a24f-a7eee7cde1f0" />

---
- X = 1.25
- Y = 2.5
- 3-X+(Y*2) = 6.75
- Resultado obtenido = 6.75

<img width="217" height="492" alt="imagen" src="https://github.com/user-attachments/assets/67d1dc5a-53cc-4529-9e18-0509379fbd76" />


---
## Referencias 



