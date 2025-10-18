import tkinter as tk 
from PIL import Image, ImageTk, ImageDraw, ImageFont
import subprocess  # Para executar o arquivo do jogo
import os

# Função para iniciar o jogo após a intro
def start_game():
    root.attributes('-fullscreen', False)  # Sai do fullscreen
    root.destroy()  # Fecha a janela
    subprocess.Popen(['Snake.exe'])  # Executa o arquivo .exe do jogo (ajuste o nome/caminho se necessário)

# Função para transição de fade sequencial: fade out de img1, depois fade in de img2
def fade_transition(canvas, img1, img2, duration=4000, steps=40):  # 4 segundos totais, 40 passos
    step_time = duration // steps
    width, height = img1.size
    
    # Fase 1: Fade out de img1 para transparente (primeira metade dos passos)
    fade_out_steps = steps // 2
    for i in range(fade_out_steps + 1):
        alpha = i / fade_out_steps  # Alpha de 0 a 1 para fade out (0 = visível, 1 = invisível)
        
        # img1 fade out
        img1_faded = Image.blend(img1.convert('RGBA'), Image.new('RGBA', img1.size, (0, 0, 0, 0)), alpha)
        
        combined = img1_faded
        
        # Converter para PhotoImage e atualizar o canvas
        combined_tk = ImageTk.PhotoImage(combined)
        canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, anchor='center', image=combined_tk)
        canvas.image = combined_tk
        
        root.update()
        root.after(step_time)
    
    # Limpar o canvas para garantir que img1 esteja completamente removida (opacidade 0)
    canvas.delete("all")
    
    # Fase 2: Fade in de img2 (segunda metade dos passos)
    fade_in_steps = steps - fade_out_steps
    for i in range(fade_in_steps + 1):
        alpha = i / fade_in_steps  # Alpha de 0 a 1 para fade in (0 = invisível, 1 = visível)
        
        # img2 fade in
        img2_faded = Image.blend(Image.new('RGBA', img2.size, (0, 0, 0, 0)), img2.convert('RGBA'), alpha)
        
        combined = img2_faded
        
        # Converter para PhotoImage e atualizar o canvas
        combined_tk = ImageTk.PhotoImage(combined)
        canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, anchor='center', image=combined_tk)
        canvas.image = combined_tk
        
        root.update()
        root.after(step_time)
    
    # Após o fade, iniciar o jogo
    start_game()

# Função para iniciar a transição
def show_second_image():
    try:
        print("Iniciando transição sequencial: fade out da primeira imagem, depois fade in da segunda.")
        
        # Atualiza o canvas para garantir que esteja pronto
        canvas.update()
        
        # Carrega a segunda imagem e redimensiona para o mesmo tamanho da primeira
        img2 = Image.open('img/pygame_tiny.png')
        img2 = img2.resize((500, 500))  # Mesmo tamanho de img1_composed (ajustado para 500x500)
        
        # Inicia a transição de fade sequencial
        fade_transition(canvas, img1_composed, img2)
    except Exception as e:
        print(f"Erro na transição: {e}")
        start_game()  # Inicia o jogo se der erro

# Cria a janela Tkinter
root = tk.Tk()
root.title("Intro do Jogo")
root.attributes('-fullscreen', True)  # Ativa fullscreen
root.configure(bg='black')  # Fundo preto

# Cria um Canvas para as imagens
canvas = tk.Canvas(root, bg='black', highlightthickness=0)
canvas.pack(fill='both', expand=True)

# Força a atualização da janela para obter dimensões corretas
root.update()

# Carrega a primeira imagem e adiciona o texto a ela
try:
    img1 = Image.open('img/VUS_LOGO.png')
    img1 = img1.resize((500, 500)) 
    
    # Criar uma cópia para adicionar o texto
    img1_composed = img1.copy().convert('RGBA')
    draw = ImageDraw.Draw(img1_composed)
    
    # Carregar fonte
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
    
    # Adicionar o texto com gap do fundo
    text = "Gamer Developer: Fernando Junior"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    gap = 1  # Espaço em pixels entre o texto e o fundo da imagem 
    x = (img1_composed.width - text_width) // 2
    y = img1_composed.height - text_height - gap  # Adiciona o gap
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Exibir a imagem composta no canvas
    img1_composed_tk = ImageTk.PhotoImage(img1_composed)
    canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, anchor='center', image=img1_composed_tk)
    canvas.image = img1_composed_tk
except Exception as e:
    print(f"Erro ao carregar ou compor a primeira imagem: {e}")
    img1_composed = None

# Após 8 segundos, inicia a transição
root.after(8000, show_second_image)

# Atalho para sair
def on_closing():
    root.attributes('-fullscreen', False)
    root.destroy()
root.bind('<Escape>', lambda event: on_closing())

# Timer de backup
root.after(15000, start_game)  # Após 15 segundos, inicia o jogo se nada acontecer

root.mainloop()
