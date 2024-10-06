# Pedro Corrêa Rigotto (762281)
# Samuel Luiz da Cunha Viana Cruz (762496)

# instalando bibliotecas necessárias
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])

import matplotlib
import numpy
import os
import scipy.io
from PIL import Image
from tkinter import filedialog
from tkinter import Tk

# CARREGAMENTO DE IMAGENS #
def carrega_imagem(caminho):
    imagem = None
    
    if caminho.lower().endswith('.mat'): # se for .mat
        imagem = carrega_imagem_mat(caminho)
    elif caminho.lower().endswith(('.png', '.jpg')): # se for .png ou .jpg
        imagem = carrega_imagem_png_jpg(caminho)

    return imagem

def carrega_imagem_mat(caminho):
    dados = scipy.io.loadmat(caminho)
    return dados['data']

def carrega_imagem_png_jpg(caminho):
    imagem = Image.open(caminho)
    return numpy.array(imagem)



# EXIBIÇÃO DE IMAGENS #
# para exibir imagens, essa função precisa de saber a altura e largura da imagem em pixels, e o dpi
# é necessário para ajustar o tamanho da imagem na tela
def exibe_imagens(vetor_imagens, vetor_titulos, largura_em_pixels = 1200, altura_em_pixels = 800, dpi = 100):
    # cálculo de altura e lagura em polegadas
    largura_em_polegadas = largura_em_pixels / dpi
    altura_em_polegadas = altura_em_pixels / dpi

    # configurações de figura e grade para exibir imagens com as dimensões calculadas
    matplotlib.pyplot.figure(figsize=(largura_em_polegadas, altura_em_polegadas), dpi=dpi)
    colunas_da_grade = 3
    linhas_da_grade = (len(vetor_imagens) + colunas_da_grade - 1) // colunas_da_grade
    
    zip_imagens_titulos = zip(vetor_imagens, vetor_titulos) # junção das imagens e títulos em um vetor de tuplas
    for i, (imagem, titulo) in enumerate(zip_imagens_titulos): # itera sobre as tuplas e exibe as imagens
        exibe_uma_imagem(imagem, titulo, colunas_da_grade, linhas_da_grade, i)
    
    # ajuste de layout e exibição de figuras
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.show()

def exibe_uma_imagem(imagem, titulo, colunas_da_grade = 3, linhas_da_grade = 1, i = 0):
    matplotlib.pyplot.subplot(linhas_da_grade, colunas_da_grade, i + 1)
    matplotlib.pyplot.imshow(imagem, cmap='gray')
    matplotlib.pyplot.title(titulo)
    matplotlib.pyplot.axis('off')

def salva_vetor_imagens(vetor_caminhos_das_imagens, vetor_imagens, vetor_titulos):
    for caminho_da_imagem in vetor_caminhos_das_imagens:
        imagem = carrega_imagem(caminho_da_imagem)
        vetor_imagens.append(imagem)
        vetor_titulos.append(os.path.basename(caminho_da_imagem))



# HISTOGRAMA #
def calculo_histograma(imagem):
    # se imagem estiver em RGB, converte para tons de cinza
    if len(imagem.shape) == 3:
        imagem = imagem.convert('L')

    # iniciliza array do histograma com 256 valores de intensidade (0 a 255), todos com 0
    histograma = [0 for intensidade in range(256)]

    # percorre imagem pixel por pixel, contando a frequência de cada valor de intensidade
    for altura in range(imagem.shape[0]): # percorre as linhas da imagem
        for largura in range(imagem.shape[1]): # percorre as colunas da imagem
            valor_intensidade_pixel = imagem[altura, largura]
            histograma[valor_intensidade_pixel] += 1

    # plotagem do histograma
    matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(histograma)
    matplotlib.pyplot.show()



def main():

    # funções necessárias do tkinter
    root = Tk()
    root.withdraw()
    
    # salva o caminho de todas as imagens a serem carregadas
    vetor_caminhos_das_imagens = filedialog.askopenfilenames(title="Selecionar imagens", filetypes=[("Todos os arquivos", "*.mat;*.jpg;*.png")])
    
    # carregar e processar cada imagem
    vetor_imagens = []
    vetor_titulos = []
    salva_vetor_imagens(vetor_caminhos_das_imagens, vetor_imagens, vetor_titulos)
    
    # exibição das imagens
    if vetor_imagens:
        exibe_imagens(vetor_imagens, vetor_titulos)
    else:
        print("Erro. Não foi adicionada nenhuma imagem. Conserte a base de dados.")

if __name__ == "__main__":
    main()
