from operator import pos
import random
import time
from turtle import down
import pygame
from pygame.locals import *
from sys import exit
from random import randint
import os
import sys

if getattr(sys, 'frozen', False):
    # Rodando como EXE: usa pasta temporária extraída
    base_path = sys._MEIPASS
else:
    # Rodando como script: usa pasta atual
    base_path = os.path.abspath(".")

# Função para carregar assets com caminho correto
def load_asset(folder, filename):
    path = os.path.join(base_path, folder, filename)
    return path

pygame.init()
pygame.joystick.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Versao do Game
Game_version = "1.1.0"

# Get version pygame
version_pygame = pygame.version.ver

# Print to console
print(f"Versão do Game: {Game_version}")
print(f"Versão do Pygame: {version_pygame}")
text_vGame = f"Versão do Game: {Game_version}"
text_vPygame = f"Versão do Pygame: {version_pygame}"

# Fonte
fonte = pygame.font.SysFont("franklingothicmedium", 30, True, False)

# Render texto em screen
surface_gamev = fonte.render(text_vGame, True, (0, 255, 0))
surface_vPygame = fonte.render(text_vPygame, True, (0, 255, 0))

# Menu pause fontes (corrigido nome da fonte)
fonte_pause = pygame.font.Font("franklingothicmedium.ttf", 30) if os.path.exists("franklingothicmedium.ttf") else pygame.font.SysFont("franklingothicmedium", 30)
fonte_pause_pequena = pygame.font.Font("franklingothicmedium.ttf", 24) if os.path.exists("franklingothicmedium.ttf") else pygame.font.SysFont("franklingothicmedium", 24)

# Menu pause texto
text_Mpause = "Menu Pause"
red_Mpause = fonte_pause.render(text_Mpause, True, (255, 255, 255))

# Configurações de som COM CAMINHOS DINÂMICOS
music_path = load_asset('sounds', 'ghost-house.mp3')
try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Toca música em loop
    pygame.mixer.music.set_volume(0.5)
    print("Música de fundo carregada!")
except:
    print("Aviso: Música não encontrada. Jogando sem som de fundo.")

Sound_Colision = None
try:
    Sound_Colision = pygame.mixer.Sound(load_asset('sounds', 'coin_collection.wav'))
    Sound_Colision.set_volume(0.5)
except:
    print("Aviso: Som de colisão não encontrado.")

Sound_start = None
try:
    Sound_start = pygame.mixer.Sound(load_asset('sounds', 'menu_selected.wav'))
    Sound_start.set_volume(1.0)
except:
    print("Aviso: Som de start não encontrado.")

Sound_quit = None
try:
    Sound_quit = pygame.mixer.Sound(load_asset('sounds', 'select-quit.wav'))
    Sound_quit.set_volume(1.0)
except:
    print("Aviso: Som de quit não encontrado.")

Sound_game_over = None
try:
    Sound_game_over = pygame.mixer.Sound(load_asset('sounds', 'game_over_effects.wav'))
    Sound_game_over.set_volume(1.0)
except:
    print("Aviso: Som de game over não encontrado.")

WIDTH = 1920
HEIGHT = 1080

# Configurações da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=FULLSCREEN, vsync=1)
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Criar overlay
overlap_pause = pygame.Surface((WIDTH, HEIGHT))
overlap_pause.fill((0, 30, 50))
overlap_pause.set_alpha(128)

# Surface desfocado
background_desf = None

# Variavel Pause
pause = False

# Aplicar blur
def aplicar_blur(surface):
    fator = 4
    temp = pygame.transform.smoothscale(surface, (WIDTH // fator, HEIGHT // fator))
    return pygame.transform.smoothscale(temp, (WIDTH, HEIGHT))

class Player():
    def __init__(self, pos_x, pos_y):
        self.rect = pygame.Rect(pos_x, pos_y, 25, 25)
        self.eating = False
        self.eat_start_time = 0
        self.eat_duration = 2000
    
    def eat(self):
        self.eating = True
        self.eat_start_time = pygame.time.get_ticks()
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if self.eating and (current_time - self.eat_start_time > self.eat_duration):
            self.eating = False

# Defina as direções como tuplas
UP = (0, -1)    # Cima
DOWN = (0, 1)   # Baixo
LEFT = (-1, 0)  # Esquerda
RIGHT = (1, 0)  # Direita

# Variáveis globais do Snake
pos_player = (WIDTH // 2 - 12, HEIGHT // 2 - 12)  # Centralizado
x_green = randint(0, WIDTH - 25)
y_green = randint(0, HEIGHT - 25)
FOOD_SIZE = 25 
MIN_X = 500  
MAX_X = 1500 
MIN_Y = 200 
MAX_Y = 700
speed = 10
x_control = speed
y_control = 0
current_direction = RIGHT
Score = 0
length_snake = 4
game_over = False
game_state = "menu"
intro_start = 0
in_transition = False
transition_start = 0
transition_delay = 1000
start_time = 0  # Para timer (setado no restart)
list_snake = []
player = Player(pos_player[0], pos_player[1])

# Suporte Joystick
joystick = None
joystick_connected = False
AXIS_THRESHOLD = 0.5
has_hat = False

# Load background image (jogo)
img_background = None
bg_path = load_asset('Sprites', 'floor-castle-background.png')
try:
    if os.path.exists(bg_path):
        img_background = pygame.image.load(bg_path).convert()
        img_background = pygame.transform.scale(img_background, (WIDTH, HEIGHT))
        print("Background do jogo carregado com sucesso!")
    else:
        raise FileNotFoundError
except FileNotFoundError:
    print("Aviso: Arquivo 'Sprites/floor-castle-background.png' não encontrado.")
    img_background = None
except pygame.error as e:
    print(f"Erro ao carregar background do jogo: {e}")
    img_background = None

# Load img_menu (menu)
img_menu = None
menu_path = load_asset('img', 'box_snake.png')
try:
    if os.path.exists(menu_path):
        img_menu = pygame.image.load(menu_path).convert()
        img_menu = pygame.transform.scale(img_menu, (WIDTH, HEIGHT))
    else:
        raise FileNotFoundError
except FileNotFoundError:
    print("Aviso: Arquivo 'box_snake.png' não encontrado na pasta raiz.")
    img_menu = None
except pygame.error as e:
    print(f"Erro ao carregar background do menu: {e}")
    img_menu = None

# Menu options
menu_options = ["Start Game", "Quit"]
menu_selected = 0

# Pause menu options (novo)
pause_options = ["Continue", "Quit to Menu"]
pause_selected = 0


# Função para desenhar menu
def drawMenu():
    if img_menu:
        screen.blit(img_menu, (0, 0))
    else:
        screen.fill((0, 0, 0))
        
    # Título
    fonte_titulo = pygame.font.SysFont("franklingothicmedium", 72, True, False)
    titulo = fonte_titulo.render("Snake Game", True, (255, 255, 255))
    ret_titulo = titulo.get_rect(center=(WIDTH//2, HEIGHT//4))
    screen.blit(titulo, ret_titulo)
    
    # AssDEV
    fonte_dev = pygame.font.SysFont("comicsansms", 30, True, False)
    dev_text = fonte_dev.render("Developed by Fernando Junior", True, (245, 245, 245))
    ret_dev = dev_text.get_rect(center=(WIDTH//2, HEIGHT - 60))
    screen.blit(dev_text, ret_dev)
    
    # Opções
    fonte_menu = pygame.font.SysFont("franklingothicmedium", 50, True, False)
    for idx, option in enumerate(menu_options):
        color = (255, 255, 0) if idx == menu_selected else (255, 255, 255)
        text = fonte_menu.render(option, True, color)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + idx * 60))
        screen.blit(text, rect)
    
    # Versões no canto
    screen.blit(surface_gamev, (WIDTH - surface_gamev.get_width() - 10, 10))
    screen.blit(surface_vPygame, (WIDTH - surface_vPygame.get_width() - 10, 50))

# Função para desenhar menu de pause (novo/completo)
def drawPauseMenu():
    # Desenha fundo desfocado + overlay
    if background_desf:
        screen.blit(background_desf, (0, 0))
    screen.blit(overlap_pause, (0, 0))
    
    # Título Pause
    screen.blit(red_Mpause, (WIDTH // 2 - red_Mpause.get_width() // 2, HEIGHT // 2 - 150))
    
    # Opções de pause
    fonte_pause_menu = pygame.font.SysFont("franklingothicmedium", 40, True, False)
    for idx, option in enumerate(pause_options):
        color = (255, 255, 0) if idx == pause_selected else (255, 255, 255)
        text = fonte_pause_menu.render(option, True, color)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50 + idx * 50))
        screen.blit(text, rect)

def restart():
    global Score, speed, length_snake, pos_player, list_snake, x_green, y_green, FOOD_SIZE, MIN_X, MAX_X, MIN_Y, MAX_Y, game_over, start_time, x_control, y_control, current_direction, player
    Score = 0
    speed = 10
    length_snake = 4
    pos_player = (WIDTH // 2 - 12, HEIGHT // 2 - 12)
    list_snake = []
    x_green = randint(0, WIDTH - 25)
    y_green = randint(0, HEIGHT - 25)
    FOOD_SIZE = 25
    MIN_X = 500
    MAX_X = 1500
    MIN_Y = 200 
    MAX_Y = 700
    game_over = False
    x_control = speed
    y_control = 0
    current_direction = RIGHT
    start_time = pygame.time.get_ticks()  # Reset timer
    player.rect.topleft = pos_player
    player.eating = False  # Corrigido

def drawTransition():
    if img_background:
        screen.blit(img_background, (0, 0))
    else:
        screen.fill((0, 0, 0))
    
    fonte_trans = pygame.font.SysFont("franklingothicmedium", 45, True, False)
    msg_trans = fonte_trans.render("Starting Game...", True, (255, 200, 0))
    ret_trans = msg_trans.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(msg_trans, ret_trans)
    
    progress = min((pygame.time.get_ticks() - transition_start) / transition_delay, 1.0)
    bar_width = int(400 * progress)
    pygame.draw.rect(screen, (255, 200, 0), (WIDTH//2 - 200, HEIGHT//2 + 60, bar_width, 20))
    pygame.draw.rect(screen, (240, 240, 240), (WIDTH//2 - 200, HEIGHT//2 + 60, 400, 20), 2)

# Função para desenhar a cobra 
def drawSnake(list_snake, eating=False):
    if not list_snake:
        return
    # Corpo (verde e preto)
    for index, pos in enumerate(list_snake[:-1]):
        if index % 2 == 0:
            color = (0, 255, 0)  # Verde para segmentos pares
        else:
            color = (0, 0, 0)     # Preto para segmentos ímpares
        pygame.draw.rect(screen, color, (pos[0], pos[1], 25, 25))  # Agora dentro do loop
    
    # Cabeça
    head_pos = list_snake[-1]
    if eating:
        current_time = pygame.time.get_ticks()
        blink = (current_time // 2000) % 2
        head_color = (150, 0, 50)
    else:
        head_color = (0, 0, 0)
    pygame.draw.rect(screen, head_color, (head_pos[0], head_pos[1], 25, 25))

# Loop principal
while True:
    clock.tick(60)
    
    delta_time = clock.get_time() / 1000.0
    
    # Detecta e inicializa joystick se não feito
    if not joystick_connected:
        if pygame.joystick.get_count() > 0:
            try:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                joystick_connected = True
                has_hat = joystick.get_numhats() > 0
                print(f"Joystick conectado: {joystick.get_name()}")
                if has_hat:
                    print("Joystick tem D-pad (hat).")
                else:
                    print("Joystick sem D-pad, usando sticks analógicos.")
            except pygame.error as e:
                print(f"Erro ao inicializar joystick: {e}")
                joystick_connected = False
                joystick = None
        else:
            joystick_connected = False
            joystick = None
            has_hat = False
    
    # Polling de joystick
    if joystick_connected and joystick:
        hat_x, hat_y = 0, 0  # Default idle
        if has_hat:
            try:
                hat = joystick.get_hat(0)
                hat_x, hat_y = hat
            except pygame.error:
                print("Erro ao ler hat, pulando para axes.")
                hat_x, hat_y = 0, 0
        
        # Sempre lê axes (stick esquerdo: 0=X, 1=Y)
        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)
        
        # Combina input: Prioriza hat se disponível, fallback para axes
        input_x = hat_x if abs(hat_x) > 0 else (1 if axis_x > AXIS_THRESHOLD else (-1 if axis_x < -AXIS_THRESHOLD else 0))
        input_y = hat_y if abs(hat_y) > 0 else (1 if axis_y > AXIS_THRESHOLD else (-1 if axis_y < -AXIS_THRESHOLD else 0))
        
        # Aplica input baseado no estado
        if game_state == "menu" and not in_transition:
            if input_y == -1:
                menu_selected = (menu_selected - 1) % len(menu_options)
            elif input_y == 1:
                menu_selected = (menu_selected + 1) % len(menu_options)
        elif game_state == "playing" and not pause:
            if input_x == 1 and x_control != -speed:  
                x_control = speed
                y_control = 0
            elif input_x == -1 and x_control != speed: 
                x_control = -speed
                y_control = 0
            elif input_y == -1 and y_control != speed:  
                x_control = 0
                y_control = -speed
            elif input_y == 1 and y_control != -speed:
                x_control = 0
                y_control = speed
        elif pause and game_state == "playing":
            # Suporte joystick no pause menu
            if input_y == -1:
                pause_selected = (pause_selected - 1) % len(pause_options)
            elif input_y == 1:
                pause_selected = (pause_selected + 1) % len(pause_options)
    
    for event in pygame.event.get():
        if event.type == QUIT: 
            pygame.quit()
            exit()
        
        # Event de Joystick (botões)
        if joystick_connected and event.type == JOYBUTTONDOWN:
            if game_state == "menu" and not in_transition:
                if event.button == 0:  # Botão 0 (A/Enter)
                    restart()
                    if menu_selected == 0:
                        if Sound_start:
                            Sound_start.play()
                        in_transition = True
                        transition_start = pygame.time.get_ticks()
                    elif menu_selected == 1: 
                        if Sound_quit:
                            Sound_quit.play()
                        in_transition = True
                        transition_delay = pygame.time.get_ticks()
                        pygame.quit()
                        exit()
            elif game_state == "playing" and pause:
                if event.button == 0:  # A/Enter no pause
                    if pause_selected == 0:  # Continue
                        pause = False
                        background_desf = None
                        if Sound_start:
                            Sound_start.play()
                    elif pause_selected == 1:  # Quit to Menu
                        game_state = "menu"
                        menu_selected = 0
                        pause = False
                        background_desf = None
                        if Sound_quit:
                            Sound_quit.play()
            elif game_state == "game_over":
                if event.button == 0:  # A = Restart
                    restart()
                    in_transition = True
                    transition_start = pygame.time.get_ticks()
                elif event.button == 1:  # B = Menu
                    game_state = "menu"
                    menu_selected = 0
            elif game_state == "playing" and not pause:
                if event.button == 0:  # A para pause no jogo
                    pause = not pause
                    if pause:
                        background_desf = aplicar_blur(screen.copy())
                    else:
                        background_desf = None
        # Teclado
        if event.type == KEYDOWN: 
            if game_state == "menu" and not in_transition:
                if event.key == K_UP:
                    menu_selected = (menu_selected - 1) % len(menu_options)
                if event.key == K_DOWN:
                    menu_selected = (menu_selected + 1) % len(menu_options)
                if event.key == K_RETURN:
                    if menu_selected == 0:  # Start Game
                        restart()
                        if Sound_start:
                            Sound_start.play()
                        in_transition = True
                        transition_start = pygame.time.get_ticks()
                    elif menu_selected == 1:  # Quit
                        if Sound_quit:
                            Sound_quit.play()
                        in_transition = True
                        transition_delay = pygame.time.get_ticks()
                        pygame.quit()
                        exit()
            elif game_state == "playing" and not pause:
                if event.key == K_LEFT and current_direction != RIGHT:
                    current_direction = LEFT
                    if x_control != -speed:
                        x_control = -speed
                        y_control = 0    
                if event.key == K_RIGHT and current_direction != LEFT:
                    current_direction = RIGHT
                    if x_control != speed:
                        x_control = speed
                        y_control = 0
                if event.key == K_UP and current_direction != DOWN:
                    current_direction = UP
                    if y_control != -speed:
                        x_control = 0
                        y_control = -speed
                if event.key == K_DOWN and current_direction != UP:
                    current_direction = DOWN
                    if y_control != speed:
                        x_control = 0
                        y_control = speed
                if event.key == K_p:
                    pause = not pause
                    if pause:
                        background_desf = aplicar_blur(screen.copy())
                    else:
                        background_desf = None
            elif pause and game_state == "playing":
                if event.key == K_UP:
                    pause_selected = (pause_selected - 1) % len(pause_options)
                if event.key == K_DOWN:
                    pause_selected = (pause_selected + 1) % len(pause_options)
                if event.key == K_RETURN:
                    if pause_selected == 0:  # Continue
                        pause = False
                        background_desf = None
                        if Sound_start:
                            Sound_start.play()
                    elif pause_selected == 1:  # Quit to Menu
                        game_state = "menu"
                        menu_selected = 0
                        pause = False
                        background_desf = None
                        if Sound_quit:
                            Sound_quit.play()
                if event.key == K_ESCAPE:
                    pause = False
                    background_desf = None
            elif game_state == "game_over":
                if event.key == K_r:
                    restart()
                    in_transition = True
                    transition_start = pygame.time.get_ticks()
                if event.key == K_m:
                    game_state = "menu"
                    menu_selected = 0
                    if Sound_start:
                        Sound_start.play()
    
    # Check fim da transição
    if in_transition:
        if pygame.time.get_ticks() - transition_start > transition_delay:
            game_state = "playing"
            in_transition = False
            start_time = pygame.time.get_ticks()  # Inicia timer no playing
    
    # LÓGICA DO JOGO (só se playing e não pausado) - Movida para antes do desenho
    if game_state == "playing" and not pause and not game_over:
        # Move player (cabeça da cobra)
        pos_player = (pos_player[0] + x_control, pos_player[1] + y_control)
        
        # Bordas infinitas (wrap around)
        if pos_player[0] > WIDTH:
            pos_player = (0, pos_player[1])
        if pos_player[0] < 0:
            pos_player = (WIDTH - 25, pos_player[1])
        if pos_player[1] > HEIGHT:
            pos_player = (pos_player[0], 0)
        if pos_player[1] < 0:
            pos_player = (pos_player[0], HEIGHT -25) 
        
        # Atualizar list_snake com a nova posição
        list_head = [pos_player[0], pos_player[1]]
        list_snake.append(list_head)
        if len(list_snake) > length_snake:
            del list_snake[0]
        
        # Sincronizar posição do player
        if list_snake:
            player.rect.topleft = tuple(list_snake[-1])
        
        # Colisão com si mesmo
        if list_snake.count(list_head) > 1:
            game_over = True
            game_state = "game_over"
            if Sound_game_over:
                Sound_game_over.play()
        
        # Desenha comida
        rect_green = pygame.Rect(x_green, y_green, FOOD_SIZE, FOOD_SIZE)
        
        # Colisão com comida
        if list_snake:
            head_pos = list_snake[-1]
            head_rect = pygame.Rect(head_pos[0], head_pos[1], 25, 25)
            if head_rect.colliderect(rect_green):
                x_green = random.randint(MIN_X, MAX_X - FOOD_SIZE)
                y_green = random.randint(MIN_Y, MAX_Y - FOOD_SIZE)
                length_snake += 1
                Score += 1
                if Sound_Colision:
                    Sound_Colision.play()
                player.eat()
        
        # Update animação
        player.update()
        
        # Aumento de speed
        if Score > 0 and Score % 10 == 0:
            new_speed = 10 + (Score // 10)
            if new_speed > speed:
                speed = new_speed
    
    # Bloco de desenho
    if game_state == "menu" and not in_transition:
        drawMenu()
    elif in_transition:
        drawTransition()
    elif game_state == "playing":
        if img_background:
            screen.blit(img_background, (0, 0))
        else:
            screen.fill((0, 0, 0))
        
        if pause:
            # Pause: Desenha blur + menu de pause
            drawPauseMenu()
        else:
            # Jogo normal: Desenha elementos
            # Desenha comida
            pygame.draw.rect(screen, (255, 0, 0), rect_green)
            
            # Desenha cobra
            drawSnake(list_snake, player.eating)
            
            # Timer
            if start_time > 0:
                elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
                minutes = elapsed_time // 60
                seconds = elapsed_time % 60
                time_text = f'Time: {minutes:02d}:{seconds:02d}'
                fonte_time = fonte.render(time_text, True, (255, 255, 255))
                ret_text_time = fonte_time.get_rect(center=(WIDTH//2, 25))
                screen.blit(fonte_time, ret_text_time)
            
            # Textos (score e speed)
            mensagem = f'Score: {Score}'
            tspeed = f'Speed: {speed}'
            text_formatado = fonte.render(mensagem, True, (255, 255, 255))
            tformat_speed = fonte.render(tspeed, True, (255, 255, 255))
            screen.blit(text_formatado, (WIDTH - 200, 10))
            screen.blit(tformat_speed, (20, 10))
    elif game_state == "game_over":   
        if img_background:
            screen.blit(img_background, (0, 0))
        else:
            screen.fill((255, 255, 255))  # Fallback branco
        
        fonte_game_over = pygame.font.SysFont("franklingothicmedium", 50, True, False)
        mensagem_game_over = 'Game Over! Press R to Restart or M for Menu'
        msg_game_over_joystick = 'Joystick: A=Restart, B=Menu'
        text_formatado_game_over = fonte_game_over.render(mensagem_game_over, True, (255, 0, 20))
        text_format_game_over_joy = fonte_game_over.render(msg_game_over_joystick, True, (255, 0, 20)) 
        ret_text_game_over = text_formatado_game_over.get_rect(center=(WIDTH//2, HEIGHT//2))
        ret_text_game_over_j = text_format_game_over_joy.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        if joystick_connected:
            screen.blit(text_format_game_over_joy, ret_text_game_over_j)
        else:
            screen.blit(text_formatado_game_over, ret_text_game_over)
            
        # Time final (calculado localmente)
        if start_time > 0:
            elapsed_time = (pygame.time.get_ticks()) // 1000
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            time_final = fonte.render(f'Time: {minutes:02d}:{seconds:02d}', True, (0, 0, 0))
            screen.blit(time_final, (WIDTH//2 - time_final.get_width()//2, HEIGHT//2 + 80))
        
        # Score final
        score_final = fonte.render(f'Final Score: {Score}', True, (0, 0, 0))
        screen.blit(score_final, (WIDTH//2 - score_final.get_width()//2, HEIGHT//2 + 50))
    
    # Atualiza a tela
    pygame.display.flip()
