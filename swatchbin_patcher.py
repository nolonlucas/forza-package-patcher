import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import zipfile
import zlib
import shutil
import struct
import os
import threading

class SwatchbinPatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Swatchbin Patcher v6 — Forza Horizon 6")
        self.root.geometry("650x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        self.zip_path = tk.StringVar()
        self.swatchbin_path = tk.StringVar()
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="🖼  SWATCHBIN PATCHER v6",
                 font=("Segoe UI", 15, "bold"),
                 fg="#e94560", bg="#1a1a2e").pack(pady=(18, 4))
        tk.Label(self.root, text="Forza Horizon 6  •  baseado no v3 que funcionou",
                 font=("Segoe UI", 9), fg="#888", bg="#1a1a2e").pack()

        content = tk.Frame(self.root, bg="#1a1a2e", padx=24, pady=18)
        content.pack(fill="x")
        self.make_row(content, "📦  ZIP do jogo:", self.zip_path,
                      [("ZIP", "*.zip")], row=0)
        self.make_row(content, "🖼  Swatchbin novo:", self.swatchbin_path,
                      [("Swatchbin", "*.swatchbin"), ("Todos", "*.*")], row=1)
        content.grid_columnconfigure(1, weight=1)

        btn = tk.Frame(self.root, bg="#1a1a2e")
        btn.pack(pady=8)
        tk.Button(btn, text="🔄  Restaurar Backup",
                  font=("Segoe UI", 10), bg="#2a2a4a", fg="#aaa",
                  relief="flat", padx=14, pady=7, cursor="hand2",
                  command=self.restaurar).pack(side="left", padx=6)
        tk.Button(btn, text="⚡  Aplicar Patch",
                  font=("Segoe UI", 11, "bold"), bg="#e94560", fg="white",
                  relief="flat", padx=22, pady=7, cursor="hand2",
                  command=lambda: threading.Thread(target=self.patch, daemon=True).start()
                  ).pack(side="left", padx=6)

        tk.Label(self.root, text="LOG", font=("Segoe UI", 8, "bold"),
                 fg="#555", bg="#1a1a2e").pack(anchor="w", padx=24)
        self.log_box = scrolledtext.ScrolledText(
            self.root, height=10, bg="#0d0d1a", fg="#00ff88",
            font=("Consolas", 9), relief="flat", bd=0, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=24, pady=(2, 16))

    def make_row(self, parent, label, var, filetypes, row):
        tk.Label(parent, text=label, fg="#ccc", bg="#1a1a2e",
                 font=("Segoe UI", 10), width=20, anchor="w"
                 ).grid(row=row, column=0, sticky="w", pady=6)
        tk.Entry(parent, textvariable=var, bg="#0d0d1a",
                 fg="#00ff88", font=("Consolas", 9), relief="flat", bd=4
                 ).grid(row=row, column=1, sticky="ew", padx=4)
        tk.Button(parent, text="...", bg="#2a2a4a", fg="#ccc", relief="flat", padx=8,
                  command=lambda v=var, f=filetypes: self.browse(v, f)
                  ).grid(row=row, column=2, padx=(4, 0))

    def browse(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)

    def log(self, msg):
        self.log_box.configure(state="normal")
        if "[OK]" in msg:
            self.log_box.insert("end", msg + "\n", "ok")
            self.log_box.tag_config("ok", foreground="#00ff88")
        elif "[ERRO]" in msg:
            self.log_box.insert("end", msg + "\n", "erro")
            self.log_box.tag_config("erro", foreground="#e94560")
        elif "[AVISO]" in msg:
            self.log_box.insert("end", msg + "\n", "aviso")
            self.log_box.tag_config("aviso", foreground="#ffaa00")
        else:
            self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def patch(self):
        zip_path = self.zip_path.get().strip()
        swatch_path = self.swatchbin_path.get().strip()

        if not zip_path or not os.path.exists(zip_path):
            self.log("[ERRO] ZIP não encontrado!"); return
        if not swatch_path or not os.path.exists(swatch_path):
            self.log("[ERRO] Swatchbin não encontrado!"); return

        target_name = os.path.basename(swatch_path)
        self.log(f"Procurando '{target_name}' no ZIP...")

        target_info = None
        target_key = None
        with zipfile.ZipFile(zip_path, 'r') as z:
            for info in z.infolist():
                if info.filename.lower().endswith(target_name.lower()):
                    target_info = info
                    target_key = info.filename
                    self.log(f"[OK] Encontrado: {info.filename}")
                    self.log(f"     Comprimido original: {info.compress_size:,} bytes")
                    self.log(f"     CRC original: {hex(info.CRC)}")
                    break

        if not target_info:
            self.log(f"[ERRO] '{target_name}' não encontrado!"); return

        backup = zip_path + ".backup"
        if not os.path.exists(backup):
            shutil.copy2(zip_path, backup)
            self.log(f"[OK] Backup criado.")
        else:
            self.log(f"[AVISO] Backup já existe.")

        with open(swatch_path, "rb") as f:
            novo_bytes = f.read()

        new_crc = zlib.crc32(novo_bytes) & 0xFFFFFFFF
        orig_crc = target_info.CRC
        self.log(f"CRC original: {hex(orig_crc)}")
        self.log(f"CRC novo:     {hex(new_crc)}")

        with open(zip_path, "rb") as f:
            zip_data = bytearray(f.read())

        offset = target_info.header_offset
        orig_compress_size = target_info.compress_size
        orig_file_size = target_info.file_size

        fname_len = struct.unpack('<H', zip_data[offset+26:offset+28])[0]
        extra_len = struct.unpack('<H', zip_data[offset+28:offset+30])[0]
        data_start = offset + 30 + fname_len + extra_len

        compressed_original = bytes(zip_data[data_start:data_start + orig_compress_size])

        if new_crc == orig_crc:
            # Mesmo conteúdo — reutilizar bytes comprimidos originais
            self.log(f"[OK] CRC idêntico — reutilizando compressão original!")
            novo_compressed = compressed_original
        else:
            # Conteúdo diferente — recomprimir
            self.log(f"Recomprimindo...")
            melhor = None
            melhor_size = float('inf')
            melhor_desc = ""
            strategies = [("DEFAULT", zlib.Z_DEFAULT_STRATEGY), ("FILTERED", zlib.Z_FILTERED),
                          ("HUFFMAN_ONLY", zlib.Z_HUFFMAN_ONLY), ("RLE", zlib.Z_RLE)]
            for level in range(1, 10):
                for strat_name, strat in strategies:
                    c = zlib.compressobj(level=level, method=zlib.DEFLATED,
                                        wbits=-15, strategy=strat)
                    comp = c.compress(novo_bytes) + c.flush()
                    # Escolhe sempre o MENOR tamanho possivel. Qualquer resultado
                    # <= orig_compress_size cabe no espaco original com padding
                    # (sem precisar expandir o ZIP), entao menor e sempre melhor.
                    if len(comp) < melhor_size:
                        melhor_size = len(comp)
                        melhor = comp
                        melhor_desc = f"level={level} strat={strat_name}"
            novo_compressed = melhor
            self.log(f"Melhor: {melhor_desc}, tamanho: {len(novo_compressed):,} (diff: {len(novo_compressed)-orig_compress_size:+,})")

        novo_compress_size = len(novo_compressed)

        if novo_compress_size <= orig_compress_size:
            # Cabe no espaço original — padding com zeros
            padding = orig_compress_size - novo_compress_size
            zip_data[data_start:data_start+orig_compress_size] = novo_compressed + bytes(padding)

            struct.pack_into('<I', zip_data, offset+14, new_crc)
            struct.pack_into('<I', zip_data, offset+18, orig_compress_size)
            struct.pack_into('<I', zip_data, offset+22, len(novo_bytes))

            # Atualizar central directory
            cd_sig = b'PK\x01\x02'
            sp = 0
            while True:
                cd = zip_data.find(cd_sig, sp)
                if cd == -1: break
                fl = struct.unpack('<H', zip_data[cd+28:cd+30])[0]
                fn2 = zip_data[cd+46:cd+46+fl].decode('utf-8', errors='replace')
                if fn2 == target_key:
                    struct.pack_into('<I', zip_data, cd+16, new_crc)
                    struct.pack_into('<I', zip_data, cd+20, orig_compress_size)
                    struct.pack_into('<I', zip_data, cd+24, len(novo_bytes))
                    self.log(f"[OK] Central directory atualizado")
                    break
                sp = cd + 1

            with open(zip_path, "wb") as f:
                f.write(zip_data)
            self.log(f"\n[OK] ZIP salvo com tamanho preservado!")
            self.log("✅ Patch concluído! Teste o jogo.")
            self.root.after(0, lambda: messagebox.showinfo("Sucesso!", "Patch aplicado!\nTeste o jogo."))

        else:
            # Não cabe — expandir e atualizar TODOS os offsets corretamente
            size_diff = novo_compress_size - orig_compress_size
            self.log(f"[AVISO] Arquivo {size_diff:,} bytes maior. Expandindo ZIP...")

            # Substituir dados
            zip_data = (zip_data[:data_start] +
                        bytearray(novo_compressed) +
                        zip_data[data_start + orig_compress_size:])

            # Atualizar local header
            struct.pack_into('<I', zip_data, offset+14, new_crc)
            struct.pack_into('<I', zip_data, offset+18, novo_compress_size)
            struct.pack_into('<I', zip_data, offset+22, len(novo_bytes))

            # Atualizar TODOS os offsets no central directory
            cd_sig = b'PK\x01\x02'
            sp = 0
            while True:
                cd = zip_data.find(cd_sig, sp)
                if cd == -1: break
                fl = struct.unpack('<H', zip_data[cd+28:cd+30])[0]
                fn2 = zip_data[cd+46:cd+46+fl].decode('utf-8', errors='replace')
                cd_offset = struct.unpack('<I', zip_data[cd+42:cd+46])[0]

                if fn2 == target_key:
                    # Atualizar CRC e tamanhos do arquivo modificado
                    struct.pack_into('<I', zip_data, cd+16, new_crc)
                    struct.pack_into('<I', zip_data, cd+20, novo_compress_size)
                    struct.pack_into('<I', zip_data, cd+24, len(novo_bytes))
                    self.log(f"[OK] CD atualizado para arquivo modificado")
                elif cd_offset > offset:
                    # Deslocar offset de todos os arquivos APÓS o modificado
                    struct.pack_into('<I', zip_data, cd+42, cd_offset + size_diff)

                sp = cd + 1

            # Atualizar EOCD (End of Central Directory)
            eocd = zip_data.rfind(b'PK\x05\x06')
            if eocd != -1:
                cd_start = struct.unpack('<I', zip_data[eocd+16:eocd+20])[0]
                struct.pack_into('<I', zip_data, eocd+16, cd_start + size_diff)
                self.log(f"[OK] EOCD atualizado")

            with open(zip_path, "wb") as f:
                f.write(zip_data)

            self.log(f"[OK] ZIP expandido em {size_diff:,} bytes")
            self.log("✅ Patch concluído! Teste o jogo.")
            self.root.after(0, lambda: messagebox.showinfo("Sucesso!",
                f"Patch aplicado!\nZIP expandido em {size_diff:,} bytes.\n\nTeste o jogo!"))

    def restaurar(self):
        zip_path = self.zip_path.get().strip()
        if not zip_path:
            messagebox.showwarning("Aviso", "Selecione o ZIP primeiro!"); return
        backup = zip_path + ".backup"
        if not os.path.exists(backup):
            messagebox.showwarning("Aviso", "Backup não encontrado!"); return
        shutil.copy2(backup, zip_path)
        self.log("[OK] Backup restaurado!")
        messagebox.showinfo("OK", "Backup restaurado!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SwatchbinPatcher(root)
    root.mainloop()