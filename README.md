# Forza Package Patcher

Ferramenta desenvolvida em Python para automatizar a aplicação de modificações em pacotes `Model.bin` e `SWATCH.BIN` utilizados por jogos da franquia **Forza Horizon**.

O objetivo do projeto é eliminar o processo manual de extração, substituição e reconstrução desses pacotes, automatizando todas as etapas através de uma interface gráfica simples e da integração com o **QuickBMS**.

---

# Visão Geral

Durante o desenvolvimento de modificações para jogos da franquia Forza Horizon, diversos recursos do jogo encontram-se armazenados em arquivos compactados como:

- Model.bin
- SWATCH.BIN

A alteração manual desses arquivos normalmente exige diversas etapas repetitivas:

- localizar o pacote correto;
- extrair seu conteúdo;
- substituir os arquivos modificados;
- reconstruir o pacote;
- remover arquivos temporários.

Este projeto automatiza completamente esse fluxo de trabalho, reduzindo erros humanos e tornando o processo muito mais rápido.

---

# Funcionalidades

## Model.bin Patcher

Permite modificar arquivos **Model.bin** através de um processo totalmente automatizado.

Fluxo executado:

1. Seleção do arquivo Model.bin.
2. Extração automática utilizando QuickBMS.
3. Criação da estrutura temporária.
4. Localização dos arquivos do patch.
5. Substituição apenas dos recursos modificados.
6. Reconstrução automática do pacote.
7. Limpeza dos arquivos temporários.
8. Exibição do resultado ao usuário.

---

## SWATCH.BIN Patcher

Responsável pela aplicação de modificações em pacotes de texturas.

O processo segue praticamente o mesmo fluxo do Model.bin, adaptado para arquivos SWATCH.BIN.

Etapas:

- Extração
- Substituição dos arquivos
- Reconstrução
- Limpeza automática

---

# Interface

A aplicação utiliza Tkinter para fornecer uma interface gráfica simples.

O usuário apenas precisa:

- selecionar o pacote original;
- selecionar a pasta do patch;
- iniciar o processo.

Todo o restante é realizado automaticamente.

---

# Tecnologias Utilizadas

- Python 3
- Tkinter
- QuickBMS
- pathlib
- shutil
- subprocess
- tempfile
- os

---

# Estrutura do Projeto

```
Forza Package Patcher
│
├── modelbin_patcher.py
├── swatchbin_patcher.py
├── README.md
├── LICENSE
└── .gitignore
```

---

# Arquitetura

A aplicação foi dividida em dois módulos independentes.

## modelbin_patcher.py

Responsável pelo processamento de arquivos Model.bin.

Funções principais:

- Interface gráfica
- Seleção de arquivos
- Extração do pacote
- Aplicação do patch
- Reconstrução
- Limpeza

---

## swatchbin_patcher.py

Responsável pelo processamento dos arquivos SWATCH.BIN.

Implementa o mesmo fluxo de trabalho adaptado para pacotes de texturas.

---

# Fluxo de Processamento

```
Usuário
    │
    ▼
Seleciona o pacote
    │
    ▼
QuickBMS extrai o conteúdo
    │
    ▼
Arquivos modificados são copiados
    │
    ▼
Pacote é reconstruído
    │
    ▼
Arquivos temporários removidos
    │
    ▼
Processo finalizado
```

---

# Integração com QuickBMS

A ferramenta utiliza o QuickBMS como mecanismo responsável pela extração e reconstrução dos pacotes.

Todo o processo é executado automaticamente em segundo plano.

O usuário não precisa utilizar o QuickBMS manualmente.

---

# Tratamento de Arquivos Temporários

Durante a execução são criados diretórios temporários para:

- extração;
- processamento;
- substituição dos arquivos;
- reconstrução do pacote.

Após a conclusão, esses diretórios são removidos automaticamente.

---

# Tratamento de Erros

O programa realiza verificações durante todas as etapas do processo.

Entre elas:

- existência dos arquivos;
- validade dos diretórios;
- localização do QuickBMS;
- erros durante a extração;
- falhas durante a reconstrução.

Sempre que possível são exibidas mensagens amigáveis ao usuário.

---

# Requisitos

- Python 3.10+
- QuickBMS
- Script BMS compatível com o formato do pacote
- Sistema Operacional Windows

---

# Como Utilizar

1. Execute o programa.

2. Escolha o arquivo:

```
Model.bin
```

ou

```
SWATCH.BIN
```

3. Selecione a pasta contendo os arquivos modificados.

4. Clique em **Patch**.

5. Aguarde a conclusão.

---

# Vantagens

- Interface simples
- Processo automatizado
- Menor risco de erros durante a substituição dos arquivos
- Elimina etapas manuais repetitivas
- Organização automática dos arquivos temporários

---

# Objetivo

Este projeto foi desenvolvido para simplificar o fluxo de trabalho durante a modificação de recursos utilizados por jogos da franquia Forza Horizon, automatizando tarefas que normalmente exigem múltiplas ferramentas e diversas etapas manuais.

---

# Licença

Este projeto está licenciado sob a licença MIT.

---

# Autor

Desenvolvido por **Lucas (nolonlucas)**

GitHub:

https://github.com/nolonlucas
