# PAI-DiagnosticoNAFLD
Projeto da matéria de Processamento e Análise de Imagens para diagnóstico de esteatose hepática não alcoólica (NAFLD) por meio de imagens de ultrassom.

<br>

### Alunos (G11):
- Pedro Corrêa Rigotto
- Samuel Luiz da Cunha Viana Cruz

<br>

### Cálculo do NT:
**NT = 1**
<br>
*(Local Binary Pattern (LPB), energia e entropia com raios = 1, 2, 4, 8)*

- **Matrícula:**
    - **Pedro:** 762281
    - **Samuel:** 762496

- **Soma =** 1524777

- **Mod 4 =** 1

<br>

# Roadmap

## 1. Menu/GUI:

### 1.1 Visualizar (Imagens + Histogramas):
- [x] Botão de leitura de imagens com os seguintes formatos aceitos:
  - [x] .mat
  - [x] PNG
  - [x] JPG
- [x] Suporte para qualquer resolução de imagem
- [x] Cálculo e exibição do histograma de tons de cinza

### 1.2 Recortar (ROIs):
- [x] Botão de recorte de regiões de interesse em uma imagem
- [x] Garantir que o usuário possa selecionar e salvar múltiplas ROIs

### 1.3 Visualizar (ROIs Geradas + Histogramas):
- [x] Botão de ler e visualizar as ROIs geradas
- [x] Calcular e exibir os respectivos histogramas para cada ROI

### 1.4 Calcular (GLCM + Descritores de Textura) de uma ROI:
- [x] Botão de cálculo de matrizes de co-ocorrência (GLCM) de uma ROI
- [ ] Exibir valores dos descritores de textura da GLCM calculada

### 1.5 Caracterizar (ROIs Geradas) através de Descritor de Textura:
- [x] Botão de caracterização de ROIs através do descritor de textura sorteado:<br>*(Local Binary Pattern (LPB), energia e entropia com raios = 1, 2, 4, 8)*
- [ ] Exibir valores dos descritores calculados

### 1.6 Classificar (Imagem):
- [x] Botão de classificação de imagem através da técnica selecionada
- [ ] Exibir a indicação da classe encontrada

<br>

## 2. Imagens
- [x] Ler e exibir imagens em tons de cinza
- [x] Implementar zoom
- [x] Exibir histogramas correspondentes

<br>

## 3. ROIs
- [x] Ler e exibir ROIs
- [x] Implementar zoom
- [x] Exibir histogramas correspondentes

<br>

## 4. Recorte de ROIs
- [x] Recorte de 2 ROIs de 28x28 pixels
  - [x] Região do Fígado
  - [x] Região do Córtex Renal
- [x] Quadrado (em cor verde) definido com o mouse 
- [x] Cálculo do índice hepatorenal:<br>*(HI) = (média_tons_cinza_ROI_fígado / média_tons_cinza_ROI_rim)*
- [x] Ajuste de tons de cinza da ROI do fígado, multiplicando cada valor de tom de cinza por (HI) e arredondando-os
- [x] Salvar somente a ROI do fígado em um diretório, o nome deve ser no formato **"ROI_nn_m"**<br>*(nn = número do paciente (0 a 54), m = número da imagem de ultrassom (0 a 9))*
- Observações:
  - Ver como localizar as regiões na seção de Materiais e Métodos do artigo (Figura 2);
  - A ROI do rim servirá como referência para a normalização da ROI do fígado, reduzindo diferenças entre imagens adquiridas com equipamentos distintos ou a influência de artefactos.

<br>

## 5. Planilha: ROIs para o Dataset
- [ ] Gerar 550 ROIs seguindo o item anterior
- [x] Armazenar em CSV:
  - [x] Nome do arquivo
  - [x] Classe<br>*(0-16 saudáveis, 17-54 esteatose)*
  - [x] Canto superior esquerdo (fígado e rim)
  - [x] Valor do (HI)

<br>

## 6. GLCMs Radiais
- [ ] Para cada ROI, calcular 4 GLCMs radiais Ci onde i = 1, 2, 4 e 8

<br>

## 7. Descritores de Haralick
- [ ] Calcular Entropia e Homogeneidade (Haralick) para cada GLCM Radial do item anterior<br>(4 * 2 características) para cada ROI

<br>

## 8. Local Binary Pattern (LBP)
- [ ] Calcular Local Binary Pattern (LBP), energia e entropia, com raios = 1, 2, 4, 8

<br>

## 9. Planilha: Características calculadas para uso no classificador
- [ ] Armazenar em CSV:
  - [ ] Nome do arquivo
  - [ ] Classe<br>*(0-16 saudáveis, 17-54 esteatose)*
  - [ ] Características calculadas


  pra fazer:
  consertar calculo dos descritores de haralic
  consertar front janela descritores