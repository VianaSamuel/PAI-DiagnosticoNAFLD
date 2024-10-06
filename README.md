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

## 1. Menu:

### 1.1 Leitura/Visualização de Imagens:
- [x] Leitura de imagens nos formatos:
  - [x] .mat
  - [x] PNG
  - [x] JPG
- [x] Suporte para qualquer resolução de imagem
- [ ] Cálculo e exibição do histograma de tons de cinza

### 1.2 Recorte Regiões de Interesse (ROIs):
- [ ] Recorte de regiões de interesse em uma imagem
- [ ] Garantir que o usuário possa selecionar e salvar múltiplas ROIs

### 1.3 Leitura/Visualização dos ROIs gerados:
- [ ] Ler e visualizar as ROIs geradas
- [ ] Calcular e exibir os respectivos histogramas para cada ROI

### 1.4 Cálculo de Matrizes de Co-ocorrência (GLCM) de uma ROI:
- [ ] Cálculo de matrizes de co-ocorrência (GLCM) de uma ROI
- [ ] Exibir valores dos descritores de textura da GLCM calculada

### 1.5 Caracterizaçaõ de ROIs usando Descritor de Textura:
- [ ] Caracterização de ROIs através do descritor de textura sorteado (Local Binary Pattern (LPB), energia e entropia com raios = 1, 2, 4, 8) e exibição de valores dos descritores calculados

### 1.6 Classificação de Imagem:
- [ ] Classificação de imagem através das técnica selecionada (Local Binary Pattern (LPB), energia e entropia com raios = 1, 2, 4, 8), indicando qual a classe encontrada

<br>

## 2. Imagens
- [ ] Ler e exibir imagens em tons de cinza
- [ ] Implementar zoom
- [ ] Exibir histogramas correspondentes

<br>

## 3. ROIs
- [ ] Ler e exibir ROIs
- [ ] Implementar zoom
- [ ] Exibir histogramas correspondentes

<br>

## 4. Geração de ROIs
- [ ] Recorte de 2 ROIs de 28x28 pixels
  - [ ] Região do Fígado
  - [ ] Região do Córtex Renal
- [ ] Quadrado (em cor verde) definido com o mouse 
- [ ] Cálculo do índice hepatorenal:<br>*(HI) = (média_tons_cinza_ROI_fígado / média_tons_cinza_ROI_rim)*
- [ ] Ajuste de tons de cinza da ROI do fígado, multiplicando cada valor de tom de cinza por (HI) e arredondando-os
- [ ] Salvar somente a ROI do fígado em um diretório, o nome deve ser no formato **"ROI_nn_m"**<br>*(nn = número do paciente (0 a 54), m = número da imagem de ultrassom (0 a 9))*
- Observações:
  - Ver como localizar as regiões na seção de Materiais e Métodos do artigo (Figura 2);
  - A ROI do rim servirá como referência para a normalização da ROI do fígado, reduzindo diferenças entre imagens adquiridas com equipamentos distintos ou a influência de artefactos.

<br>

## 5. Geração de ROIs para o Dataset
- [ ] Gerar 550 ROIs seguindo o item anterior
- [ ] Armazenar em CSV:
  - [ ] Nome do arquivo
  - [ ] Classe<br>*(0-16 saudáveis, 17-54 esteatose)*
  - [ ] Canto superior esquerdo (fígado e rim)
  - [ ] Valor do (HI)

<br>

## 6. GLCMs Radiais
- [ ] Para cada ROI, calcular 4 GLCMs radiais Ci onde i = 1, 2, 4 e 8

<br>

## 7. Descritores de Haralick
- [ ] Calcular Entropia e Homogeneidade (Haralick) para cada GLCM Radial do item anterior<br>(4 * 2 características) para cada ROI
