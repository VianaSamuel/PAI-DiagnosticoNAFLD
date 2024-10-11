# Pedro Corrêa Rigotto (762281)
# Samuel Luiz da Cunha Viana Cruz (762496)

# instalando bibliotecas necessárias
# import subprocess
# import sys
# subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])

import matplotlib.pyplot as plt
import numpy as np
import os
import scipy.io
from PIL import Image
import tkinter as tk
from tkinter import ttk, filedialog#, messagebox



#=============== PROCESSAMENTO DE IMAGENS ===============#
#=(CARREGAMENTO - imagens)
# retorna uma tupla que contém um vetor de imagens soltas e um vetor de imagens de cada paciente para uso na função exibir_imagens
def carregar_imagens():
    # salva os caminhos das imagens a serem carregadas
    vetor_caminhos_imagens = filedialog.askopenfilenames(title="Selecionar imagens", filetypes=[("Todos os arquivos", "*.mat;*.jpg;*.png")])
    
    # carregamento e processamento de cada imagem
    vetor_pacientes = [[]] # indice 0: imagens avulsas, indice 1 em diante: imagens de cada paciente. pacientes vao de 1 a 55
    salva_vetor_pacientes(vetor_caminhos=vetor_caminhos_imagens, vetor_pacientes=vetor_pacientes)
    return vetor_pacientes


#=(CARREGAMENTO - .mat)
# retorna um ARRAY de imagens
def carrega_array_mat(caminho):
    arquivo_mat = scipy.io.loadmat(caminho)
    array_mat = arquivo_mat['data']
    return array_mat['images']


#=(CARREGAMENTO - .jpg e .png)
# retorna UMA imagem
def carrega_imagem_jpg_png(caminho):
    img_aberta = Image.open(caminho)
    if img_aberta.mode != 'L':  # se imagem estiver em RGB, converte para tons de cinza
        img_aberta = img_aberta.convert('L')
    img_aberta = np.array(img_aberta, dtype=np.uint8).tolist()
    return img_aberta

#=(SALVAMENTO)
def salva_vetor_pacientes(vetor_caminhos, vetor_pacientes):
    for caminho in vetor_caminhos:
        # PACIENTES
        if caminho.lower().endswith('.mat'):
            array_mat = carrega_array_mat(caminho)
            for i, paciente in enumerate(array_mat[0]): # array_mat[0][paciente][imagem]
                vetor_pacientes.append(paciente)
                for imagem in paciente:
                    if isinstance(vetor_pacientes[i+1], np.ndarray):
                        vetor_pacientes[i+1] = vetor_pacientes[i+1].tolist() # o paciente vem como ndarray por algum motivo. isso converte para lista
                    vetor_pacientes[i+1].append(imagem)

        # IMAGENS AVULSAS
        elif caminho.lower().endswith(('.png', '.jpg')):
            imagem_avulsa = carrega_imagem_jpg_png(caminho)
            vetor_pacientes[0].append(imagem_avulsa)
#=============== FIM PROCESSAMENTO DE IMAGENS ===============#



#=============== HISTOGRAMA ===============#
#=(CALCULO - histograma)
def calculo_histograma(imagem):
    # iniciliza array do histograma com 256 valores de intensidade (0 a 255), todos com 0
    histograma = [0 for _ in range(256)]

    # percorre imagem pixel por pixel, contando a frequência de cada valor de intensidade
    for x in range(len(imagem)): # percorre as linhas (altura) da imagem
        for y in range(len(imagem[x])): # percorre as colunas (largura) da imagem
            valor_intensidade_pixel = imagem[x][y]
            histograma[valor_intensidade_pixel] += 1
    histograma[0] = 0 # o fundo da imagem de ultrassom é preto. isso tira do histograma o pico do fundo, para normalizar a altura dos dados
    return histograma

#=============== FIM HISTOGRAMA ===============#


#=============== JANELAS DOS BOTÕES ===============#

def janela_imagens_e_histogramas(vetor_pacientes, idx_paciente=-1, idx_imagem=-1):
    def prepara_a_tela():
        nonlocal idx_paciente
        nonlocal idx_imagem
        # limpa o gráfico anterior
        imagem_histograma[0].cla()
        imagem_histograma[1].cla()
        # exibe a nova imagem e o histograma dela
        if(len(vetor_pacientes[idx_paciente]) > 0): # se tem alguma imagem para exibir
            janela_histograma_exibe_uma(vetor_pacientes[idx_paciente][idx_imagem], titulo)
        else:
            print("Nenhuma imagem carregada para exibir.")
            tk.messagebox.showerror("Erro", "Nenhuma imagem carregada para exibir.")
            plt.close(figura)
            return
        # atualiza a tela
        plt.draw()
        
    def navegar_avancar(event):
        nonlocal idx_paciente
        nonlocal idx_imagem
        if idx_imagem < len(vetor_pacientes[idx_paciente]) - 1: # se nao é a ultima imagem daquela fonte
            idx_imagem += 1
        elif idx_paciente < len(vetor_pacientes) - 1: # se nao é a ultima fonte
            if len(vetor_pacientes[idx_paciente+1]) != 0:
                idx_imagem = 0
                idx_paciente += 1
        prepara_a_tela()
    
    def navegar_retroceder(event):
        nonlocal idx_paciente
        nonlocal idx_imagem
        if idx_imagem > 0:  # se não é a primeira imagem daquela fonte
            idx_imagem -= 1
        elif idx_paciente > 0:  # se não é a primeira fonte
            if len(vetor_pacientes[idx_paciente-1]) != 0:
                idx_paciente -= 1
                idx_imagem = len(vetor_pacientes[idx_paciente]) - 1
        prepara_a_tela()

    def janela_histograma_exibe_uma(imagem, titulo=""):
        # exibe a imagem à esquerda
        imagem_histograma[0].imshow(imagem, cmap='gray')
        imagem_histograma[0].set_title(titulo)
        imagem_histograma[0].axis('off')
        # calcula o histograma
        histograma = calculo_histograma(imagem)
        # exibe o histograma à direita
        imagem_histograma[1].plot(histograma, color='black')
        imagem_histograma[1].set_title('Histograma')
        imagem_histograma[1].set_xlim([0, 255])
        imagem_histograma[1].set_xlabel('Intensidade')
        imagem_histograma[1].set_ylabel('Frequência')

    def on_key(event):
        if event.key == 'right':
            navegar_avancar(event)
        elif event.key == 'left':
            navegar_retroceder(event)

    titulo = ""
    # idx_paciente - 0: avulsa, >=1: paciente
    is_avulsa = True if idx_paciente == 0 else False
    if is_avulsa:
        titulo = f"Imagem Avulsa #{idx_imagem+1}"
    else:
        titulo = f"Paciente #{idx_paciente} - Imagem #{idx_imagem+1}"

    # cria a figura e os subplots
    figura, imagem_histograma = plt.subplots(1, 2, figsize=(10, 5))

    # conecta os eventos de botões do teclado. especificamente, navegação via setas
    figura.canvas.mpl_connect('key_press_event', on_key)

    # cria os botões. pode navegar via teclado ou os botões
    localizacao_botao_avancar = plt.axes([0.7, 0.05, 0.1, 0.075])
    localizacao_botao_retroceder = plt.axes([0.81, 0.05, 0.1, 0.075])
    btn_prev = plt.Button(localizacao_botao_avancar, '<')
    btn_next = plt.Button(localizacao_botao_retroceder, '>')
    btn_prev.on_clicked(navegar_retroceder)
    btn_next.on_clicked(navegar_avancar)

    prepara_a_tela()

    # insere a figura na tela
    plt.tight_layout()
    plt.show()
#=============== FIM JANELA DOS BOTÕES ===============#


def prepara_ids(vetor_pacientes):
    idx_paciente = -1,
    idx_imagem = -1,
    for i, paciente in enumerate(vetor_pacientes):
        if len(paciente) != 0:
            idx_paciente = i
            idx_imagem = 0
            break
    if idx_paciente == -1:
        print("Nenhuma imagem.")
        tk.messagebox.showerror("Erro", "Nenhuma imagem.")
        return
    janela_imagens_e_histogramas(vetor_pacientes, idx_paciente, idx_imagem)

#=============== GUI ===============#
def menu_principal():
    # config: janela, resolução, estilização
    root = tk.Tk()
    root.title("PAI-DIagnosticoNAFLD")
    root.geometry("400x500")
    style = ttk.Style()
    style.theme_use('clam')

    # frame: menu principal
    menu_principal = ttk.Frame(root)
    menu_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    menu_principal.columnconfigure(0, weight=1)

    vetor_pacientes = carregar_imagens()

    # botões
    btn0 = tk.Button(menu_principal, text="Visualizar (Imagens + Histogramas)", command=lambda:{prepara_ids(vetor_pacientes=vetor_pacientes)}, width=50, height=2)
    btn0.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    btn1 = tk.Button(menu_principal, text="Recortar (ROIs)", width=50, height=2)
    btn1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    btn2 = tk.Button(menu_principal, text="Visualizar (ROIs Geradas + Histogramas)", width=50, height=2)
    btn2.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    btn3 = tk.Button(menu_principal, text="Calcular (GLCM + Descritores de Textura) de uma ROI", width=50, height=2)
    btn3.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    btn4 = tk.Button(menu_principal, text="Caracterizar (ROIs Geradas) através de Descritor de Textura", width=50, height=2)
    btn4.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

    btn5 = tk.Button(menu_principal, text="Classificar (Imagem)", width=50, height=2)
    btn5.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

    # nomes e matrículas
    pedro = tk.Label(menu_principal, text="Pedro Corrêa Rigotto (762281)", anchor="center")
    pedro.grid(row=6, column=0, pady=(20, 0), sticky="nsew")
    samuel = tk.Label(menu_principal, text="Samuel Luiz da Cunha Viana Cruz (762496)", anchor="center")
    samuel.grid(row=7, column=0, pady=(0, 10), sticky="nsew")
    
    root.mainloop()
#=============== FIM GUI ===============#



#=============== MAIN ===============#    
if __name__ == "__main__":
    menu_principal()
#=============== FIM MAIN ===============#