# Pedro Corrêa Rigotto (762281)
# Samuel Luiz da Cunha Viana Cruz (762496)

# instalando bibliotecas necessárias
import subprocess
import sys
# subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-image"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "xgboost"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "keras"])

import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import scipy.io
import skimage
from PIL import Image
import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.widgets import Button, RectangleSelector
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import pandas as pd
import time
import threading
import tensorflow as tf
import keras as k
from keras import *
from tensorflow import *
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.regularizers import l2
from tensorflow.keras.models import Model
from keras.utils import to_categorical



rois_salva_na_hora = []
modelo = 0

#=============== PROCESSAMENTO DE IMAGENS ===============#
#=(CARREGAMENTO - imagens)
# retorna uma tupla que contém um vetor de imagens soltas e um vetor de imagens de cada paciente para uso na função exibir_imagens
def carregar_imagens():
    # salva os caminhos das imagens a serem carregadas
    vetor_caminhos_imagens = filedialog.askopenfilenames(title="Selecionar imagens", filetypes=[("Imagens ou Dataset", "*.mat;*.jpg;*.png")])
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
def carrega_imagem_jpg_png():
    caminho = filedialog.askopenfilenames(title="Selecionar imagens", filetypes=[("Imagens ou Dataset", "*.mat;*.jpg;*.png")])
    if not caminho:
        return None
    img_aberta = Image.open(caminho[0])
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
            for paciente in array_mat[0]: # array_mat[0][paciente][imagem]
                imagens_paciente = []
                for imagem in paciente:
                    if isinstance(imagem, np.ndarray):
                        imagem = imagem.tolist() # o paciente vem como ndarray por algum motivo. isso converte para lista
                    imagens_paciente.append(imagem)
                vetor_pacientes.append(imagens_paciente)

        # IMAGENS AVULSAS
        elif caminho.lower().endswith(('.png', '.jpg')):
            imagem_avulsa = carrega_imagem_jpg_png()
            vetor_pacientes[0].append(imagem_avulsa)

# carrega as imagens já preparadas das rois que foram salvas automaticamente na pasta delimitada e retorna 
# uma tupla com o vetor das imagens e caminhos das rois
def carrega_rois():
    vetor_rois = []
    diretorio = os.listdir('rois')
    for nome_arquivo_imagem in diretorio: # os.listdir é diferente do filedialog.askopenfilenames. ele retorna apenas o nome do arquivo, que tem que ser concatenado com o diretório
        if nome_arquivo_imagem.endswith(('.png', '.jpg')):
            caminho = os.path.join('rois', nome_arquivo_imagem)
            img_aberta = Image.open(caminho)
            if img_aberta.mode != 'L':  # se imagem estiver em RGB, converte para tons de cinza
                img_aberta = img_aberta.convert('L')
            img_aberta = np.array(img_aberta, dtype=np.uint8).tolist()
            vetor_rois.append((img_aberta, nome_arquivo_imagem))
    return vetor_rois
#=============== FIM PROCESSAMENTO DE IMAGENS ===============#



#=============== FUNÇÕES AUXILIARES ===============#
# seleciona o primeiro paciente e imagem e chama a função da janela recebida como parâmetro
def prepara_ids(vetor_pacientes, funcao):
    idx_paciente = -1,
    idx_imagem = -1,
    for i, paciente in enumerate(vetor_pacientes):
        if len(paciente) != 0:
            idx_paciente = i
            idx_imagem = 0
            break
    if idx_paciente == -1:
        tk.messagebox.showerror("Erro", "Nenhuma imagem.")
        return
    if funcao:
        funcao(vetor_pacientes, idx_paciente, idx_imagem)

# plota a janela para uso dos classificadores
def plota_janela_classificador(classificador):
    janela_classificador = tk.Toplevel()
    janela_classificador.title("Treino do Classificador")
    janela_classificador.geometry("275x200")
    threading.Thread(target=classificador, args=(janela_classificador,)).start()


#=============== FIM FUNÇÕES AUXILIARES ===============#



#=============== CÁLCULO DO HISTOGRAMA ===============#
#=(CALCULO - histograma)
def calcula_histograma(imagem):
    # iniciliza array do histograma com 256 valores de intensidade (0 a 255), todos com 0
    histograma = [0 for _ in range(256)]
    # percorre imagem pixel por pixel, contando a frequência de cada valor de intensidade
    for x in range(len(imagem)): # percorre as linhas (altura) da imagem
        for y in range(len(imagem[x])): # percorre as colunas (largura) da imagem
            valor_intensidade_pixel = imagem[x][y]
            histograma[valor_intensidade_pixel] += 1
    return histograma

#=(CALCULO - média do histograma)
def media_histograma(histograma, imagem):
    if not imagem:
        return -1
    altura = len(imagem)
    largura = len(imagem[0])
    soma = 0
    numero_pixels = altura * largura
    for i in range(256):
        soma += histograma[i] * i
    return soma / numero_pixels

#=(CÁLCULO - normalização do histograma)
def normalizar_histograma(histograma):
    numero_pixels = sum(histograma)
    if numero_pixels == 0:
        tk.messagebox.showerror("Erro", f"Histograma com 0 pixels.\n{histograma}")
        return None
    histograma_normalizado = []
    for intensidade in histograma:
        histograma_normalizado.append(intensidade / numero_pixels)
    return histograma_normalizado
#=============== FIM CÁLCULO DO HISTOGRAMA ===============#



#=============== CÁLCULO DO ÍNDICE HEPATORENAL ===============#
#=(CALCULO - hi)
def calculo_hi(roi_figado_img, roi_rim_img):
    histograma_figado = calcula_histograma(roi_figado_img)
    histograma_rim = calcula_histograma(roi_rim_img)
    media_tons_cinza_roi_figado = media_histograma(histograma_figado, roi_figado_img)
    print(f"media de tons de cinza figado: {media_tons_cinza_roi_figado}")
    media_tons_cinza_roi_rim = media_histograma(histograma_rim, roi_rim_img)
    print(f"media de tons de cinza rim: {media_tons_cinza_roi_rim}")
    if media_tons_cinza_roi_rim == 0:
        media_tons_cinza_roi_rim = 0.0000000001 # para não ter divisão por 0
    return media_tons_cinza_roi_figado / media_tons_cinza_roi_rim

#=(AJUSTE - tons de cinza da roi do fígado)
def ajusta_roi(roi_figado, hi):
    roi_figado_ajustada = roi_figado
    for x in range(len(roi_figado)):
        for y in range(len(roi_figado[x])):
            pixel_ajustado = round(roi_figado_ajustada[x][y] * hi) # multiplica cada valor de tom de cinza por HI e arredonda
            if pixel_ajustado > 255:
                pixel_ajustado = 255
            roi_figado_ajustada[x][y] = pixel_ajustado
    return roi_figado_ajustada
#=============== FIM CÁLCULO DO ÍNDICE HEPATORENAL ===============#



#=============== CÁLCULO DE GLCMs + DESCRITORES DE HARALICK ===============#
#=(CALCULO - GLCMs radiais + descritores de haralick)
def glcm_biblioteca(imagem):
    raios =  (1, 2, 4, 8)
    glcms = skimage.feature.graycomatrix(imagem, 
                                        distances=raios, 
                                        angles=[np.radians(0), np.radians(45), np.radians(90), np.radians(135)],
                                        levels=256,
                                        symmetric=True,
                                        normed=True
                                        )
    homogeneidades = skimage.feature.graycoprops(glcms, 'homogeneity') # [raio][angulo]
    energias = skimage.feature.graycoprops(glcms, 'energy')
    angulos = len(homogeneidades)
    homogeneidades_tratadas = [sum(homogeneidades[i])/angulos for i in range(angulos)] # faz a media das homogeneidades dos angulos
    energias_tratadas = [sum(energias[i])/angulos for i in range(angulos)]
    # antes: glcms = [i][j][raio][angulo]
    glcms = soma_angulos(glcms) # depois: glcms = [raio][i][j]
    entropias = calcula_entropias(glcms)
    return (glcms, entropias, homogeneidades_tratadas, energias_tratadas)

#=(AUXILIAR - cálculo de entropia)
def calcula_entropias(glcms): # precisa da glcm estar no formato [raio][i][j]
    entropias = []
    for raio, glcm in enumerate(glcms):
        entropia = 0
        for i in range(256):
            for j in range(256):
                pixel = glcm[i][j]
                if pixel != 0:
                    entropia += pixel * np.log2(pixel)
        entropias.append(-entropia)
    return entropias

#=(AUXILIAR - soma ângulos da GLCM)
def soma_angulos(glcms): # a glcm vem dividida para cada raio e angulo. aqui a gente soma
    # glcms[i][j][raio][angulo] -> glcms[raio][i][j]
    glcms_finais = [[[0 for _ in range(256)] for _ in range(256)] for _ in range(4)] # junta as glcms de mesmo raio em uma só. começa com 0 para somar depois
    for raio in range(4):
        for i in range(256):
            for j in range(256):
                for angulo in range(4):
                    glcms_finais[raio][i][j] += glcms[i][j][raio][angulo]
    return glcms_finais
 


#=============== CÁLCULO DO LOCAL BINARY PATTERN (LBP) ===============#
def calcula_lbp(roi): # retorna um vetor no formato [raio (só tem 1)][descritor][raio_glcm][i][j]
    print("lbps")
    raio = 1
    num_vizinhos = 8
    lbps = []
    print("calculando lbp")
    lbp = skimage.feature.local_binary_pattern(np.array(roi), num_vizinhos, raio, method='uniform')  # cálculo do LBP
    lbp = lbp.astype(np.uint8) # conversão de LBP para inteiros (para obter histograma)
    print("descritores")
    descritores_lbp = glcm_biblioteca(lbp)
    lbps.append(descritores_lbp)
    return lbps
#=============== FIM CÁLCULO DO LOCAL BINARY PATTERN (LBP) ===============#



#=============== DATASET ROIS EM .CSV ===============#
def atualizar_dataset_rois(nome_arquivo, idx_paciente, roi_figado, roi_rim, valor_hi):
    # tratamento de erro se não tiver algum dos dados
    if not nome_arquivo or not roi_figado or not roi_rim or valor_hi == -1:
        tk.messagebox.showerror("Erro", f"Erro: dados inconsistentes.\nnome_arquivo: {nome_arquivo}\nidx_paciente: {idx_paciente}\nroi_figado: {roi_figado}\nroi_rim: {roi_rim}\nvalor_hi: {valor_hi}")  
        return
    
    # configura nome do arquivo e verifica se o mesmo já existe
    arquivo_csv = "dataset_rois.csv"
    existe_arquivo = os.path.isfile(arquivo_csv)
    dados_csv = []

    # se arquivo não existe, cria o cabeçalho
    if not existe_arquivo:
        dados_csv.append(["nome_arquivo", "classe", "x_figado", "y_figado", "x_rim", "y_rim", "valor_hi"])
    # se arquivo existe, carrega dados existentes
    if existe_arquivo:
        with open(arquivo_csv, mode='r', newline='') as arquivo:
            leitor_csv = csv.reader(arquivo)
            dados_csv = list(leitor_csv)

    # cantos superiores esquerdos dos rois: formato [xmin, ymin, xmax, ymax]
    x_figado = roi_figado[0]
    y_figado = roi_figado[1]
    x_rim = roi_rim[0]
    y_rim = roi_rim[1]

    # classe do paciente
    classe_paciente = None
    if idx_paciente <= 16: # 0 = saudável
        classe_paciente = "0"
    else: # 1 = doente
        classe_paciente = "1"

    # verifica se já existe a entrada para esta imagem específica do paciente no dataset
    duplicado = False
    for i, linha in enumerate(dados_csv):
        # sobrescreve os novos dados caso tenha encontrado a entrada já existente ao iterar sobre as linhas
        if linha[0] == nome_arquivo:
            dados_csv[i] = [nome_arquivo, classe_paciente, x_figado, y_figado, x_rim, y_rim, valor_hi]
            duplicado = True
            break

    # caso não exista a entrada, adiciona na lista
    if not duplicado:
        dados_csv.append([nome_arquivo, classe_paciente, x_figado, y_figado, x_rim, y_rim, valor_hi])

    # reescrita/atualização do CSV
    with open(arquivo_csv, mode='w', newline='') as arquivo:
        escritor_csv = csv.writer(arquivo)
        escritor_csv.writerows(dados_csv)
#=============== FIM DATASET ROIS EM .CSV ===============#



#=============== .CSV PARA USO NO CLASSIFICADOR ===============#
def gerar_planilha_classificador():
    # le todas as rois em arquivos
    # gera os descritores de haralick e lbp para cada roi
    # adiciona os dados ao csv
    
    # configura nome do arquivo e verifica se o mesmo já existe
    arquivo_csv = "planilha_pra_uso_no_classificador.csv"
    dados_csv = []

    dados_csv.append(["nome_arquivo", 
                      "classe",
                      "roi_entropia_1",
                      "roi_entropia_2",
                      "roi_entropia_4",
                      "roi_entropia_8",
                      "roi_homogeneidade_1",
                      "roi_homogeneidade_2",
                      "roi_homogeneidade_4",
                      "roi_homogeneidade_8",
                      "lbp_entropia_1",
                      "lbp_entropia_2",
                      "lbp_entropia_4",
                      "lbp_entropia_8",
                      "lbp_energia_1",
                      "lbp_energia_2",
                      "lbp_energia_4",
                      "lbp_energia_8",
                      ])

    rois = carrega_rois()
    if not rois:
        tk.messagebox.showerror("Erro", "Nenhuma ROI salva.")
        return

    for roi in rois:
        # calcula descritores
        descritores = glcm_biblioteca(roi[0])
        # calcula lbp e seus descritores
        lbp = calcula_lbp(roi[0])
        # classe do paciente - 0: saudável, 1: doente
        idx_paciente = int(roi[1].split("_")[1])
        classe_paciente = 0 if idx_paciente <= 16 else 1
        # salva no csv
        dados_csv.append([roi[1],
                          classe_paciente,
                          descritores[1][0],
                          descritores[1][1],
                          descritores[1][2],
                          descritores[1][3],
                          descritores[2][0],
                          descritores[2][1],
                          descritores[2][2],
                          descritores[2][3],
                          lbp[0][1][0],
                          lbp[0][1][1],
                          lbp[0][1][2],
                          lbp[0][1][3],
                          lbp[0][3][0],
                          lbp[0][3][1],
                          lbp[0][3][2],
                          lbp[0][3][3]
                        ])

    # reescrita/atualização do CSV
    with open(arquivo_csv, mode='w', newline='') as arquivo:
        escritor_csv = csv.writer(arquivo)
        escritor_csv.writerows(dados_csv)
        tk.messagebox.showinfo("Resultado", "Dados salvos no CSV corretamente.")
#=============== FIM .CSV PARA USO NO CLASSIFICADOR ===============#



#=============== GRÁFICOS PARA MOBILENET ===============#
def graficos_mobilenet(vetor_acuracia, vetor_acuracia_val):
    numero_epocas = range(len(vetor_acuracia))

    plt.figure(figsize=(14, 6))

    # gráfico - treino
    plt.subplot(1, 2, 1)
    plt.plot(numero_epocas, vetor_acuracia, label="Acurácia de Treino", color="black")
    plt.title("Acurácia de Treino")
    plt.xlabel("Épocas")
    plt.ylabel("Acurácia")
    plt.legend()
    plt.grid(True)

    # gráfico - validação
    plt.subplot(1, 2, 2)
    plt.plot(numero_epocas, vetor_acuracia_val, label="Acurácia de Validação", color="black")
    plt.title("Acurácia de Validação")
    plt.xlabel("Épocas")
    plt.ylabel("Acurácia")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
#=============== FIM GRÁFICOS PARA MOBILENET ===============#



#=============== JANELA - BOTÃO 1 (imagens + histogramas) ===============#
def janela_imagens_e_histogramas(vetor_pacientes, idx_paciente=-1, idx_imagem=-1, titulo = ""):
    def prepara_a_tela():
        nonlocal idx_paciente
        nonlocal idx_imagem
        nonlocal titulo
        # limpa o gráfico anterior
        imagem_histograma[0].cla()
        imagem_histograma[1].cla()
        # exibe a nova imagem e o histograma dela
        if(len(vetor_pacientes[idx_paciente]) > 0): # se tem alguma imagem para exibir
            janela_histograma_exibe_uma(vetor_pacientes[idx_paciente][idx_imagem], titulo)
        else:
            tk.messagebox.showerror("Erro", "Nenhuma imagem.")
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
        nonlocal titulo 
        titulo = f"Paciente #{idx_paciente} - Imagem #{idx_imagem+1}"
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
        nonlocal titulo 
        titulo = f"Paciente #{idx_paciente} - Imagem #{idx_imagem+1}"
        prepara_a_tela()

    def janela_histograma_exibe_uma(imagem, titulo=""):
        # exibe a imagem à esquerda
        imagem_histograma[0].imshow(imagem, cmap='gray')
        imagem_histograma[0].set_title(titulo)
        imagem_histograma[0].axis('off')
        # calcula o histograma
        histograma = calcula_histograma(imagem)
        histograma[0] = 0 # o fundo da imagem de ultrassom é preto. isso tira do histograma o pico do fundo, para normalizar a altura dos dados
        # exibe o histograma à direita
        imagem_histograma[1].plot(histograma, color='black')
        imagem_histograma[1].set_title('Histograma')
        imagem_histograma[1].set_xlim([0, 255])
        imagem_histograma[1].set_xlabel('Intensidade')
        imagem_histograma[1].set_ylabel('Frequência')

    def on_key(event): # trocar de imagem via setas do teclado
        if event.key == 'right':
            navegar_avancar(event)
        elif event.key == 'left':
            navegar_retroceder(event)
        elif event.key == 'r':  # reseta o zoom da imagem
            reseta_zoom(None)

    # define a nova imagem a ser exibida quando o usuario marca a regiao para zoom
    def aplica_zoom(evento_clicar, evento_soltar):
        # coordenadas do clique e do soltar
        x1, y1 = evento_clicar.xdata, evento_clicar.ydata
        x2, y2 = evento_soltar.xdata, evento_soltar.ydata
        # novos limites da imagem a ser exibida
        imagem_histograma[0].set_xlim(min(x1, x2), max(x1, x2))
        imagem_histograma[0].set_ylim(max(y1, y2), min(y1, y2))
        # atualiza
        figura.canvas.draw_idle()
    
    def reseta_zoom(event):
        # volta os limites da imagem para a imagem inteira
        imagem_histograma[0].set_xlim(0, imagem_histograma[0].get_images()[0].get_array().shape[1])
        imagem_histograma[0].set_ylim(imagem_histograma[0].get_images()[0].get_array().shape[0], 0)
        # atualiza
        figura.canvas.draw_idle()

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
    figura.canvas.manager.set_window_title("Imagem + Histograma")
    # cria os botões. pode navegar via teclado ou os botões
    localizacao_botao_avancar = plt.axes([0.2, 0.04, 0.1, 0.075])
    localizacao_botao_retroceder = plt.axes([0.1, 0.04, 0.1, 0.075])
    botao_avancar = plt.Button(localizacao_botao_avancar, '>')
    botao_retroceder = plt.Button(localizacao_botao_retroceder, '<')
    botao_avancar.on_clicked(navegar_avancar)
    botao_retroceder.on_clicked(navegar_retroceder)
    localizacao_botao_reseta = plt.axes([0.35, 0.04, 0.1, 0.075])
    botao_reseta = Button(localizacao_botao_reseta, 'Resetar Zoom')
    botao_reseta.on_clicked(reseta_zoom)

    prepara_a_tela()

    # criação do seletor para zoom
    seletor = RectangleSelector(imagem_histograma[0], aplica_zoom,
                                useblit=True,
                                button=[1, 3],  # 1: esquerdo, 3: direito
                                minspanx=5, minspany=5,
                                spancoords='pixels',
                                interactive=True,
                                props=dict(facecolor='none', edgecolor='red', alpha=1.0, fill=False)) # deixa o retângulo transparente
    seletor.set_active(True)

    # insere a figura na tela
    plt.tight_layout()
    plt.show()
#=============== FIM JANELA - BOTÃO 1 (imagens + histogramas) ===============#



#=============== JANELA - BOTÃO 2 (recorte de rois) ===============#
def janela_selecionar_rois(vetor_pacientes, idx_paciente=-1, idx_imagem=-1):
    # estrutura da roi: [xmin, ymin, xmax, ymax]
    global roi_figado, roi_rim, roi_atual, retangulo_figado, retangulo_rim, texto_hi, hi
    texto_hi = ""
    ax = None
    figura = None
    roi_figado = None
    roi_rim = None
    roi_atual = None
    retangulo_figado = None
    retangulo_rim = None
    hi = -1

    def evento_selecionar_roi(evento):
        global roi_figado, roi_rim, retangulo_figado, retangulo_rim, texto_hi, hi
        if roi_atual and evento.inaxes == ax:
            imagem = vetor_pacientes[idx_paciente][idx_imagem]
            altura_imagem = len(imagem)
            largura_imagem = len(imagem[0])
            largura = 28

            # calcula as coordenadas do clique na imagem em relação à posição do clique na tela
            x_img = int(evento.xdata)
            y_img = int(evento.ydata)
            # corrige se a roi estiver fora da imagem
            x_img = max(0, min(x_img, largura_imagem - largura))
            y_img = max(0, min(y_img, altura_imagem - largura))
            
            # salva as coordenadas da roi // ISSO É SALVO NA SELEÇÃO DA ROI E NÃO AO SALVAR A ROI
            if not os.path.exists('rois'): # cria o arquivo e pasta se não existir
                os.makedirs('rois')
            with open('rois/coords.txt', 'w') as arquivo_coordenadas:
                arquivo_coordenadas.write(f'{idx_paciente},{idx_imagem},{x_img},{y_img}\n')
                arquivo_coordenadas.close()
            
            # roi_figado é [xmin, ymin, xmax, ymax]
            if roi_atual == 'figado':
                roi_figado = [x_img, y_img, min(x_img + largura, largura_imagem), min(y_img + largura, altura_imagem)]
                if retangulo_figado:
                    retangulo_figado.remove()
                retangulo_figado = plt.Rectangle((x_img, y_img), largura, largura, fill=False, edgecolor='green', linewidth=2)
                ax.add_patch(retangulo_figado)
            elif roi_atual == 'rim':
                roi_rim = [x_img, y_img, min(x_img + largura, largura_imagem), min(y_img + largura, altura_imagem)]
                if retangulo_rim:
                    retangulo_rim.remove()
                retangulo_rim = plt.Rectangle((x_img, y_img), largura, largura, fill=False, edgecolor='green', linewidth=2)
                ax.add_patch(retangulo_rim)

            # plotagem da média do histograma e cálculo do índice hepatorenal (HI)
            if roi_figado and roi_rim:
                # extrai as regiões de interesse. roi é [xmin, ymin, xmax, ymax] (coordenadas)
                xmin_figado, ymin_figado, xmax_figado, ymax_figado = roi_figado[0], roi_figado[1], roi_figado[2], roi_figado[3] 
                xmin_rim, ymin_rim, xmax_rim, ymax_rim = roi_rim[0], roi_rim[1], roi_rim[2], roi_rim[3]
                # faz o split da matriz, selecionando apenas as partes dentro dos limites especificados
                roi_figado_img = [linha[xmin_figado:xmax_figado] for linha in imagem[ymin_figado:ymax_figado]]
                roi_rim_img = [linha[xmin_rim:xmax_rim] for linha in imagem[ymin_rim:ymax_rim]]
                hi = calculo_hi(roi_figado_img, roi_rim_img)
                texto_hi = f'Índice Hepatorrenal:\n{hi:.2f}'
            else:
                texto_hi = ""
            
            if len(ax.texts) > 0:
                # se o objeto do texto existir, só renomeia
                ax.texts[0].set_text(texto_hi)
            else:
                # adiciona o texto a tela
                ax.text(0.4, -0.1, texto_hi, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes, fontsize=12)

            figura.canvas.draw()


    def selecionar_figado(event):
        global roi_atual
        roi_atual = 'figado'

    def selecionar_rim(event):
        global roi_atual
        roi_atual = 'rim'

    def salvar_rois(event):
        global hi
        if roi_figado == None:
            tk.messagebox.showwarning("Aviso", "Selecione a ROI do fígado.")
            return
        # prepara a pasta
        if not os.path.exists('rois'):
            os.makedirs('rois')
        # converte a imagem para o formato certo para salvar
        imagem = np.array(vetor_pacientes[idx_paciente][idx_imagem])
        if imagem.dtype != np.uint8:
            imagem = (imagem / imagem.max() * 255).astype(np.uint8)
        if(idx_paciente > 0):
            idx_paciente_corrigido = idx_paciente - 1 # correção para index começando em 0
            idx_paciente_formatado = f"{idx_paciente_corrigido:02}" # formatação com 2 dígitos
            # salva as rois
            roi_figado_cortada = imagem[roi_figado[1]:roi_figado[3], roi_figado[0]:roi_figado[2]] # [xmin, ymin, xmax, ymax]
            roi_figado_cortada = ajusta_roi(roi_figado_cortada, hi)
            roi_figado_imagem = Image.fromarray(roi_figado_cortada)
            nome_arquivo_roi = f'ROI_{idx_paciente_formatado}_{idx_imagem}.png'
            roi_figado_imagem.save(f'rois/{nome_arquivo_roi}')
            atualizar_dataset_rois(nome_arquivo_roi, idx_paciente_corrigido, roi_figado, roi_rim, hi)
            tk.messagebox.showinfo("Sucesso", "ROI salva com sucesso.")
        else:
            global rois_salva_na_hora
            rois_salva_na_hora.append([roi_figado, roi_rim, hi])

    def navegar_avancar(event):
        nonlocal idx_paciente
        nonlocal idx_imagem
        if idx_imagem < len(vetor_pacientes[idx_paciente]) - 1: # se nao é a ultima imagem daquela fonte
            idx_imagem += 1
        elif idx_paciente < len(vetor_pacientes) - 1: # se nao é a ultima fonte
            idx_imagem = 0
            idx_paciente += 1
        exibe_figura()
    
    def navegar_retroceder(event):
        nonlocal idx_paciente
        nonlocal idx_imagem
        if idx_imagem > 0:  # se não é a primeira imagem daquela fonte
            idx_imagem -= 1
        elif idx_paciente > 0:  # se não é a primeira fonte
            if len(vetor_pacientes[idx_paciente-1]) != 0:
                idx_paciente -= 1
                idx_imagem = len(vetor_pacientes[idx_paciente]) - 1
            else:
                idx_imagem = 0
        exibe_figura()

    # atualiza a e imagem e os retangulos das rois quando troca de imagem
    def exibe_figura():
        global retangulo_figado, retangulo_rim, roi_figado, roi_rim, texto_hi
        ax.clear()
        imagem = vetor_pacientes[idx_paciente][idx_imagem]
        altura = len(imagem)
        largura = len(imagem[0])
        ax.imshow(imagem, cmap='gray', extent=[0, largura, altura, 0])
        titulo = f"Selecionar ROIs - Paciente {idx_paciente}, Imagem {idx_imagem+1}"
        ax.set_title(titulo)
        retangulo_figado = None # reseta as rois
        retangulo_rim = None
        roi_figado = None
        roi_rim = None
        figura.canvas.draw()

    # EXECUÇÃO DA FUNÇÃO
    figura, ax = plt.subplots(figsize=(8, 6)) # cria a figura
    exibe_figura() # mostra a primeira imagem
    figura.canvas.mpl_connect('button_press_event', evento_selecionar_roi) # conecta o evento de clique
    figura.canvas.manager.set_window_title("Recorte de ROIs")
    
    # adicionar botões
    ax_botao_figado = plt.axes([0.6, 0.01, 0.1, 0.075])
    ax_botao_rim = plt.axes([0.71, 0.01, 0.1, 0.075])
    ax_botao_salvar = plt.axes([0.82, 0.01, 0.1, 0.075])
    ax_botao_avancar = plt.axes([0.2, 0.01, 0.1, 0.075])
    ax_botao_retroceder = plt.axes([0.1, 0.01, 0.1, 0.075])

    botao_figado = Button(ax_botao_figado, 'Fígado')
    botao_rim = Button(ax_botao_rim, 'Rim')
    botao_salvar = Button(ax_botao_salvar, 'Salvar')
    botao_avancar = Button(ax_botao_avancar, '>')
    botao_retroceder = Button(ax_botao_retroceder, '<')

    botao_figado.on_clicked(selecionar_figado)
    botao_rim.on_clicked(selecionar_rim)
    botao_salvar.on_clicked(salvar_rois)
    botao_avancar.on_clicked(navegar_avancar)
    botao_retroceder.on_clicked(navegar_retroceder)

    plt.subplots_adjust(bottom=0.15)
    plt.show()
#=============== FIM JANELA - BOTÃO 2 (recorte de rois) ===============#



#=============== JANELA - BOTÃO 3 (rois + histogramas) ===============#
def janela_rois_e_histogramas(vetor_rois=None, idx_roi=-1, roi_atual=None, titulo = ""):
    def prepara_a_tela():
        nonlocal roi_atual
        nonlocal idx_roi
        nonlocal titulo
        # limpa o gráfico anterior
        imagem_histograma[0].cla()
        imagem_histograma[1].cla()
        # exibe a nova imagem e o histograma dela
        if(len(vetor_rois) > 0): # se tem alguma imagem para exibir
            roi_atual = vetor_rois[idx_roi]
            janela_rois_exibe_uma()
        else:
            tk.messagebox.showerror("Erro", "Nenhuma imagem.")
            plt.close(figura)
            return
        # atualiza a tela
        plt.draw()
        
    def navegar_avancar(event):
        nonlocal idx_roi
        if idx_roi < len(vetor_rois) - 1: # se nao é a ultima roi
            idx_roi += 1
        prepara_a_tela()
    
    def navegar_retroceder(event):
        nonlocal idx_roi
        if idx_roi > 0:  # se não é a primeira roi
            idx_roi -= 1
        prepara_a_tela()

    def janela_rois_exibe_uma():
        nonlocal roi_atual
        imagem_roi = roi_atual[0]
        nome_arquivo_roi = roi_atual[1]
        # exibe a imagem à esquerda
        imagem_histograma[0].imshow(imagem_roi, cmap='gray')
        imagem_histograma[0].set_title(nome_arquivo_roi)
        imagem_histograma[0].axis('off')
        # calcula o histograma
        histograma = calcula_histograma(imagem_roi)
        # exibe o histograma à direita
        imagem_histograma[1].plot(histograma, color='black')
        imagem_histograma[1].set_title('Histograma')
        imagem_histograma[1].set_xlim([0, 255])
        imagem_histograma[1].set_xlabel('Intensidade')
        imagem_histograma[1].set_ylabel('Frequência')

    def on_key(event): # trocar de imagem via setas do teclado
        if event.key == 'right':
            navegar_avancar(event)
        elif event.key == 'left':
            navegar_retroceder(event)
        elif event.key == 'r':  # reseta o zoom da imagem
            reseta_zoom(None)

    # define a nova imagem a ser exibida quando o usuario marca a regiao para zoom
    def aplica_zoom(evento_clicar, evento_soltar):
        # coordenadas do clique e do soltar
        x1, y1 = evento_clicar.xdata, evento_clicar.ydata
        x2, y2 = evento_soltar.xdata, evento_soltar.ydata
        # novos limites da imagem a ser exibida
        imagem_histograma[0].set_xlim(min(x1, x2), max(x1, x2))
        imagem_histograma[0].set_ylim(max(y1, y2), min(y1, y2))
        # atualiza
        figura.canvas.draw_idle()
    
    def reseta_zoom(event):
        # volta os limites da imagem para a imagem inteira
        imagem_histograma[0].set_xlim(0, imagem_histograma[0].get_images()[0].get_array().shape[1])
        imagem_histograma[0].set_ylim(imagem_histograma[0].get_images()[0].get_array().shape[0], 0)
        # atualiza
        figura.canvas.draw_idle()

    # cria a figura e os subplots
    figura, imagem_histograma = plt.subplots(1, 2, figsize=(10, 5)) 

    # conecta os eventos de botões do teclado. especificamente, navegação via setas
    figura.canvas.mpl_connect('key_press_event', on_key)
    figura.canvas.manager.set_window_title("ROI + Histograma")

    # cria os botões. pode navegar via teclado ou os botões
    localizacao_botao_avancar = plt.axes([0.2, 0.04, 0.1, 0.075])
    localizacao_botao_retroceder = plt.axes([0.1, 0.04, 0.1, 0.075])
    botao_avancar = plt.Button(localizacao_botao_avancar, '>')
    botao_retroceder = plt.Button(localizacao_botao_retroceder, '<')
    botao_avancar.on_clicked(navegar_avancar)
    botao_retroceder.on_clicked(navegar_retroceder)
    localizacao_botao_reseta = plt.axes([0.35, 0.04, 0.1, 0.075])
    botao_reseta = Button(localizacao_botao_reseta, 'Resetar Zoom')
    botao_reseta.on_clicked(reseta_zoom)

    vetor_rois = carrega_rois()
    prepara_a_tela()

    # criação do seletor para zoom
    seletor = RectangleSelector(imagem_histograma[0], aplica_zoom,
                                useblit=True,
                                button=[1, 3],  # 1: esquerdo, 3: direito
                                minspanx=5, minspany=5,
                                spancoords='pixels',
                                interactive=True,
                                props=dict(facecolor='none', edgecolor='red', alpha=1.0, fill=False)) # deixa o retângulo transparente
    seletor.set_active(True)

    # insere a figura na tela
    plt.tight_layout()
    plt.show()
#=============== FIM JANELA - BOTÃO 3 (rois + histogramas) ===============#



#=============== JANELA - BOTÃO 4 (GLCM + descritores de textura) ===============#
def janela_descritores_haralick(vetor_rois=None, idx_roi=0, roi_atual=None, descritores=None, descritores_lbp=None):
    descritores = []
    existe_texto = False
    def prepara_a_tela():
        nonlocal roi_atual
        nonlocal idx_roi
        nonlocal existe_texto
        if(len(vetor_rois) > 0): # se tem alguma roi salva
            roi_atual = vetor_rois[idx_roi]
            calcula_descritores()
            texto_descritores =  f"ROI: {idx_roi}\n\n"
            texto_descritores_lbp = f"Descritores LBP: "
            if len(descritores) <= 0:
                tk.messagebox.showerror("Erro", "Zero descritores.")
                return
            for idx_raio in range(len(descritores[0])): # descritores = [descritor][raio]
                # descritores normais
                raio = 2**idx_raio
                entropia = descritores[1][idx_raio]
                homogeneidade = descritores[2][idx_raio]
                texto_descritores += f"Raio {raio}:\n"
                texto_descritores += f"Homogeneidade: {homogeneidade}\n"
                texto_descritores += f"Entropia: {entropia}\n\n"
                # descritores lbp
                texto_descritores_lbp += f"\n\nRaio {raio}:\n"
                texto_descritores_lbp += f"Entropia: {descritores_lbp[0][1][idx_raio]}"
                texto_descritores_lbp += f"\nEnergia: {descritores_lbp[0][3][idx_raio]}"
            if existe_texto:
                # se o objeto do texto existir, só renomeia
                ax.texts[0].set_text(texto_descritores)
                ax.texts[1].set_text(texto_descritores_lbp)
            else:
                # adiciona o texto a tela
                ax.text(0.01, 0.9, texto_descritores, horizontalalignment='left', verticalalignment='top', transform=ax.transAxes, fontsize=12)
                ax.text(0.6, 0.9, texto_descritores_lbp, horizontalalignment='left', verticalalignment='top', transform=ax.transAxes, fontsize=12)
                existe_texto = True 
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            tk.messagebox.showerror("Erro", "Nenhuma ROI salva.")
            return
        # atualiza a tela
        figura.canvas.draw_idle()
        
    def navegar_avancar(event):
        nonlocal idx_roi, descritores
        if idx_roi < len(vetor_rois) - 1: # se nao é a ultima roi
            idx_roi += 1
        prepara_a_tela()
    
    def navegar_retroceder(event):
        nonlocal idx_roi, descritores
        if idx_roi > 0:  # se não é a primeira roi
            idx_roi -= 1
        prepara_a_tela()

    def calcula_descritores():
        nonlocal roi_atual, descritores, descritores_lbp
        imagem_roi = roi_atual[0]
        nome_arquivo_roi = roi_atual[1]
        descritores = glcm_biblioteca(imagem_roi)
        descritores_lbp = calcula_lbp(imagem_roi)
    
    def on_key(event): # trocar de roi via setas do teclado
        if event.key == 'right':
            navegar_avancar(event)
        elif event.key == 'left':
            navegar_retroceder(event)

    # cria a figura e os subplots
    figura, ax = plt.subplots(figsize=(10, 8)) 

    # conecta os eventos de botões do teclado. especificamente, navegação via setas
    figura.canvas.mpl_connect('key_press_event', on_key)
    figura.canvas.manager.set_window_title("Descritores")

    # cria os botões. pode navegar via teclado ou os botões
    localizacao_botao_avancar = plt.axes([0.2, 0.14, 0.1, 0.075])
    localizacao_botao_retroceder = plt.axes([0.1, 0.14, 0.1, 0.075])
    botao_avancar = plt.Button(localizacao_botao_avancar, '>')
    botao_retroceder = plt.Button(localizacao_botao_retroceder, '<')
    botao_avancar.on_clicked(navegar_avancar)
    botao_retroceder.on_clicked(navegar_retroceder)

    vetor_rois = carrega_rois()
    prepara_a_tela()

    # insere a figura na tela
    plt.show()
#=============== FIM JANELA - BOTÃO 4 (GLCM + descritores de textura) ===============#



#=============== BOTÃO 5 (Classificador Raso - XGBoost) ===============#
def roda_xgboost(janela_classificador):
    label_status = ttk.Label(janela_classificador, text="Rodando XGBoost, por favor, aguarde.", wraplength=480, anchor="w", justify="left")
    label_status.pack(pady=30)
    csv = 'planilha_pra_uso_no_classificador.csv'
    df = pd.read_csv(csv)
    inicio_cronometro = time.time() # conta o tempo do treino
    resultados_xgboost = cross_validation_xgboost(df)
    fim_cronometro = time.time()
    tempo_total_treino = fim_cronometro - inicio_cronometro
    print(f"\n55 rodadas de testes para cross validation concluídas em {tempo_total_treino:.2f} segundos. Resultados médios:")
    print(f" - Acurácia        {resultados_xgboost[0]:.2f}")
    print(f" - Especificidade  {resultados_xgboost[1]:.2f}")
    print(f" - Sensibilidade   {resultados_xgboost[2]:.2f}")
    print(f"\nMatriz de Confusão:\n{np.sum(resultados_xgboost[3], axis=0)}")
    label_status['text'] = (
        "Resultados:\n"
        f"Acurácia:        {resultados_xgboost[0]:.2f}\n"
        f"Especificidade:  {resultados_xgboost[1]:.2f}\n"
        f"Sensibilidade:   {resultados_xgboost[2]:.2f}\n"
        f"Matriz de Confusão:\n{np.sum(resultados_xgboost[3], axis=0)}\n"
        f"Tempo total de treino: {tempo_total_treino:.2f} segundos"
    )


# faz a cross validation, rotacionando pacientes como o conjunto teste, e roda o classificador raso xgboost
def cross_validation_xgboost(df):
    metricas = [0, 0, 0, []] # acuracia, especificidade, sensibilidade, matriz_confusao
    resultados = [0, 0, 0, 0] # verdadeiro_negativo, falso_positivo, falso_negativo, verdadeiro_positivo
    hiperparametros = { 'learning_rate': [0.01, 0.1, 0.3], 
                        'max_depth': [3, 6] }
    
    for paciente_teste in range(55):
        # separa treino e teste com apenas 1 paciente como teste
        str_paciente = ""
        if paciente_teste < 10:
            str_paciente = "0" + str(int(paciente_teste))
        else:
            str_paciente = str(int(paciente_teste))
        df_teste = df[df['nome_arquivo'].str.startswith(f'ROI_{str_paciente}_')]
        df_treino = df[~df['nome_arquivo'].str.startswith(f'ROI_{str_paciente}_')]
        
        # separa os dataframes em X sendo atributos e y a classe
        X_treino = df_treino.iloc[:, 2:] # matriz com tudo depois da classe
        X_teste = df_teste.iloc[:, 2:]
        y_treino = df_treino['classe'] # só a classe
        y_teste = df_teste['classe']

        X_treino = X_treino.to_numpy()
        X_teste = X_teste.to_numpy()
        y_treino = y_treino.to_numpy()
        y_teste = y_teste.to_numpy()
        
        # executa o treinamento do xgboost, roda o grid search, e faz a predição do conjunto de teste
        #   parâmetro device setado para fazer rodar em paralelo na gpu
        classificador = XGBClassifier(eval_metric='logloss') 
        gridsearch = GridSearchCV(estimator=classificador, param_grid=hiperparametros, cv=3, scoring='accuracy')
        inicio_cronometro = time.time() # conta o tempo do treino
        #classificador.fit(X_treino, y_treino)
        gridsearch.fit(X_treino, y_treino)
        fim_cronometro = time.time()
        tempo_atual_treino = fim_cronometro - inicio_cronometro
        print(f"Fold {paciente_teste+1} levou {tempo_atual_treino:.2f} segundos")
        #y_pred = classificador.predict(X_teste)
        y_pred = gridsearch.predict(X_teste)
        
        # acha as métricas
        matriz_confusao = confusion_matrix(y_teste, y_pred, labels=[0, 1])
        metricas[3].append(matriz_confusao)

        # faz a especificidade e sensibilidade na mão
        verdadeiro_negativo, falso_positivo, falso_negativo, verdadeiro_positivo = matriz_confusao.ravel()
        resultados[0] += verdadeiro_negativo
        resultados[1] += falso_positivo
        resultados[2] += falso_negativo
        resultados[3] += verdadeiro_positivo
    
    # faz as métricas na mão, contando a soma dos valores de todas as rodadas
    total = resultados[0] + resultados[1] + resultados[2] + resultados[3]
    acuracia = (resultados[0] + resultados[3]) / total
    metricas[0] = acuracia
    especificidade = resultados[0] / (resultados[0] + resultados[1])
    metricas[1] = especificidade
    sensibilidade = resultados[3] / (resultados[3] + resultados[2])
    metricas[2] = sensibilidade
    
    
    return metricas
#=============== FIM BOTÃO 5 (Classificador Raso - XGBoost) ===============#



#=============== BOTÃO 6 (Classificador Profundo - MobileNet) ===============#
def roda_mobilenet(janela_classificador):
    label_status = ttk.Label(janela_classificador, text="Rodando MobileNet, por favor, aguarde.", wraplength=480, anchor="w", justify="left")
    label_status.pack(pady=30)
    tempo_total_treino = 0
    # prepara os dataframes
    csv = 'planilha_pra_uso_no_classificador.csv'
    df = pd.read_csv(csv)

    vetor_rois = carrega_rois()
    dicionario_rois = {nome: imagem for imagem, nome in vetor_rois}
    X_teste = None
    y_teste = None
    X_treino = None
    y_treino = None

    def prepara_treino_teste(paciente_teste):
        nonlocal X_teste, y_teste, X_treino, y_treino
        str_paciente = ""
        if paciente_teste < 10:
            str_paciente = "0" + str(int(paciente_teste))
        else:
            str_paciente = str(int(paciente_teste))
        df_teste = df[df['nome_arquivo'].str.startswith(f'ROI_{str_paciente}_')]
        df_treino = df[~df['nome_arquivo'].str.startswith(f'ROI_{str_paciente}_')]

        # pega a imagem do dicionario de rois e roda ela pelo preprocessamento, depois salva no X.
        X_teste = np.array([ preprocessamento_mobilenet( dicionario_rois[ row['nome_arquivo']]) for _, row in df_teste.iterrows()])
        y_teste = df_teste['classe']
        X_treino = np.array([ preprocessamento_mobilenet( dicionario_rois[ row['nome_arquivo']]) for _, row in df_treino.iterrows()])
        y_treino = df_treino['classe']

    # pega o modelo pré-treinado
    modelo_base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    for camada in modelo_base.layers: # as camadas treinadas pelo imagenet não devem ser treinadas novamente
        camada.trainable = False
    
    # adiciona as camadas treináveis para fazer o fine-tuning
    modelo_temp = modelo_base.output # começa pela última do outro modelo
    modelo_temp = GlobalAveragePooling2D()(modelo_temp) # pooling 
    modelo_temp = Dense(100, activation='relu', kernel_regularizer=l2(0.01))(modelo_temp) # adiciona outra camada densa. inclui um regularizador para evitar overfitting
    modelo_temp = Dropout(0.5)(modelo_temp) # desliga alguns nós para evitar overfitting
    saida_modelo_temp = Dense(2, activation='softmax')(modelo_temp) # saída com 2 classes (saudável/esteatose)
    modelo_final = Model(inputs=modelo_base.input, outputs=saida_modelo_temp)

    # define algumas coisas primeiro
    epocas = 7
    paciencia = 3
    modelo_final.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']) # loss: categorical_crossentropy, sparse_categorical_crossentropy, mse
    var_callbacks = [callbacks.EarlyStopping(monitor='val_loss', patience=paciencia, restore_best_weights=True)] # para o treino se a função não melhorar
    pesos_das_classes = {0: 1.0, 1: 2.0} # peso maior para a classe 1 (esteatose), porque tem menos dados

    # roda o cross validation
    historicos = []
    matrizes_confusao = []
    relatorios = []
    inicio_cronometro = time.time() # conta o tempo do treino
    pacientes = list(range(55)) # faz o paciente a ser o conjunto de teste um paciente aleatório, para não ter viés sobre a ordem do conjunto teste
    rng = np.random.default_rng(seed=int(time.time()))
    rng.shuffle(pacientes)
    for _ in range(55):
        paciente_teste = pacientes.pop()
        prepara_treino_teste(paciente_teste)
        # USAR TO_CATEGORICAL SE TROCAR PARA CATEGORICAL_CROSSENTROPY. trocar apenas no modelo_final.fit
        y_treino_cat = to_categorical(y_treino)  if y_treino.size > 0 else y_treino # one hot encoder
        y_teste_cat = to_categorical(y_teste) if y_teste.size > 0 else y_teste
        if y_treino.size == 0 or y_teste.size == 0:
            print(f"Não há dados suficientes para o paciente {paciente_teste}.")
            print(f"Treino: {y_treino.size} Teste: {y_teste.size}")
            input()
        historicos.append(modelo_final.fit(X_treino, y_treino_cat, epochs=epocas, batch_size=32, validation_data=(X_teste, y_teste_cat), callbacks=var_callbacks, class_weight=pesos_das_classes)) # salva o histórico do treino para plotar depois
        y_previsto = modelo_final.predict(X_teste) # faz os testes
        y_previsto = np.argmax(y_previsto, axis=1) # a classe com maior probabilidade é a previsão
        relatorios.append(classification_report(y_teste, y_previsto, zero_division=0))
        matrizes_confusao.append(confusion_matrix(y_teste, y_previsto, labels=[0, 1]))
    fim_cronometro = time.time()
    tempo_atual_treino = fim_cronometro - inicio_cronometro
    tempo_total_treino += tempo_atual_treino
    print(f"Treino levou {tempo_atual_treino:.2f} segundos")

    # salva resultados em arquivo
    with open('resultados_mobilenet.txt', 'w') as arquivo_resultados:
        for i, relatorio in enumerate(relatorios):
            arquivo_resultados.write(f"\n\nPaciente {i+1}:\n{relatorio}")
            arquivo_resultados.write(f"\nMatriz de Confusao:\n{matrizes_confusao[i]}")
            arquivo_resultados.write(f"\nHistorico de Treino:\n{historicos[i].history}\n\n")
    label_status['text'] = (
        f"Resultados salvos em 'resultados_mobilenet.txt'\n"
        f"Tempo total de treino: {tempo_total_treino:.2f} segundos\n"
    )

    # prepara os dados para plotagem do gráfico
    vetor_acuracia_val = []
    vetor_acuracia = []
    for historico in historicos:
        acuracias_val = historico.history['val_accuracy']
        acuracias = historico.history['accuracy']
        for loss in acuracias_val:
            vetor_acuracia_val.append(loss)
        for acuracia in acuracias:
            vetor_acuracia.append(acuracia)
    graficos_mobilenet(vetor_acuracia, vetor_acuracia_val)

    global modelo
    modelo = modelo_final
    global rois_salva_na_hora
    if(len(rois_salva_na_hora > 0)):
        resultado = modelo.predict(preprocessamento_mobilenet(rois_salva_na_hora[0][0]))
        print(f"Resultado da imagem salva na hora: {resultado}")


def preprocessamento_mobilenet(imagem_vetor):
    imagem = np.array(imagem_vetor, dtype=np.uint8)
    imagem = tf.expand_dims(imagem, axis=-1)
    imagem = tf.image.resize(imagem, (224, 224))
    imagem = tf.image.grayscale_to_rgb(imagem)
    imagem = k.applications.imagenet_utils.preprocess_input(imagem) # normaliza a imagem
    return imagem
#=============== FIM BOTÃO 6 (Classificador Profundo - MobileNet) ===============#



#=============== GUI ===============#
def menu_principal():
    # config: janela, resolução, estilização
    root = tk.Tk()
    root.title("PAI-DIagnosticoNAFLD")
    root.geometry("400x550")
    style = ttk.Style()
    style.theme_use('clam')

    # frame: menu principal
    menu_principal = ttk.Frame(root)
    menu_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    menu_principal.columnconfigure(0, weight=1)

    vetor_pacientes = carregar_imagens()

    # botões
    btn0 = tk.Button(menu_principal, text="Visualizar (Imagens + Histogramas)", command=lambda:{prepara_ids(vetor_pacientes=vetor_pacientes, funcao=prepara_ids(vetor_pacientes=vetor_pacientes, funcao=janela_imagens_e_histogramas))}, width=50, height=2)
    btn0.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    btn1 = tk.Button(menu_principal, text="Recortar (ROIs)", command=lambda:{prepara_ids(vetor_pacientes=vetor_pacientes, funcao=janela_selecionar_rois)}, width=50, height=2)
    btn1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    btn2 = tk.Button(menu_principal, text="Visualizar (ROIs Geradas + Histogramas)", command=janela_rois_e_histogramas, width=50, height=2)
    btn2.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    btn3 = tk.Button(menu_principal, text="Exibir (Descritores de Textura [Haralick + LBPs]) de uma ROI", command=janela_descritores_haralick, width=50, height=2)
    btn3.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
    btn4 = tk.Button(menu_principal, text="Salvar (Características [Haralick + LBPs]) em Planilha .CSV", command=gerar_planilha_classificador, width=50, height=2)
    btn4.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
    btn5 = tk.Button(menu_principal, text="Classificador Raso (XGBoost)", command=lambda:{plota_janela_classificador(roda_xgboost)}, width=50, height=2)
    btn5.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
    btn6 = tk.Button(menu_principal, text="Classificador Profundo (MobileNet)", command=lambda:{plota_janela_classificador(roda_mobilenet)}, width=50, height=2)
    btn6.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
    #btn7 = tk.Button(menu_principal, text="Carregar Imagem", command=carrega_imagem_jpg_png, width=50, height=2)
    #btn7.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

    # nomes e matrículas
    pedro = tk.Label(menu_principal, text="Pedro Corrêa Rigotto (762281)", anchor="center")
    pedro.grid(row=7, column=0, pady=(20, 0), sticky="nsew")
    samuel = tk.Label(menu_principal, text="Samuel Luiz da Cunha Viana Cruz (762496)", anchor="center")
    samuel.grid(row=8, column=0, pady=(0, 10), sticky="nsew")
    
    root.mainloop()
#=============== FIM GUI ===============#



#=============== MAIN ===============# 
if __name__ == "__main__":
    menu_principal()
#=============== FIM MAIN ===============#