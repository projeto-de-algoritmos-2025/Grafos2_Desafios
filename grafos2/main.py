import pygame
from pyamaze import maze
from collections import deque

# --- Configurações do jogo ---
TAM_CELULA = 40
FPS = 60
COR_PAREDE = (0, 0, 0)
COR_CAMINHO = (223, 234, 252)
COR_JOGADOR = (77, 63, 78)
COR_OBJETIVO = (0, 200, 0)
COR_TEXTO = (0, 0, 0)
COR_BOTAO = (200, 50, 50)
COR_TEXTO_BOTAO = (255, 255, 255)
COR_CAMINHO_BFS = (36, 225, 89)  

# Inicializar pygame
pygame.init()
fonte = pygame.font.SysFont(None, 30)
fonte_vitoria = pygame.font.SysFont(None, 40)
fonte_popup = pygame.font.SysFont(None, 36)

def inicializar_jogo():
    global m, mapa, pos_linha, pos_coluna, passos, venceu, largura_tela, altura_tela, tela, caminho_bfs, passos_bfs
    
    # Gerar o labirinto
    m = maze(10, 10)
    m.CreateMaze()
    mapa = m.maze_map

    # Configurações da tela
    largura_tela = m.cols * TAM_CELULA
    altura_tela = m.rows * TAM_CELULA + 55  # Espaço extra para o contador e botão
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    pygame.display.set_caption("Labirinto - Chegue ao objetivo")

    # Posição inicial e contador
    pos_linha = m.rows
    pos_coluna = m.cols
    passos = 0
    venceu = False
    
    # Calcular caminho BFS
    caminho_bfs, passos_bfs = calcular_bfs()
    mostrar_bfs = False

# Algoritmo BFS para encontrar o caminho mais curto
def calcular_bfs():
    # Início (canto inferior direito) e objetivo (canto superior esquerdo)
    inicio = (m.rows, m.cols)
    objetivo = (1, 1)
    
    fila = deque()
    fila.append((inicio, [inicio]))
    visitados = set()
    visitados.add(inicio)
    
    while fila:
        (linha, coluna), caminho = fila.popleft()
        
        # Verificar se chegou ao objetivo
        if (linha, coluna) == objetivo:
            return caminho, len(caminho) - 1  # Número de passos é o tamanho do caminho - 1
        
        # Explorar vizinhos (N, S, E, W)
        for direcao in ['N', 'S', 'E', 'W']:
            if mapa[(linha, coluna)][direcao] == 1:
                if direcao == 'N' and linha > 1:
                    vizinho = (linha - 1, coluna)
                elif direcao == 'S' and linha < m.rows:
                    vizinho = (linha + 1, coluna)
                elif direcao == 'E' and coluna < m.cols:
                    vizinho = (linha, coluna + 1)
                elif direcao == 'W' and coluna > 1:
                    vizinho = (linha, coluna - 1)
                else:
                    continue
                
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append((vizinho, caminho + [vizinho]))
    
    return [], 0  # Caso não encontre caminho (teoricamente impossível neste labirinto)

# Inicializar o jogo pela primeira vez
inicializar_jogo()

def desenhar_labirinto():
    for linha in range(1, m.rows+1):
        for coluna in range(1, m.cols+1):
            celula = mapa[(linha, coluna)]
            x = (coluna - 1) * TAM_CELULA
            y = (linha - 1) * TAM_CELULA

            pygame.draw.rect(tela, COR_CAMINHO, (x, y, TAM_CELULA, TAM_CELULA))

            if celula['N'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x, y), (x + TAM_CELULA, y), 3)
            if celula['S'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x, y + TAM_CELULA), (x + TAM_CELULA, y + TAM_CELULA), 3)
            if celula['W'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x, y), (x, y + TAM_CELULA), 3)
            if celula['E'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x + TAM_CELULA, y), (x + TAM_CELULA, y + TAM_CELULA), 3)

    # Desenhar objetivo (canto superior esquerdo)
    obj_x = 0 + TAM_CELULA // 4
    obj_y = 0 + TAM_CELULA // 4
    pygame.draw.rect(tela, COR_OBJETIVO, (obj_x, obj_y, TAM_CELULA // 2, TAM_CELULA // 2))

def desenhar_caminho_bfs():
    for i, (linha, coluna) in enumerate(caminho_bfs):
        x = (coluna - 1) * TAM_CELULA + TAM_CELULA // 4
        y = (linha - 1) * TAM_CELULA + TAM_CELULA // 4
        pygame.draw.rect(tela, COR_CAMINHO_BFS, (x, y, TAM_CELULA // 2, TAM_CELULA // 2))

def desenhar_controles():
    # Desenhar contador de passos
    texto_passos = fonte.render(f"Seus passos: {passos} | Melhor: {passos_bfs}", True, COR_TEXTO)
    tela.blit(texto_passos, (10, m.rows * TAM_CELULA + 10))
    
    # Desenhar botão de reiniciar
    botao_reiniciar = pygame.Rect(largura_tela - 120, m.rows * TAM_CELULA + 10, 110, 30)
    pygame.draw.rect(tela, COR_BOTAO, botao_reiniciar, border_radius=5)
    texto_botao = fonte.render("Reiniciar", True, COR_TEXTO_BOTAO)
    tela.blit(texto_botao, (largura_tela - 110, m.rows * TAM_CELULA + 15))
    
    # Botão para mostrar/ocultar caminho BFS
    botao_bfs = pygame.Rect(largura_tela - 320, m.rows * TAM_CELULA + 10, 180, 30)
    pygame.draw.rect(tela, (50, 150, 50), botao_bfs, border_radius=5)
    texto_bfs = fonte.render("Melhor Caminho", True, COR_TEXTO_BOTAO)
    tela.blit(texto_bfs, (largura_tela - 310, m.rows * TAM_CELULA + 15))
    
    return botao_reiniciar, botao_bfs

def mostrar_popup_vitoria():
    # Desenhar fundo semi-transparente
    s = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))  # Preto com transparência
    tela.blit(s, (0, 0))
    
    # Desenhar caixa do popup
    popup_rect = pygame.Rect(largura_tela//2 - 200, altura_tela//2 - 100, 400, 200)
    pygame.draw.rect(tela, (240, 240, 240), popup_rect, border_radius=10)
    pygame.draw.rect(tela, (0, 150, 0), popup_rect, 3, border_radius=10)
    
    # Texto do popup
    texto_vitoria = fonte_popup.render("Você venceu o labirinto!", True, (0, 100, 0))
    tela.blit(texto_vitoria, (popup_rect.centerx - texto_vitoria.get_width()//2, popup_rect.y + 30))
    
    texto_passos = fonte_vitoria.render(f"Seus passos: {passos}", True, COR_TEXTO)
    tela.blit(texto_passos, (popup_rect.centerx - texto_passos.get_width()//2, popup_rect.y + 70))
    
    texto_melhor = fonte_vitoria.render(f"Melhor possível: {passos_bfs}", True, COR_TEXTO)
    tela.blit(texto_melhor, (popup_rect.centerx - texto_melhor.get_width()//2, popup_rect.y + 110))
    
    # Botão OK
    botao_ok = pygame.Rect(popup_rect.centerx - 50, popup_rect.y + 150, 100, 35)
    pygame.draw.rect(tela, (50, 150, 50), botao_ok, border_radius=5)
    texto_ok = fonte.render("OK", True, COR_TEXTO_BOTAO)
    tela.blit(texto_ok, (popup_rect.centerx - texto_ok.get_width()//2, popup_rect.y + 157))
    
    pygame.display.flip()
    
    # Esperar clique no botão OK
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_ok.collidepoint(evento.pos):
                    esperando = False

# Loop principal
rodando = True
relogio = pygame.time.Clock()
mostrar_bfs = False

while rodando:
    tela.fill(COR_PAREDE)
    desenhar_labirinto()
    
    if mostrar_bfs:
        desenhar_caminho_bfs()
    
    botao_reiniciar, botao_bfs = desenhar_controles()

    # Jogador
    jogador_x = (pos_coluna - 1) * TAM_CELULA + TAM_CELULA // 4
    jogador_y = (pos_linha - 1) * TAM_CELULA + TAM_CELULA // 4
    pygame.draw.rect(tela, COR_JOGADOR, (jogador_x, jogador_y, TAM_CELULA // 2, TAM_CELULA // 2))

    pygame.display.flip()
    relogio.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if botao_reiniciar.collidepoint(evento.pos):
                inicializar_jogo()
                mostrar_bfs = False
            elif botao_bfs.collidepoint(evento.pos):
                mostrar_bfs = not mostrar_bfs

        if evento.type == pygame.KEYDOWN and not venceu:
            celula_atual = mapa[(pos_linha, pos_coluna)]

            if evento.key == pygame.K_UP and celula_atual['N'] == 1:
                pos_linha -= 1
                passos += 1
            elif evento.key == pygame.K_DOWN and celula_atual['S'] == 1:
                pos_linha += 1
                passos += 1
            elif evento.key == pygame.K_LEFT and celula_atual['W'] == 1:
                pos_coluna -= 1
                passos += 1
            elif evento.key == pygame.K_RIGHT and celula_atual['E'] == 1:
                pos_coluna += 1
                passos += 1

            # Verificar vitória
            if pos_linha == 1 and pos_coluna == 1:
                venceu = True
                mostrar_popup_vitoria()
                venceu = False  # Resetar após fechar o popup
                inicializar_jogo()

pygame.quit()