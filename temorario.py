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
from tkinter import ttk, filedialog, messagebox

#=============== PROCESSAMENTO DE IMAGENS ===============#

#=(CARREGAMENTO + EXIBIÇÃO)
def carregar_exibir_imagens():
    # salva os caminhos das imagens a serem carregadas
    vetor_caminhos_imagens = filedialog.askopenfilenames(title="Selecionar imagens", filetypes=[("Todos os arquivos", "*.mat;*.jpg;*.png")])
    
    # carregamento e processamento de cada imagem
    vetor_imagens = []
    vetor_titulos = []
    salva_vetor_imagens(vetor_caminhos_imagens, vetor_imagens, vetor_titulos)
    
    # exibição das imagens
    if vetor_imagens:
        janela_imagens(vetor_imagens, vetor_titulos)
    else:
        messagebox.showwarning("Aviso", "Não foi adicionada nenhuma imagem.")

#=(CARREGAMENTO)
def carrega_imagem(caminho):
    img = None
    
    # se for .mat
    if caminho.lower().endswith('.mat'):
        img_dados = scipy.io.loadmat(caminho)
        img = img_dados['data']

    # se for .png ou .jpg
    elif caminho.lower().endswith(('.png', '.jpg')):
        img_aberta = Image.open(caminho)
        if img_aberta.mode != 'L':  # se imagem estiver em RGB, converte para tons de cinza
            img_aberta = img_aberta.convert('L')
        img = np.array(img_aberta)

    return img

#=(EXIBIÇÃO)
# janela do matplot utilizada para exibir as imagens carregadas
def janela_imagens(vetor_imagens, vetor_titulos, largura_px = 800, altura_px = 600, dpi = 100):
    # cálculo de altura e lagura em polegadas
    largura_pol = largura_px / dpi
    altura_pol = altura_px / dpi

    # configurações de janela e grade (galeria) para exibir imagens com as dimensões calculadas
    colunas_grade = 3
    linhas_grade = (len(vetor_imagens) + colunas_grade - 1) // colunas_grade
    janela_plot = plt.figure(figsize=(largura_pol, altura_pol), dpi=dpi)
    janela_plot.canvas.manager.set_window_title("Visualização de Imagens")
    # janela_plot.canvas.toolbar_visible = False
    
    # junção das imagens e títulos em um vetor de tuplas, iterando sobre as tuplas e exibindo as imagens
    zip_imagens_titulos = zip(vetor_imagens, vetor_titulos)
    for i, (imagem, titulo) in enumerate(zip_imagens_titulos):
        exibe_imagem(imagem, titulo, colunas_grade, linhas_grade, i)
    
    # ajuste de layout e exibição de figuras
    plt.tight_layout()
    plt.show()

def exibe_imagem(imagem, titulo, colunas_grade = 3, linhas_grade = 1, i = 0):
    plt.subplot(linhas_grade, colunas_grade, i+1)
    plt.imshow(imagem, cmap='gray')
    plt.title(titulo)
    plt.axis('off')

#=(SALVAMENTO)
def salva_vetor_imagens(vetor_caminhos_imagens, vetor_imagens, vetor_titulos):
    for caminho_imagem in vetor_caminhos_imagens:
        imagem = carrega_imagem(caminho_imagem)
        vetor_imagens.append(imagem)
        vetor_titulos.append(os.path.basename(caminho_imagem))
#=============== FIM PROCESSAMENTO DE IMAGENS ===============#

#=============== HISTOGRAMA ===============#
def calculo_histograma(imagem):
    # iniciliza array do histograma com 256 valores de intensidade (0 a 255), todos com 0
    histograma = [0 for intensidade in range(256)]

    # percorre imagem pixel por pixel, contando a frequência de cada valor de intensidade
    for altura in range(imagem.shape[0]): # percorre as linhas da imagem
        for largura in range(imagem.shape[1]): # percorre as colunas da imagem
            valor_intensidade_pixel = imagem[altura, largura]
            histograma[valor_intensidade_pixel] += 1

    # plotagem do histograma
    plt.figure()
    plt.plot(histograma)
    plt.show()
#=============== FIM HISTOGRAMA ===============#

    
#=============== GUI ===============#
def menu_principal():
    # config: janela, resolução, estilização
    root = tk.Tk()
    root.title("PAI-DIagnosticoNAFLD")
    root.geometry("400x475")
    style = ttk.Style()
    style.theme_use('clam')

    # frame: menu principal
    menu_principal = ttk.Frame(root)
    menu_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    menu_principal.columnconfigure(0, weight=1)

    # botões
    btn0 = tk.Button(menu_principal, text="Visualizar (Imagens + Histogramas)", command=carregar_exibir_imagens, width=50, height=2)
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