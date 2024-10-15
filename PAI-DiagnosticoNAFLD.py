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
from tkinter import ttk, filedialog
from matplotlib.widgets import Button, RectangleSelector



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
            for paciente in array_mat[0]: # array_mat[0][paciente][imagem]
                imagens_paciente = []
                for imagem in paciente:
                    if isinstance(imagem, np.ndarray):
                        imagem = imagem.tolist() # o paciente vem como ndarray por algum motivo. isso converte para lista
                    imagens_paciente.append(imagem)
                vetor_pacientes.append(imagens_paciente)

        # IMAGENS AVULSAS
        elif caminho.lower().endswith(('.png', '.jpg')):
            imagem_avulsa = carrega_imagem_jpg_png(caminho)
            vetor_pacientes[0].append(imagem_avulsa)
#=============== FIM PROCESSAMENTO DE IMAGENS ===============#



#=============== CÁLCULO DO HISTOGRAMA ===============#
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


#=(AUXILIAR - prepara id's)
# seleciona o primeiro paciente e imagem e chama a função da janela recebida como parametro
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
    funcao(vetor_pacientes, idx_paciente, idx_imagem)
#=============== FIM CÁLCULO DO HISTOGRAMA ===============#



#=============== JANELA - BOTÃO 1 (imagens + histograma) ===============#
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
        histograma = calculo_histograma(imagem)
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
#=============== FIM JANELA - BOTÃO 1 (imagens + histograma) ===============#



#=============== JANELA - BOTÃO 2 (recorte de rois) ===============#
def janela_selecionar_rois(vetor_pacientes, idx_paciente=-1, idx_imagem=-1):
    global roi_figado, roi_rim, roi_atual, retangulo_figado, retangulo_rim
    ax = None
    figura = None
    roi_figado = None
    roi_rim = None
    roi_atual = None
    retangulo_figado = None
    retangulo_rim = None

    def evento_selecionar_roi(evento):
        global roi_figado, roi_rim, retangulo_figado, retangulo_rim
        if roi_atual and evento.inaxes == ax:
            imagem = vetor_pacientes[idx_paciente][idx_imagem]
            altura_imagem = len(imagem[0])
            largura_imagem = len(imagem)

            # calcula as coordenadas do clique na imagem em relação à posição do clique na tela
            x_img = int(evento.xdata)
            y_img = int(evento.ydata)

            largura = 28

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

            figura.canvas.draw()


    def selecionar_figado(event):
        global roi_atual
        roi_atual = 'figado'

    def selecionar_rim(event):
        global roi_atual
        roi_atual = 'rim'

    def salvar_rois(event):
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
        idx_paciente_corrigido = idx_paciente - 1 # correção para index começando em 0
        idx_paciente_formatado = f"{idx_paciente_corrigido:02}" # formatação com 2 dígitos
        # salva as rois
        roi_figado_imagem = Image.fromarray(imagem[roi_figado[1]:roi_figado[3], roi_figado[0]:roi_figado[2]])
        roi_figado_imagem.save(f'rois/ROI_{idx_paciente_formatado}_{idx_imagem}.png')
        # roi_rim_imagem = Image.fromarray(imagem[roi_rim[1]:roi_rim[3], roi_rim[0]:roi_rim[2]])
        # roi_rim_imagem.save(f'rois/ROI_{idx_paciente_formatado}_{idx_imagem}.png')
        tk.messagebox.showinfo("Sucesso", "ROI salva com sucesso.")

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
        exibe_figura()

    # atualiza a e imagem e os retangulos das rois quando troca de imagem
    def exibe_figura():
        global retangulo_figado, retangulo_rim, roi_figado, roi_rim
        ax.clear()
        ax.imshow(vetor_pacientes[idx_paciente][idx_imagem], cmap='gray')
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
    btn0 = tk.Button(menu_principal, text="Visualizar (Imagens + Histogramas)", command=lambda:{prepara_ids(vetor_pacientes=vetor_pacientes, funcao=prepara_ids(vetor_pacientes=vetor_pacientes, funcao=janela_imagens_e_histogramas))}, width=50, height=2)
    btn0.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    btn1 = tk.Button(menu_principal, text="Recortar (ROIs)", command=lambda:{prepara_ids(vetor_pacientes=vetor_pacientes, funcao=janela_selecionar_rois)}, width=50, height=2)
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