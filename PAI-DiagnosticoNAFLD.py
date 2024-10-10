# Pedro Corrêa Rigotto (762281)
# Samuel Luiz da Cunha Viana Cruz (762496)

# instalando bibliotecas necessárias
# import subprocess
# import sys
# subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])

import matplotlib.pyplot as plt
# import numpy as np
# import os
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
    vetor_imagens = [] # indice 0: imagens avulsas, indice 1 em diante: imagens de cada paciente. pacientes vao de 1 a 55
    vetor_imagens.append([]) # imagens avulsas (indice 0)
    salva_vetor_imagens(vetor_caminhos_imagens, vetor_imagens)
    return vetor_imagens


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
    return img_aberta


#=(EXIBIÇÃO)
# VELHA, PROVAVELMENTE NÃO VAI SER USADA E TA ERRADA
# def exibir_imagens(tupla_avulsas_pacientes, funcao_exibicao = janela_histograma):
#     if tupla_avulsas_pacientes[0] != [] or tupla_avulsas_pacientes[1] != []:
#         funcao_exibicao(tupla_avulsas_pacientes)
#     else:
#         messagebox.showwarning("Aviso", "Não foi adicionada nenhuma imagem.")


#=(SALVAMENTO)
def salva_vetor_imagens(vetor_caminhos, vetor_imagens):
    for caminho in vetor_caminhos:
        # PACIENTES
        if caminho.lower().endswith('.mat'):
            array_mat = carrega_array_mat(caminho)
            for i, paciente in enumerate(array_mat[0]): # array_mat[0][paciente][imagem]
                vetor_imagens.append(paciente)
                for imagem in paciente:
                    vetor_imagens[i+1].append(imagem)

        # IMAGENS AVULSAS
        elif caminho.lower().endswith(('.png', '.jpg')):
            imagem_avulsa = carrega_imagem_jpg_png(caminho)
            vetor_imagens[0].append(imagem_avulsa)
#=============== FIM PROCESSAMENTO DE IMAGENS ===============#



#=============== HISTOGRAMA ===============#
#=(CALCULO - histograma)
def calculo_histograma(imagem):
    # iniciliza array do histograma com 256 valores de intensidade (0 a 255), todos com 0
    histograma = [0 for intensidade in range(256)]
    print(imagem.shape)

    # percorre imagem pixel por pixel, contando a frequência de cada valor de intensidade
    for x in range(imagem.shape[0]): # percorre as linhas (altura) da imagem
        for y in range(imagem.shape[1]): # percorre as colunas (largura) da imagem
            valor_intensidade_pixel = imagem[x, y]
            histograma[valor_intensidade_pixel] += 1
    return histograma


# #=(GERA IMAGEM - histograma)
# # transforma o vetor do histograma em uma imagem 256x200
# def gera_imagem_histograma(histograma, altura = 200):
#     histograma_imagem = [[] for intensidade in range(256)] 
#     for cor_count in histograma: # cor_count = numero de pixels daquela cor
#         for y in range(altura):
#             if y < cor_count: # preenche de preto até o número de ocorrências
#                 histograma_imagem[cor_count].append(0)
#             else:
#                 histograma_imagem[cor_count].append(255)
#     return histograma_imagem
#=============== FIM HISTOGRAMA ===============#


#=============== JANELAS DOS BOTÕES ===============#

def janela_imagens_e_histogramas(vetor_imagens):
    def prepara_a_tela():
        # limpa o gráfico anterior
        imagem_histograma[0].cla()
        imagem_histograma[1].cla()
        # exibe a nova imagem e o histograma dela
        janela_histograma_exibe_uma(vetor_imagens[idx_fonte][idx_imagem], titulo)
        # atualiza a tela
        plt.draw()

    def navegar_avancar(event):
        nonlocal idx_fonte
        nonlocal idx_imagem
        if idx_imagem < len(vetor_imagens[idx_fonte]) - 1: # se nao é a ultima imagem daquela fonte
            idx_imagem += 1
        elif idx_fonte < len(vetor_imagens) - 1: # se nao é a ultima fonte
            idx_imagem = 0
            idx_fonte += 1
        prepara_a_tela()
    
    def navegar_retroceder(event):
        nonlocal idx_fonte
        nonlocal idx_imagem
        if idx_imagem > 0:  # se não é a primeira imagem daquela fonte
            idx_imagem -= 1
        elif idx_fonte > 0:  # se não é a primeira fonte
            idx_fonte -= 1
            idx_imagem = len(vetor_imagens[idx_fonte]) - 1
        prepara_a_tela()

    def janela_histograma_exibe_uma(imagem, titulo=""):
        # exibe a imagem à esquerda
        imagem_histograma[0].imshow(imagem)
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

    idx_fonte = 0 # 0: avulsa, >=1: paciente
    idx_imagem = 0 # id da imagem dentro do vetor da fonte dela
    titulo = ""
    is_avulsa = True if idx_fonte == 0 else False
    if is_avulsa:
        titulo = f"Imagem Avulsa #{idx_imagem+1}"
    else:
        titulo = f"Paciente #{idx_fonte} - Imagem #{idx_imagem+1}"

    # cria a figura e os subplots
    figura, imagem_histograma = plt.subplots(1, 2, figsize=(10, 5))

    # conecta os eventos de navegação com os botões do menu do matplotlib
    figura.canvas.manager.toolbar.push_current = navegar_avancar
    figura.canvas.manager.toolbar.back = navegar_retroceder

    prepara_a_tela()

    # insere a figura na tela
    plt.tight_layout()
    plt.show()
#=============== FIM JANELA DOS BOTÕES ===============#



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

    vetor_imagens = carregar_imagens()

    # botões
    btn0 = tk.Button(menu_principal, text="Visualizar (Imagens + Histogramas)", command=lambda: {janela_imagens_e_histogramas(vetor_imagens)}, width=50, height=2)
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