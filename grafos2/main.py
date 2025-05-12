import sys
import pygame
from pyamaze import maze
import heapq

# --- Configurações do jogo ---
TAM_CELULA = 30
FPS = 60
COR_PAREDE = (0, 0, 0)
COR_CAMINHO = (223, 234, 252)
COR_JOGADOR = (77, 63, 78)
COR_OBJETIVO = (0, 200, 0)
COR_TEXTO = (0, 0, 0)
COR_BOTAO = (200, 50, 50)
COR_TEXTO_BOTAO = (255, 255, 255)
COR_CAMINHO_DJK = (36, 225, 89)
COR_VISITADO = (200, 220, 255)

pygame.init()
fonte = pygame.font.SysFont(None, 30)
fonte_vitoria = pygame.font.SysFont(None, 40)
fonte_popup = pygame.font.SysFont(None, 36)


def inicializar_jogo():
    global m, mapa, pos_linha, pos_coluna, passos, venceu, largura_tela, altura_tela, tela, caminho_djk, passos_djk, visitados_djk
    
    # Gerar o labirinto
    m = maze(m_linhas, m_colunas) # jogador agora pode escolher a dificulade do lab 2.0
    m.CreateMaze()
    mapa = m.maze_map

    # Configurações da tela
    largura_tela = m.cols * TAM_CELULA
    altura_tela = m.rows * TAM_CELULA + 55
    tela = pygame.display.set_mode((largura_tela, altura_tela))
    pygame.display.set_caption("Labirinto - Chegue ao objetivo")

    pos_linha = m.rows
    pos_coluna = m.cols
    passos = 0
    venceu = False

    # Calcular caminho com Dijkstra
    caminho_djk, passos_djk, visitados_djk = calcular_dijkstra()
    mostrar_djk = False

def calcular_dijkstra():
    inicio = (m.rows, m.cols)
    objetivo = (1, 1)

    distancias = {cell: float('inf') for cell in mapa}
    distancias[inicio] = 0
    predecessores = {}
    visitados = set()
    fila = [(0, inicio)]

    while fila:
        distancia_atual, atual = heapq.heappop(fila)
        visitados.add(atual)

        if atual == objetivo:
            break

        linha, coluna = atual
        for direcao in ['N', 'S', 'E', 'W']:
            if mapa[(linha, coluna)][direcao] == 1:
                if direcao == 'N':
                    vizinho = (linha - 1, coluna)
                elif direcao == 'S':
                    vizinho = (linha + 1, coluna)
                elif direcao == 'E':
                    vizinho = (linha, coluna + 1)
                elif direcao == 'W':
                    vizinho = (linha, coluna - 1)
                else:
                    continue

                if distancias[vizinho] > distancia_atual + 1:
                    distancias[vizinho] = distancia_atual + 1
                    predecessores[vizinho] = atual
                    heapq.heappush(fila, (distancias[vizinho], vizinho))

    caminho = []
    atual = objetivo
    while atual in predecessores or atual == inicio:
        caminho.append(atual)
        if atual == inicio:
            break
        atual = predecessores[atual]
    caminho.reverse()
    return caminho, len(caminho) - 1, visitados

def escolher_dificuldade(): # função para o jogador escolher a dificuldade 
    global m_linhas, m_colunas

    tela_temp = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Escolha a dificuldade")
    relogio = pygame.time.Clock()
    escolhendo = True

    while escolhendo:
        tela_temp.fill((30, 30, 30))

        titulo = fonte_popup.render("Escolha a dificuldade:", True, (255, 255, 255))
        tela_temp.blit(titulo, (400//2 - titulo.get_width()//2, 40))

        botoes = {
            "Fácil (10x10)": pygame.Rect(120, 90, 160, 40),
            "Médio (15x15)": pygame.Rect(120, 150, 160, 40),
            "Difícil (20x20)": pygame.Rect(120, 210, 160, 40),
        }

        for texto, ret in botoes.items():
            pygame.draw.rect(tela_temp, (70, 130, 180), ret, border_radius=8)
            txt = fonte.render(texto, True, (255, 255, 255))
            tela_temp.blit(txt, (ret.centerx - txt.get_width()//2, ret.centery - txt.get_height()//2))

        pygame.display.flip()
        relogio.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                for texto, ret in botoes.items():
                    if ret.collidepoint(evento.pos):
                        if "Fácil" in texto:
                            m_linhas, m_colunas = 10, 10
                        elif "Médio" in texto:
                            m_linhas, m_colunas = 15, 15
                        elif "Difícil" in texto:
                            m_linhas, m_colunas = 20, 20
                        escolhendo = False

escolher_dificuldade()
inicializar_jogo()

def desenhar_labirinto():
    for linha in range(1, m.rows + 1):
        for coluna in range(1, m.cols + 1):
            celula = mapa[(linha, coluna)]
            x = (coluna - 1) * TAM_CELULA
            y = (linha - 1) * TAM_CELULA

            pygame.draw.rect(tela, COR_CAMINHO, (x, y, TAM_CELULA, TAM_CELULA))

            if celula['N'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x, y), (x + TAM_CELULA, y), 2)
            if celula['S'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x, y + TAM_CELULA), (x + TAM_CELULA, y + TAM_CELULA), 2)
            if celula['W'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x, y), (x, y + TAM_CELULA), 2)
            if celula['E'] == 0:
                pygame.draw.line(tela, COR_PAREDE, (x + TAM_CELULA, y), (x + TAM_CELULA, y + TAM_CELULA), 2)

    obj_x = 0 + TAM_CELULA // 4
    obj_y = 0 + TAM_CELULA // 4
    pygame.draw.rect(tela, COR_OBJETIVO, (obj_x, obj_y, TAM_CELULA // 2, TAM_CELULA // 2))

def desenhar_caminho_djk():
    for (linha, coluna) in caminho_djk:
        x = (coluna - 1) * TAM_CELULA + TAM_CELULA // 4
        y = (linha - 1) * TAM_CELULA + TAM_CELULA // 4
        pygame.draw.rect(tela, COR_CAMINHO_DJK, (x, y, TAM_CELULA // 2, TAM_CELULA // 2))

def desenhar_controles():
    texto_passos = fonte.render(f"Seus passos: {passos} | Melhor: {passos_djk}", True, COR_TEXTO)
    tela.blit(texto_passos, (10, m.rows * TAM_CELULA + 10))

    botao_reiniciar = pygame.Rect(largura_tela - 120, m.rows * TAM_CELULA + 10, 110, 30)
    pygame.draw.rect(tela, COR_BOTAO, botao_reiniciar, border_radius=5)
    texto_botao = fonte.render("Reiniciar", True, COR_TEXTO_BOTAO)
    tela.blit(texto_botao, (largura_tela - 110, m.rows * TAM_CELULA + 15))

    botao_djk = pygame.Rect(largura_tela - 308, m.rows * TAM_CELULA + 10, 180, 30)
    pygame.draw.rect(tela, (50, 150, 50), botao_djk, border_radius=5)
    texto_djk = fonte.render("Melhor Caminho", True, COR_TEXTO_BOTAO)
    tela.blit(texto_djk, (largura_tela - 295, m.rows * TAM_CELULA + 15))

    return botao_reiniciar, botao_djk

def mostrar_popup_vitoria():
    s = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    tela.blit(s, (0, 0))

    popup_rect = pygame.Rect(largura_tela//2 - 200, altura_tela//2 - 100, 400, 200)
    pygame.draw.rect(tela, (240, 240, 240), popup_rect, border_radius=10)
    pygame.draw.rect(tela, (0, 150, 0), popup_rect, 3, border_radius=10)

    texto_vitoria = fonte_popup.render("Você venceu o labirinto!", True, (0, 100, 0))
    tela.blit(texto_vitoria, (popup_rect.centerx - texto_vitoria.get_width()//2, popup_rect.y + 30))

    texto_passos = fonte_vitoria.render(f"Seus passos: {passos}", True, COR_TEXTO)
    tela.blit(texto_passos, (popup_rect.centerx - texto_passos.get_width()//2, popup_rect.y + 70))

    texto_melhor = fonte_vitoria.render(f"Melhor possível: {passos_djk}", True, COR_TEXTO)
    tela.blit(texto_melhor, (popup_rect.centerx - texto_melhor.get_width()//2, popup_rect.y + 110))

    botao_ok = pygame.Rect(popup_rect.centerx - 50, popup_rect.y + 150, 100, 35)
    pygame.draw.rect(tela, (50, 150, 50), botao_ok, border_radius=5)
    texto_ok = fonte.render("OK", True, COR_TEXTO_BOTAO)
    tela.blit(texto_ok, (popup_rect.centerx - texto_ok.get_width()//2, popup_rect.y + 157))

    pygame.display.flip()
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            if evento.type == pygame.MOUSEBUTTONDOWN and botao_ok.collidepoint(evento.pos):
                esperando = False

# Loop principal
rodando = True
relogio = pygame.time.Clock()
mostrar_djk = False

while rodando:
    tela.fill(COR_PAREDE)
    desenhar_labirinto()

    if mostrar_djk:
        desenhar_caminho_djk()

    botao_reiniciar, botao_djk = desenhar_controles()

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
                mostrar_djk = False
            elif botao_djk.collidepoint(evento.pos):
                mostrar_djk = not mostrar_djk

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

            if pos_linha == 1 and pos_coluna == 1:
                venceu = True
                mostrar_popup_vitoria()
                venceu = False
                inicializar_jogo()

pygame.quit()
