import heapq
import random
from collections import deque

# Configuración de caracteres para visualización
WALL = '▓▓'
PATH = '  '
START = '🚦'
GOAL = '🏁'
ROUTE = '··'
VISITED = '░░'

def generar_laberinto_aleatorio(filas=15, columnas=20, densidad_paredes=0.3):
    """
    Genera un laberinto aleatorio con las dimensiones especificadas.
    densidad_paredes: probabilidad de que una celda sea una pared (0-1)
    """
    # Inicializar todo como paredes
    laberinto = [[WALL for _ in range(columnas)] for _ in range(filas)]
    
    # Usar DFS aleatorio para crear caminos
    def dfs(x, y):
        laberinto[y][x] = PATH
        
        # Direcciones aleatorias: arriba, derecha, abajo, izquierda
        direcciones = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(direcciones)
        
        for dx, dy in direcciones:
            nx, ny = x + dx, y + dy
            if 0 <= nx < columnas and 0 <= ny < filas and laberinto[ny][nx] == WALL:
                # Derribar la pared entre la celda actual y la nueva
                laberinto[y + dy//2][x + dx//2] = PATH
                dfs(nx, ny)
    
    # Empezar desde una posición aleatoria (pero impar para que funcione con el método de derribar paredes)
    inicio_x, inicio_y = random.randrange(0, columnas, 2), random.randrange(0, filas, 2)
    dfs(inicio_x, inicio_y)
    
    # Añadir paredes adicionales según la densidad especificada
    for y in range(filas):
        for x in range(columnas):
            if laberinto[y][x] == PATH and random.random() < densidad_paredes:
                laberinto[y][x] = WALL
    
    # Asegurar que haya un inicio y una meta
    # Buscar una posición para el inicio (preferiblemente cerca de la esquina superior izquierda)
    inicio_encontrado = False
    for y in range(2):
        for x in range(2):
            if laberinto[y][x] == PATH:
                laberinto[y][x] = START
                inicio_encontrado = True
                break
        if inicio_encontrado:
            break
    
    # Si no encontró un camino cerca de la esquina, buscar en cualquier lugar
    if not inicio_encontrado:
        for y in range(filas):
            for x in range(columnas):
                if laberinto[y][x] == PATH:
                    laberinto[y][x] = START
                    inicio_encontrado = True
                    break
            if inicio_encontrado:
                break
    
    # Buscar una posición para la meta (preferiblemente lejos del inicio)
    meta_encontrada = False
    for y in range(filas-1, filas-3, -1):
        for x in range(columnas-1, columnas-3, -1):
            if laberinto[y][x] == PATH:
                laberinto[y][x] = GOAL
                meta_encontrada = True
                break
        if meta_encontrada:
            break
    
    # Si no encontró un camino cerca de la esquina, buscar en cualquier lugar
    if not meta_encontrada:
        for y in range(filas-1, -1, -1):
            for x in range(columnas-1, -1, -1):
                if laberinto[y][x] == PATH:
                    laberinto[y][x] = GOAL
                    meta_encontrada = True
                    break
            if meta_encontrada:
                break
    
    return laberinto

def imprimir_laberinto(laberinto, titulo=""):
    """Imprime el laberinto de forma visual"""
    if titulo:
        print(f"\n{titulo}")
        print("=" * (len(laberinto[0]) * 2))
    
    for fila in laberinto:
        print("".join(fila))
    
    if titulo:
        print("=" * (len(laberinto[0]) * 2))

def encontrar_posicion(laberinto, simbolo):
    """Encuentra la posición de un símbolo en el laberinto"""
    for i, fila in enumerate(laberinto):
        for j, celda in enumerate(fila):
            if celda == simbolo:
                return (i, j)
    return None

def obtener_vecinos(laberinto, posicion):
    """Obtiene los vecinos válidos de una posición"""
    fila, columna = posicion
    vecinos = []
    
    # Movimientos posibles: arriba, abajo, izquierda, derecha
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for df, dc in movimientos:
        nf, nc = fila + df, columna + dc
        # Verificar límites y que no sea pared
        if 0 <= nf < len(laberinto) and 0 <= nc < len(laberinto[0]) and laberinto[nf][nc] != WALL:
            vecinos.append((nf, nc))
            
    return vecinos

def distancia_manhattan(pos1, pos2):
    """Calcula la distancia de Manhattan entre dos posiciones"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def bfs(laberinto, inicio, meta):
    """Implementación de Breadth-First Search"""
    cola = deque([inicio])
    visitados = {inicio: None}  # Almacena nodo padre para reconstruir el camino
    laberinto_visual = [fila[:] for fila in laberinto]  # Copia para visualización
    
    print("Iniciando BFS...")
    pasos = 0
    
    while cola:
        actual = cola.popleft()
        pasos += 1
        
        # Visualización del proceso
        if laberinto_visual[actual[0]][actual[1]] not in [START, GOAL]:
            laberinto_visual[actual[0]][actual[1]] = VISITED
        
        if actual == meta:
            break  # Meta encontrada
        
        for vecino in obtener_vecinos(laberinto, actual):
            if vecino not in visitados:
                cola.append(vecino)
                visitados[vecino] = actual
    
    # Reconstruir el camino si se encontró la meta
    if meta not in visitados:
        print("BFS no encontró camino hacia la meta")
        return None, pasos
    
    camino = []
    actual = meta
    while actual != inicio:
        camino.append(actual)
        actual = visitados[actual]
    camino.append(inicio)
    camino.reverse()
    
    # Marcar el camino en la visualización
    for pos in camino[1:-1]:  # Excluir inicio y meta
        laberinto_visual[pos[0]][pos[1]] = ROUTE
    
    return camino, pasos

def a_estrella(laberinto, inicio, meta):
    """Implementación del algoritmo A*"""
    # Cola de prioridad: (f_score, node)
    cola_prioridad = [(0, inicio)]
    heapq.heapify(cola_prioridad)
    
    # Para cada nodo, almacena el nodo anterior en el camino óptimo
    procedencia = {}
    
    # g_score: costo desde el inicio hasta el nodo
    g_score = {inicio: 0}
    
    # f_score = g_score + heurística
    f_score = {inicio: distancia_manhattan(inicio, meta)}
    
    # Conjunto de nodos en la cola de prioridad
    en_cola = {inicio}
    
    laberinto_visual = [fila[:] for fila in laberinto]  # Copia para visualización
    print("Iniciando A*...")
    pasos = 0
    
    while cola_prioridad:
        # Obtener el nodo con menor f_score
        actual = heapq.heappop(cola_prioridad)[1]
        en_cola.remove(actual)
        pasos += 1
        
        # Visualización del proceso
        if laberinto_visual[actual[0]][actual[1]] not in [START, GOAL]:
            laberinto_visual[actual[0]][actual[1]] = VISITED
        
        if actual == meta:
            # Reconstruir camino
            camino = []
            while actual in procedencia:
                camino.append(actual)
                actual = procedencia[actual]
            camino.append(inicio)
            camino.reverse()
            
            # Marcar el camino en la visualización
            for pos in camino[1:-1]:  # Excluir inicio y meta
                laberinto_visual[pos[0]][pos[1]] = ROUTE
                
            return camino, pasos
        
        for vecino in obtener_vecinos(laberinto, actual):
            # Calcular g_score tentativo para el vecino
            g_tentativo = g_score[actual] + 1  # Costo uniforme de 1 por movimiento
            
            if vecino not in g_score or g_tentativo < g_score[vecino]:
                # Este camino es mejor que cualquier otro encontrado previamente
                procedencia[vecino] = actual
                g_score[vecino] = g_tentativo
                f_score[vecino] = g_tentativo + distancia_manhattan(vecino, meta)
                
                if vecino not in en_cola:
                    heapq.heappush(cola_prioridad, (f_score[vecino], vecino))
                    en_cola.add(vecino)
    
    print("A* no encontró camino hacia la meta")
    return None, pasos

def main():
    """Función principal"""
    # Crear laberinto aleatorio
    print("Generando laberinto aleatorio...")
    laberinto = generar_laberinto_aleatorio(15, 20, 0.3)
    imprimir_laberinto(laberinto, "Laberinto Aleatorio")
    
    # Encontrar inicio y meta
    inicio = encontrar_posicion(laberinto, START)
    meta = encontrar_posicion(laberinto, GOAL)
    
    if not inicio or not meta:
        print("Error: El laberinto debe tener un inicio (🚦) y una meta (🏁)")
        return
    
    print(f"Inicio: {inicio}, Meta: {meta}")
    
    # Resolver con BFS
    camino_bfs, pasos_bfs = bfs(laberinto, inicio, meta)
    if camino_bfs:
        laberinto_bfs = [fila[:] for fila in laberinto]  # Copia
        for pos in camino_bfs[1:-1]:  # Excluir inicio y meta
            laberinto_bfs[pos[0]][pos[1]] = ROUTE
        imprimir_laberinto(laberinto_bfs, f"BFS - Camino encontrado ({len(camino_bfs)-1} pasos, {pasos_bfs} nodos explorados)")
    
    # Resolver con A*
    camino_astar, pasos_astar = a_estrella(laberinto, inicio, meta)
    if camino_astar:
        laberinto_astar = [fila[:] for fila in laberinto]  # Copia
        for pos in camino_astar[1:-1]:  # Excluir inicio y meta
            laberinto_astar[pos[0]][pos[1]] = ROUTE
        imprimir_laberinto(laberinto_astar, f"A* - Camino encontrado ({len(camino_astar)-1} pasos, {pasos_astar} nodos explorados)")
    
    # Comparación
    if camino_bfs and camino_astar:
        print("\n" + "="*50)
        print("COMPARACIÓN:")
        print(f"BFS: {len(camino_bfs)-1} pasos en el camino, {pasos_bfs} nodos explorados")
        print(f"A*:  {len(camino_astar)-1} pasos en el camino, {pasos_astar} nodos explorados")
        
        if len(camino_bfs) == len(camino_astar):
            print("Ambos algoritmos encontraron caminos de la misma longitud")
        else:
            print("Diferencia en la longitud del camino:", abs(len(camino_bfs) - len(camino_astar)), "pasos")
            
        eficiencia = (pasos_bfs - pasos_astar) / pasos_bfs * 100
        print(f"A* fue {eficiencia:.1f}% más eficiente en la exploración de nodos")
    
    # Opción para generar otro laberinto
    respuesta = input("\n¿Generar otro laberinto? (s/n): ")
    if respuesta.lower() == 's':
        main()

if __name__ == "__main__":
    main()