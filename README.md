# 🎮 Forza Horizon 6 — ZIP Asset Patcher Tools

> **Ferramentas de baixo nível para substituição de assets internos nos ZIPs da franquia Forza, sem corromper a validação interna do engine ForzaTech.**

---

## ⚠️ Por que essas ferramentas existem?

O engine **ForzaTech** (usado em Forza Horizon e Forza Motorsport) empacota os assets de cada carro — modelos 3D, texturas, luzes, presets — dentro de arquivos **ZIP internos**. Porém, ao contrário de um ZIP comum, o jogo executa uma **validação estrutural rigorosa** ao carregar esses arquivos:

- Verifica o **CRC-32** de cada entrada no Local Header e no Central Directory
- Valida os **tamanhos comprimidos e descomprimidos** em ambos os cabeçalhos
- Verifica os **offsets absolutos** de todas as entradas no Central Directory
- Verifica o **offset do Central Directory** no End of Central Directory (EOCD)

Se qualquer um desses valores estiver inconsistente — mesmo que o conteúdo do arquivo esteja correto — **o jogo crasha imediatamente** ou rejeita o asset silenciosamente.

Ferramentas convencionais de ZIP (WinRAR, 7-Zip, Python `zipfile`) **reconstroem** o arquivo ao salvar, alterando offsets e invalidando a estrutura esperada pelo jogo. Por isso foi necessário desenvolver um **patcher in-place** que edita o ZIP diretamente em memória, byte a byte, preservando toda a estrutura original intacta.

---

## 🛠️ Ferramentas incluídas

### 1. `modelbin_patcher.py` — Neon Underglow Patcher

Permite injetar até **três arquivos simultaneamente** no ZIP de um carro:

| Arquivo | Função |
|---|---|
| `*.modelbin` | Modelo 3D do neon undercarriage (geometria + materiais emissivos) |
| `Lights.bin` | Definição das fontes de luz do neon |
| `LightPresets.bin` | Presets de cor e intensidade das luzes |

**Funcionalidades:**
- Checkboxes individuais para selecionar quais arquivos aplicar
- Compressão DEFLATE multi-nível (testa levels 1–9, escolhe o menor que caiba no espaço original)
- Padding automático com zeros quando o arquivo novo é menor que o original
- Expansão controlada do ZIP quando o arquivo novo é maior (com aviso de risco de crash)
- Atualização correta de todos os offsets do Central Directory e EOCD após expansão
- Backup automático antes de qualquer modificação

---

### 2. `swatchbin_patcher.py` — Swatchbin Patcher

Substitui arquivos **`.swatchbin`** (paletas de textura/cor) no ZIP do jogo.

**Funcionalidades:**
- Busca o arquivo-alvo por nome dentro do ZIP (sem distinção de maiúsculas)
- Compara CRC-32 antes de recomprimir: se o conteúdo for idêntico, reutiliza os bytes comprimidos originais sem reprocessamento
- Testa **36 combinações** de nível de compressão (1–9) × estratégia DEFLATE (`DEFAULT`, `FILTERED`, `HUFFMAN_ONLY`, `RLE`) para encontrar a melhor compressão possível
- Suporte completo a expansão do ZIP com atualização dos offsets
- Restauração de backup com um clique

---

## 🔬 Como o patch funciona (detalhes técnicos)

```
ZIP original (em memória como bytearray):
┌─────────────────────────────────────────────────────────┐
│  Local Header (PK\x03\x04)                              │
│    ├─ CRC-32             ← atualizado                   │
│    ├─ Compressed size    ← preservado ou atualizado     │
│    └─ Uncompressed size  ← atualizado                   │
│  [dados comprimidos]     ← substituídos in-place        │
│  ...outros arquivos...                                  │
│  Central Directory (PK\x01\x02)                         │
│    ├─ CRC-32             ← atualizado                   │
│    ├─ Compressed size    ← atualizado                   │
│    ├─ Uncompressed size  ← atualizado                   │
│    └─ Offset do header   ← corrigido para todos os      │
│                             arquivos após o modificado  │
│  End of Central Directory (PK\x05\x06)                  │
│    └─ Offset do CD       ← corrigido se ZIP expandiu   │
└─────────────────────────────────────────────────────────┘
```

### Caso 1 — Arquivo novo ≤ espaço original
O arquivo novo é comprimido e **ocupa exatamente o mesmo espaço** do original no ZIP, com padding de bytes nulos no final. Nenhum offset é alterado. O jogo não percebe nenhuma diferença estrutural — apenas o conteúdo mudou.

### Caso 2 — Arquivo novo > espaço original
O ZIP precisa ser expandido. Neste caso:
1. Os bytes novos são inseridos na posição correta
2. Todos os **offsets do Central Directory** de entradas que vêm depois do arquivo modificado são incrementados pelo `size_diff`
3. O **offset do Central Directory** no EOCD também é incrementado
4. O usuário é avisado sobre o risco de crash (o ForzaTech pode rejeitar ZIPs expandidos em alguns casos)

---

## 📋 Requisitos

- Python **3.8+**
- Biblioteca padrão apenas (`tkinter`, `zipfile`, `zlib`, `struct`, `shutil`) — **sem dependências externas**

---

## 🚀 Como usar

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/forza-zip-patcher.git
cd forza-zip-patcher

# Execute o patcher de modelbins/neon
python modelbin_patcher.py

# Execute o patcher de texturas/swatchbin
python swatchbin_patcher.py
```

### Fluxo básico

1. Selecione o **ZIP do carro** extraído do jogo
2. Selecione o(s) **arquivo(s) modificado(s)** que deseja injetar
3. Clique em **⚡ Aplicar Patch**
4. Um backup `.backup` é criado automaticamente antes de qualquer modificação
5. Teste o jogo — em caso de problema, clique em **🔄 Restaurar Backup**

---

## 📁 Estrutura do repositório

```
forza-zip-patcher/
├── modelbin_patcher.py    # Neon Underglow Patcher (modelbin + lights + lightpresets)
├── swatchbin_patcher.py   # Swatchbin Patcher (texturas/paletas de cor)
└── README.md
```

---

## 🧠 Contexto e motivação

Este projeto nasceu durante o modding de um **BMW M4WP 21** em Forza Horizon 6, com o objetivo de adicionar **iluminação neon interna** ao veículo usando o ForzaTech Studio. 

Durante o processo ficou evidente que nenhuma ferramenta disponível publicamente era capaz de substituir assets dentro dos ZIPs do ForzaTech sem corromper a estrutura interna. Qualquer tentativa com ferramentas convencionais resultava em crash imediato do jogo.

A solução foi engenharia reversa do formato ZIP conforme implementado pelo ForzaTech, resultando nessas ferramentas de edição direta em memória.

---

## ⚠️ Aviso

Este projeto é feito para fins educacionais e de modding pessoal. Use por sua conta e risco. Sempre mantenha backups dos arquivos originais do jogo.

---

## 📄 Licença

MIT License — sinta-se livre para usar, modificar e distribuir.
