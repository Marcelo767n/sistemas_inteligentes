import tkinter as tk
import heapq
import random
from collections import deque

# Colores
COLORS = {
    "WALL": "black",
    "PATH": "white",
    "START": "green",
    "GOAL": "red",
    "ROUTE": "yellow",
}

# Tipos de celda
WALL = "WALL"
PATH = "PATH"
START = "START"
GOAL = "GOAL"
ROUTE = "ROUTE"

def generar_laberinto(filas=15, columnas=20, densidad=0.3):
    lab = [[WALL for _ in range(columnas)] for _ in range(filas)]
    def dfs(x, y):
        lab[y][x] = PATH
        dirs = [(0,-2),(2,0),(0,2),(-2,0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if 0<=nx<columnas and 0<=ny<filas and lab[ny][nx]==WALL:
                lab[y+dy//2][x+dx//2] = PATH
                dfs(nx, ny)
    start_x, start_y = random.randrange(0, columnas, 2), random.randrange(0, filas, 2)
    dfs(start_x, start_y)
    for y in range(filas):
        for x in range(columnas):
            if lab[y][x]==PATH and random.random()<densidad:
                lab[y][x]=WALL
    lab[0][0]=START
    lab[filas-1][columnas-1]=GOAL
    return lab

def encontrar(lab, tipo):
    for y,row in enumerate(lab):
        for x,val in enumerate(row):
            if val==tipo:
                return (y,x)
    return None

def vecinos(lab,pos):
    y,x = pos
    vec = []
    for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        ny,nx=y+dy,x+dx
        if 0<=ny<len(lab) and 0<=nx<len(lab[0]) and lab[ny][nx]!=WALL:
            vec.append((ny,nx))
    return vec

def bfs(lab,inicio,meta):
    cola = deque([inicio])
    visitados = {inicio: None}
    while cola:
        act = cola.popleft()
        if act==meta:
            break
        for v in vecinos(lab,act):
            if v not in visitados:
                visitados[v]=act
                cola.append(v)
    if meta not in visitados: return None
    cam=[]
    act=meta
    while act!=inicio:
        cam.append(act)
        act=visitados[act]
    cam.append(inicio)
    cam.reverse()
    return cam

def a_estrella(lab,inicio,meta):
    cola = [(0,inicio)]
    heapq.heapify(cola)
    g = {inicio:0}
    f = {inicio: abs(inicio[0]-meta[0])+abs(inicio[1]-meta[1])}
    prev = {}
    en_cola = {inicio}
    while cola:
        act = heapq.heappop(cola)[1]
        en_cola.remove(act)
        if act==meta:
            cam=[]
            while act in prev:
                cam.append(act)
                act=prev[act]
            cam.append(inicio)
            cam.reverse()
            return cam
        for v in vecinos(lab,act):
            g_t = g[act]+1
            if v not in g or g_t<g[v]:
                prev[v]=act
                g[v]=g_t
                f[v]=g_t+abs(v[0]-meta[0])+abs(v[1]-meta[1])
                if v not in en_cola:
                    heapq.heappush(cola,(f[v],v))
                    en_cola.add(v)
    return None

# ================== Tkinter sin clases ==================
def dibujar_laberinto(frame, laberinto, celdas, camino=[]):
    filas = len(laberinto)
    columnas = len(laberinto[0])
    for y in range(filas):
        for x in range(columnas):
            val = laberinto[y][x]
            color = COLORS[val]
            if (y,x) in camino and val not in [START,GOAL]:
                color = COLORS[ROUTE]
            if not celdas[y][x]:
                lbl = tk.Label(frame,width=2,height=1,bg=color,borderwidth=1,relief="solid")
                lbl.grid(row=y,column=x)
                celdas[y][x]=lbl
            else:
                celdas[y][x].config(bg=color)

def main():
    filas, columnas = 15, 20
    laberinto = generar_laberinto(filas, columnas)
    inicio = encontrar(laberinto, START)
    meta = encontrar(laberinto, GOAL)

    ventana = tk.Tk()
    ventana.title("Laberinto BFS / A*")
    frame = tk.Frame(ventana)
    frame.pack()
    celdas = [[None]*columnas for _ in range(filas)]

    def generar():
        nonlocal laberinto, inicio, meta
        laberinto = generar_laberinto(filas, columnas)
        inicio = encontrar(laberinto, START)
        meta = encontrar(laberinto, GOAL)
        dibujar_laberinto(frame, laberinto, celdas)

    def resolver_bfs():
        cam = bfs(laberinto, inicio, meta)
        if cam:
            dibujar_laberinto(frame, laberinto, celdas, cam)

    def resolver_astar():
        cam = a_estrella(laberinto, inicio, meta)
        if cam:
            dibujar_laberinto(frame, laberinto, celdas, cam)

    tk.Button(ventana,text="Generar Laberinto",command=generar).pack(side="left",padx=5,pady=5)
    tk.Button(ventana,text="Resolver BFS",command=resolver_bfs).pack(side="left",padx=5,pady=5)
    tk.Button(ventana,text="Resolver A*",command=resolver_astar).pack(side="left",padx=5,pady=5)

    dibujar_laberinto(frame, laberinto, celdas)
    ventana.mainloop()

if __name__=="__main__":
    main()