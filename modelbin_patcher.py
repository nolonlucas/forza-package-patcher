import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile
import struct
import shutil
import zlib
import os
import threading

# ═══════════════════════════════════════════════════════════════
#  NEON UNDERGLOW PATCHER - Forza Horizon 6
#  Interface gráfica para patch in-place de arquivos no ZIP
# ═══════════════════════════════════════════════════════════════

class NeonPatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Underglow Patcher — Forza Horizon 6")
        self.root.geometry("780x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        # Variáveis
        self.zip_path = tk.StringVar()
        self.modelbin_path = tk.StringVar()
        self.lights_path = tk.StringVar()
        self.lightpresets_path = tk.StringVar()

        self.use_modelbin = tk.BooleanVar(value=True)
        self.use_lights = tk.BooleanVar(value=True)
        self.use_lightpresets = tk.BooleanVar(value=True)

        self.build_ui()

    def build_ui(self):
        # ── Header ──────────────────────────────────────────────
        header = tk.Frame(self.root, bg="#16213e", pady=14)
        header.pack(fill="x")

        tk.Label(header, text="🌈  NEON UNDERGLOW PATCHER",
                 font=("Segoe UI", 16, "bold"),
                 fg="#e94560", bg="#16213e").pack()
        tk.Label(header, text="Forza Horizon 6  •  in-place ZIP patcher",
                 font=("Segoe UI", 9),
                 fg="#888", bg="#16213e").pack()

        # ── Main content ────────────────────────────────────────
        content = tk.Frame(self.root, bg="#1a1a2e", padx=24, pady=16)
        content.pack(fill="both", expand=True)

        # ZIP do carro
        self.make_file_row(content,
            label="📦  ZIP do Carro",
            var=self.zip_path,
            filetypes=[("ZIP files", "*.zip")],
            required=True,
            row=0)

        tk.Frame(content, bg="#2a2a4a", height=1).grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=10)

        tk.Label(content, text="ARQUIVOS PARA INJETAR",
                 font=("Segoe UI", 8, "bold"),
                 fg="#555", bg="#1a1a2e").grid(
                 row=2, column=0, columnspan=3, sticky="w", pady=(0,8))

        # Undercarriage modelbin
        self.make_file_row(content,
            label="🔵  Modelbin do Neon",
            var=self.modelbin_path,
            filetypes=[("Modelbin files", "*.modelbin"), ("All files", "*.*")],
            check_var=self.use_modelbin,
            hint="undercarriage_a.modelbin personalizado",
            row=3)

        # Lights.bin
        self.make_file_row(content,
            label="💡  Lights.bin",
            var=self.lights_path,
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")],
            check_var=self.use_lights,
            hint="Lights.bin com entradas do neon",
            row=4)

        # LightPresets.bin
        self.make_file_row(content,
            label="🎨  LightPresets.bin",
            var=self.lightpresets_path,
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")],
            check_var=self.use_lightpresets,
            hint="LightPresets.bin com preset do neon",
            row=5)

        tk.Frame(content, bg="#2a2a4a", height=1).grid(
            row=6, column=0, columnspan=3, sticky="ew", pady=12)

        # ── Log ─────────────────────────────────────────────────
        log_frame = tk.Frame(content, bg="#1a1a2e")
        log_frame.grid(row=7, column=0, columnspan=3, sticky="ew")

        tk.Label(log_frame, text="LOG",
                 font=("Segoe UI", 8, "bold"),
                 fg="#555", bg="#1a1a2e").pack(anchor="w")

        self.log_text = tk.Text(log_frame, height=8, width=84,
                                bg="#0d0d1a", fg="#00ff88",
                                font=("Consolas", 9),
                                relief="flat", bd=0,
                                state="disabled",
                                insertbackground="#00ff88")
        self.log_text.pack(fill="x", pady=(4, 0))

        # Scrollbar
        sb = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)

        # ── Botões ──────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg="#16213e", pady=14)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="🔄  RESTAURAR BACKUP",
                  font=("Segoe UI", 10),
                  bg="#2a2a4a", fg="#aaa",
                  activebackground="#3a3a5a", activeforeground="#fff",
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  command=self.restore_backup).pack(side="left", padx=(20, 8))

        tk.Button(btn_frame, text="🗑  LIMPAR LOG",
                  font=("Segoe UI", 10),
                  bg="#2a2a4a", fg="#aaa",
                  activebackground="#3a3a5a", activeforeground="#fff",
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  command=self.clear_log).pack(side="left", padx=8)

        self.patch_btn = tk.Button(btn_frame, text="⚡  APLICAR PATCH",
                  font=("Segoe UI", 11, "bold"),
                  bg="#e94560", fg="white",
                  activebackground="#c73652", activeforeground="white",
                  relief="flat", padx=28, pady=8, cursor="hand2",
                  command=self.run_patch)
        self.patch_btn.pack(side="right", padx=20)

        content.grid_columnconfigure(1, weight=1)

        self.log("Neon Underglow Patcher iniciado.")
        self.log("Selecione o ZIP do carro e os arquivos modificados.")

    def make_file_row(self, parent, label, var, filetypes,
                      required=False, check_var=None, hint="", row=0):
        """Cria uma linha de seleção de arquivo."""

        col_offset = 0

        if check_var:
            cb = tk.Checkbutton(parent, variable=check_var,
                                bg="#1a1a2e", fg="#aaa",
                                selectcolor="#1a1a2e",
                                activebackground="#1a1a2e",
                                relief="flat", cursor="hand2",
                                command=lambda: self.toggle_row(var, check_var))
            cb.grid(row=row, column=0, sticky="w", pady=4)
            col_offset = 0

        lbl_col = 0 if required else 0
        tk.Label(parent, text=label,
                 font=("Segoe UI", 10, "bold" if required else "normal"),
                 fg="#e94560" if required else "#ccc",
                 bg="#1a1a2e", width=22, anchor="w").grid(
                 row=row, column=0, sticky="w", padx=(20 if check_var else 0, 8), pady=5)

        entry_frame = tk.Frame(parent, bg="#0d0d1a",
                               highlightthickness=1,
                               highlightbackground="#2a2a4a")
        entry_frame.grid(row=row, column=1, sticky="ew", padx=4)

        entry = tk.Entry(entry_frame, textvariable=var,
                         bg="#0d0d1a", fg="#00ff88" if required else "#88aaff",
                         font=("Consolas", 9),
                         relief="flat", bd=4,
                         insertbackground="#00ff88")
        entry.pack(fill="x")

        if hint:
            entry.insert(0, hint)
            entry.config(fg="#444")
            entry.bind("<FocusIn>", lambda e, en=entry, v=var, h=hint:
                       self.clear_hint(en, v, h))

        tk.Button(parent, text="...",
                  font=("Segoe UI", 9),
                  bg="#2a2a4a", fg="#ccc",
                  activebackground="#3a3a5a", activeforeground="#fff",
                  relief="flat", padx=10, pady=3, cursor="hand2",
                  command=lambda v=var, f=filetypes: self.browse(v, f)).grid(
                  row=row, column=2, padx=(4, 0), pady=5)

    def clear_hint(self, entry, var, hint):
        if entry.get() == hint:
            entry.delete(0, "end")
            entry.config(fg="#88aaff")

    def toggle_row(self, var, check_var):
        pass

    def browse(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)

    def log(self, msg, color=None):
        self.log_text.configure(state="normal")
        tag = None
        if "[OK]" in msg:
            self.log_text.insert("end", msg + "\n", "ok")
            self.log_text.tag_config("ok", foreground="#00ff88")
        elif "[ERRO]" in msg:
            self.log_text.insert("end", msg + "\n", "erro")
            self.log_text.tag_config("erro", foreground="#e94560")
        elif "[AVISO]" in msg:
            self.log_text.insert("end", msg + "\n", "aviso")
            self.log_text.tag_config("aviso", foreground="#ffaa00")
        else:
            self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def patch_file_inplace(self, zip_data, entries, target_name, novo_bytes, label):
        target_key = None
        for filename in entries.keys():
            fn_lower = filename.replace("\\", "/").lower()
            tn_lower = target_name.lower()
            if fn_lower == tn_lower or fn_lower.endswith("/" + tn_lower):
                target_key = filename
                break

        if not target_key:
            self.log(f"  [ERRO] {label}: '{target_name}' nao encontrado no ZIP!")
            return False, zip_data

        info, _ = entries[target_key]
        offset = info.header_offset
        orig_compress_size = info.compress_size

        novo_comprimido = None
        force_oversize = False

        for level in range(1, 10):
            compressed = zlib.compress(novo_bytes, level=level)[2:-4]
            if len(compressed) <= orig_compress_size:
                diff = orig_compress_size - len(compressed)
                novo_comprimido = compressed + bytes(diff)
                self.log(f"  [OK] {label}: compressão level {level}, padding {diff} bytes")
                break

        if novo_comprimido is None:
            candidates = [zlib.compress(novo_bytes, level=l)[2:-4] for l in range(1, 10)]
            best_compressed = min(candidates, key=len)
            best_size = len(best_compressed)
            excesso = best_size - orig_compress_size
            self.log(f"  [AVISO] {label}: arquivo novo ({best_size:,}b) > original ({orig_compress_size:,}b) em +{excesso:,} bytes!")
            self.log(f"  [AVISO] ⚠️  RISCO DE CRASH! O jogo pode rejeitar ou travar com arquivo maior.")
            self.log(f"  [AVISO] Prosseguindo com substituição forçada por solicitação do usuário...")

            # Confirmação via messagebox na thread principal
            import threading as _th
            confirmed = [None]
            _ev = _th.Event()
            def ask():
                _msg = (
                    f"O arquivo '{label}' é maior que o original!\n\n"
                    f"  Original comprimido: {orig_compress_size:,} bytes\n"
                    f"  Novo comprimido:     {best_size:,} bytes\n"
                    f"  Excesso:             +{excesso:,} bytes\n\n"
                    "⚠️ RISCO DE CRASH: O jogo pode travar ou rejeitar o arquivo.\n\n"
                    "Deseja forçar a substituição mesmo assim?"
                )
                confirmed[0] = messagebox.askyesno("⚠️ Arquivo maior — Risco de Crash", _msg)
                _ev.set()
            self.root.after(0, ask)
            _ev.wait(timeout=60)

            if not confirmed[0]:
                self.log(f"  [CANCELADO] {label}: substituição cancelada pelo usuário.")
                return False, zip_data

            novo_comprimido = best_compressed
            force_oversize = True

        sig = b'PK\x03\x04'
        pos = offset
        if zip_data[pos:pos+4] != sig:
            self.log(f"  [ERRO] {label}: assinatura ZIP inválida!")
            return False, zip_data

        fname_len = struct.unpack('<H', zip_data[pos+26:pos+28])[0]
        extra_len = struct.unpack('<H', zip_data[pos+28:pos+30])[0]
        data_start = pos + 30 + fname_len + extra_len

        new_crc = zlib.crc32(novo_bytes) & 0xFFFFFFFF

        if force_oversize:
            # Substituição forçada: expande o ZIP inserindo bytes extras
            novo_comprimido_final = novo_comprimido
            novo_compress_size = len(novo_comprimido_final)
            zip_data = (
                zip_data[:data_start] +
                bytearray(novo_comprimido_final) +
                zip_data[data_start + orig_compress_size:]
            )
            # Atualizar tamanho comprimido no local header
            struct.pack_into('<I', zip_data, pos+18, novo_compress_size)
            struct.pack_into('<I', zip_data, pos+14, new_crc)
            struct.pack_into('<I', zip_data, pos+22, len(novo_bytes))

            # Atualizar central directory — precisa reescrever offsets de entradas posteriores
            size_diff = novo_compress_size - orig_compress_size
            cd_sig = b'PK\x01\x02'
            search_start = 0
            while True:
                cd_pos = zip_data.find(cd_sig, search_start)
                if cd_pos == -1:
                    break
                fl = struct.unpack('<H', zip_data[cd_pos+28:cd_pos+30])[0]
                fname = zip_data[cd_pos+46:cd_pos+46+fl].decode('utf-8', errors='replace')
                entry_offset = struct.unpack('<I', zip_data[cd_pos+42:cd_pos+46])[0]
                if fname == target_key:
                    struct.pack_into('<I', zip_data, cd_pos+16, new_crc)
                    struct.pack_into('<I', zip_data, cd_pos+20, novo_compress_size)
                    struct.pack_into('<I', zip_data, cd_pos+24, len(novo_bytes))
                elif entry_offset > offset:
                    # Corrigir offset de entradas que vieram depois no ZIP
                    struct.pack_into('<I', zip_data, cd_pos+42, entry_offset + size_diff)
                search_start = cd_pos + 1

            # Atualizar offset do End of Central Directory
            eocd_sig = b'PK\x05\x06'
            eocd_pos = zip_data.rfind(eocd_sig)
            if eocd_pos != -1:
                cd_offset = struct.unpack('<I', zip_data[eocd_pos+16:eocd_pos+20])[0]
                if cd_offset > offset:
                    struct.pack_into('<I', zip_data, eocd_pos+16, cd_offset + size_diff)

            self.log(f"  [AVISO] ⚠️  Substituição forçada concluída com +{size_diff:,} bytes extras no ZIP.")
        else:
            zip_data[data_start:data_start+orig_compress_size] = novo_comprimido
            struct.pack_into('<I', zip_data, pos+14, new_crc)
            struct.pack_into('<I', zip_data, pos+22, len(novo_bytes))

            cd_sig = b'PK\x01\x02'
            search_start = 0
            while True:
                cd_pos = zip_data.find(cd_sig, search_start)
                if cd_pos == -1:
                    break
                fl = struct.unpack('<H', zip_data[cd_pos+28:cd_pos+30])[0]
                fname = zip_data[cd_pos+46:cd_pos+46+fl].decode('utf-8', errors='replace')
                if fname == target_key:
                    struct.pack_into('<I', zip_data, cd_pos+16, new_crc)
                    struct.pack_into('<I', zip_data, cd_pos+24, len(novo_bytes))
                    break
                search_start = cd_pos + 1

        return True, zip_data

    def run_patch(self):
        threading.Thread(target=self._do_patch, daemon=True).start()

    def _do_patch(self):
        self.patch_btn.configure(state="disabled", text="⏳  Aplicando...")
        self.clear_log()

        try:
            zip_path = self.zip_path.get().strip()
            if not zip_path or not os.path.exists(zip_path):
                self.log("[ERRO] ZIP do carro não encontrado!")
                return

            # Verificar o que será patchado
            patches = []
            if self.use_modelbin.get() and self.modelbin_path.get().strip():
                p = self.modelbin_path.get().strip()
                if os.path.exists(p):
                    patches.append(("glassLTL_a.modelbin", p, "Modelbin Neon"))
                else:
                    self.log(f"[AVISO] Modelbin não encontrado: {p}")

            if self.use_lights.get() and self.lights_path.get().strip():
                p = self.lights_path.get().strip()
                if os.path.exists(p):
                    patches.append(("Lights.bin", p, "Lights.bin"))
                else:
                    self.log(f"[AVISO] Lights.bin não encontrado: {p}")

            if self.use_lightpresets.get() and self.lightpresets_path.get().strip():
                p = self.lightpresets_path.get().strip()
                if os.path.exists(p):
                    patches.append(("LightPresets.bin", p, "LightPresets.bin"))
                else:
                    self.log(f"[AVISO] LightPresets.bin não encontrado: {p}")

            if not patches:
                self.log("[ERRO] Nenhum arquivo selecionado para patch!")
                return

            self.log(f"ZIP: {os.path.basename(zip_path)}")
            self.log(f"Patches a aplicar: {len(patches)}")

            # Backup
            backup = zip_path + ".backup"
            shutil.copy2(zip_path, backup)
            self.log(f"[OK] Backup criado: {os.path.basename(backup)}")

            # Ler ZIP
            entries = {}
            with zipfile.ZipFile(zip_path, 'r') as zin:
                for item in zin.infolist():
                    entries[item.filename] = (item, zin.read(item.filename))
            self.log(f"[OK] ZIP lido: {len(entries)} arquivos")

            with open(zip_path, 'rb') as f:
                zip_data = bytearray(f.read())

            # Aplicar patches
            results = {}
            self.log("\nAplicando patches...")
            for target_name, src_path, label in patches:
                with open(src_path, 'rb') as f:
                    novo_bytes = f.read()
                self.log(f"\n→ {label} ({len(novo_bytes):,} bytes)")
                success, zip_data = self.patch_file_inplace(
                    zip_data, entries, target_name, novo_bytes, label)
                results[label] = success

            # Salvar
            any_success = any(results.values())
            if any_success:
                with open(zip_path, 'wb') as f:
                    f.write(zip_data)
                self.log(f"\n[OK] ZIP salvo com sucesso!")
            else:
                self.log(f"\n[ERRO] Nenhum patch foi aplicado! ZIP não modificado.")

            # Resumo
            self.log("\n" + "─" * 45)
            self.log("RESUMO:")
            for label, success in results.items():
                status = "✅ OK" if success else "❌ FALHOU"
                self.log(f"  {label:<25} {status}")

            if any_success:
                self.log("\n✅ Patch concluído! Pode testar o jogo.")
                messagebox.showinfo("Sucesso!", 
                    "Patch aplicado com sucesso!\n\nPode testar o jogo agora.")
            else:
                messagebox.showerror("Erro", 
                    "Nenhum patch foi aplicado.\nVerifique o log para detalhes.")

        except Exception as e:
            self.log(f"[ERRO] Exceção: {str(e)}")
            messagebox.showerror("Erro inesperado", str(e))
        finally:
            self.patch_btn.configure(state="normal", text="⚡  APLICAR PATCH")

    def restore_backup(self):
        zip_path = self.zip_path.get().strip()
        if not zip_path:
            messagebox.showwarning("Aviso", "Selecione o ZIP do carro primeiro!")
            return
        backup = zip_path + ".backup"
        if not os.path.exists(backup):
            messagebox.showwarning("Aviso", "Backup não encontrado!")
            return
        shutil.copy2(backup, zip_path)
        self.log("[OK] Backup restaurado com sucesso!")
        messagebox.showinfo("Restaurado!", "Backup restaurado com sucesso!")


if __name__ == "__main__":
    root = tk.Tk()
    app = NeonPatcher(root)
    root.mainloop()
