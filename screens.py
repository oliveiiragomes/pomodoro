import tkinter as tk
from tkinter import messagebox, ttk


class ConstrucaoTelas:
    """Cria as telas, controles e diálogos e sincroniza sua apresentação."""

    def _montar_interface(self):
        # A tela principal e a compacta compartilham o mesmo estado do aplicativo.
        janela = self.janela
        cores = self.CORES

        self.interface_completa = tk.Frame(janela, bg=cores["background"])
        self.interface_completa.pack(fill="both", expand=True)

        cabecalho = tk.Frame(self.interface_completa, bg=cores["background"])
        cabecalho.pack(fill="x", padx=54, pady=(34, 0))

        tk.Label(
            cabecalho,
            text="POMODORO",
            bg=cores["background"],
            fg=cores["text"],
            font=self._fonte(18, "bold"),
        ).pack(side="left")
        tk.Label(
            cabecalho,
            text="Mantenha sua mente onde o seu corpo está",
            bg=cores["background"],
            fg=cores["muted"],
            font=self._fonte(10),
        ).pack(side="right", pady=5)

        conteudo = tk.Frame(self.interface_completa, bg=cores["background"])
        conteudo.pack(fill="both", expand=True, padx=54, pady=30)

        self.rotulo_modo = tk.Label(
            conteudo,
            text="FOCO",
            bg=cores["background"],
            fg=cores["accent"],
            font=self._fonte(11, "bold"),
        )
        self.rotulo_modo.pack(pady=(8, 14))

        self.rotulo_cronometro = tk.Label(
            conteudo,
            text="25:00",
            bg=cores["background"],
            fg=cores["text"],
            font=self._fonte(92, "bold"),
        )
        self.rotulo_cronometro.pack()

        self.rotulo_status = tk.Label(
            conteudo,
            text="Pronto para comecar?",
            bg=cores["background"],
            fg=cores["muted"],
            font=self._fonte(11),
        )
        self.rotulo_status.pack(pady=(0, 26))

        self.barra_progresso = tk.Canvas(
            conteudo,
            height=8,
            bg=cores["surface_alt"],
            highlightthickness=0,
            bd=0,
        )
        self.barra_progresso.pack(fill="x", pady=(0, 34))

        controles = tk.Frame(conteudo, bg=cores["background"])
        controles.pack()

        self.botao_iniciar = tk.Button(
            controles,
            text="INICIAR",
            command=self.alternar_timer,
            bg=cores["accent"],
            activebackground=cores["accent_dark"],
            activeforeground="white",
            fg="white",
            font=self._fonte(11, "bold"),
            relief="flat",
            bd=0,
            padx=34,
            pady=13,
            cursor="hand2",
        )
        self.botao_iniciar.pack(side="left", padx=6)

        self._botao_secundario(controles, "REINICIAR", self.reiniciar_timer).pack(side="left", padx=6)
        self._botao_secundario(controles, "PULAR", self.pular_modo).pack(side="left", padx=6)

        rodape = tk.Frame(self.interface_completa, bg=cores["surface"])
        rodape.pack(fill="x", side="bottom")

        conteudo_rodape = tk.Frame(rodape, bg=cores["surface"])
        conteudo_rodape.pack(fill="x", padx=54, pady=20)

        self.rotulo_ciclos = tk.Label(
            conteudo_rodape,
            text="0 ciclos concluidos",
            bg=cores["surface"],
            fg=cores["text"],
            font=self._fonte(10, "bold"),
        )
        self.rotulo_ciclos.pack(side="left")

        acoes_rodape = tk.Frame(conteudo_rodape, bg=cores["surface"])
        acoes_rodape.pack(side="right")
        self.acoes_rodape = acoes_rodape

        tk.Button(
            acoes_rodape,
            text="MODO MINI",
            command=self.entrar_modo_compacto,
            bg=cores["surface"],
            fg=cores["muted"],
            activebackground=cores["surface"],
            activeforeground=cores["text"],
            font=self._fonte(9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left", padx=(0, 18))

        tk.Button(
            acoes_rodape,
            text="CONFIGURAR",
            command=self.abrir_configuracoes,
            bg=cores["surface"],
            fg=cores["muted"],
            activebackground=cores["surface"],
            activeforeground=cores["text"],
            font=self._fonte(9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left", padx=(0, 18))

        tk.Button(
            acoes_rodape,
            text="COMO FUNCIONA",
            command=self.mostrar_ajuda,
            bg=cores["surface"],
            fg=cores["muted"],
            activebackground=cores["surface"],
            activeforeground=cores["text"],
            font=self._fonte(9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="right")

        self._montar_interface_mini()

    def _montar_interface_mini(self):
        self.interface_compacta = tk.Frame(self.janela, bg=self.CORES["background"])
        self.interface_compacta.bind("<Enter>", self._mostrar_botao_restaurar)
        self.interface_compacta.bind("<Leave>", self._agendar_ocultacao_botao_restaurar)

        self.rotulo_modo_compacto = tk.Label(
            self.interface_compacta,
            text="FOCO",
            bg=self.CORES["background"],
            fg=self.CORES["accent"],
            font=self._fonte(10, "bold"),
        )

        self.rotulo_cronometro_compacto = tk.Label(
            self.interface_compacta,
            text="25:00",
            bg=self.CORES["background"],
            fg=self.CORES["text"],
            font=self._fonte(28, "bold"),
        )
        self.rotulo_cronometro_compacto.pack()

        self.botao_restaurar = tk.Button(
            self.interface_compacta,
            text="VOLTAR",
            command=self.sair_modo_compacto,
            bg=self.CORES["surface"],
            fg=self.CORES["text"],
            activebackground=self.CORES["surface_alt"],
            activeforeground=self.CORES["text"],
            font=self._fonte(8, "bold"),
            relief="solid",
            bd=1,
            highlightthickness=0,
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.botao_restaurar.bind("<Enter>", self._cancelar_ocultacao_botao_restaurar)
        self.botao_restaurar.bind("<Leave>", self._agendar_ocultacao_botao_restaurar)

    def _botao_secundario(self, componente_pai, texto, comando):
        return tk.Button(
            componente_pai,
            text=texto,
            command=comando,
            bg=self.CORES["surface"],
            fg=self.CORES["text"],
            activebackground=self.CORES["surface_alt"],
            activeforeground=self.CORES["text"],
            font=self._fonte(10, "bold"),
            relief="solid",
            bd=1,
            highlightthickness=0,
            padx=22,
            pady=12,
            cursor="hand2",
        )

    def abrir_configuracoes(self):
        janela_configuracoes = tk.Toplevel(self.janela)
        janela_configuracoes.title("Configurar tempos")
        janela_configuracoes.geometry("440x760")
        janela_configuracoes.resizable(False, False)
        janela_configuracoes.configure(bg=self.CORES["surface"])
        janela_configuracoes.transient(self.janela)
        janela_configuracoes.grab_set()

        campo_fundo = self.CORES["surface"]
        campo_texto = self.CORES["text"]
        if self.tema in {"Neon escuro", "Retro", "Verde Floresta"}:
            # Campos claros mantêm o texto legível nos temas escuros e retro.
            campo_fundo = "#F4F4F4"
            campo_texto = "#111111"
        cor_fundo_acao = self.CORES["surface_alt"]
        cor_texto_acao = self.CORES["text"]
        cor_ativa_acao = self.CORES["border"]
        if self.tema in {"Neon escuro", "Retro", "Verde Floresta"}:
            cor_fundo_acao = campo_fundo
            cor_texto_acao = campo_texto
            cor_ativa_acao = "#DEDEDE"

        estilo = ttk.Style(janela_configuracoes)
        estilo.configure(
            "Pomodoro.TCombobox",
            fieldbackground=campo_fundo,
            background=campo_fundo,
            foreground=campo_texto,
            font=self._fonte(10),
            padding=6,
        )
        estilo.map(
            "Pomodoro.TCombobox",
            fieldbackground=[("readonly", campo_fundo)],
            foreground=[("readonly", campo_texto)],
        )
        estilo.configure(
            "Pomodoro.TSpinbox",
            fieldbackground=campo_fundo,
            background=campo_fundo,
            foreground=campo_texto,
            font=self._fonte(10),
            padding=5,
        )
        estilo.configure(
            "Pomodoro.TCheckbutton",
            background=self.CORES["surface"],
            foreground=self.CORES["text"],
            font=self._fonte(10),
            padding=(2, 5),
        )
        estilo.map(
            "Pomodoro.TCheckbutton",
            background=[("active", self.CORES["surface"])],
            foreground=[("disabled", self.CORES["muted"])],
        )
        tk.Label(
            janela_configuracoes,
            text="DURACAO DOS CICLOS",
            bg=self.CORES["surface"],
            fg=self.CORES["text"],
            font=self._fonte(13, "bold"),
        ).pack(anchor="w", padx=30, pady=(26, 4))
        tk.Label(
            janela_configuracoes,
            text="Defina os tempos em minutos.",
            bg=self.CORES["surface"],
            fg=self.CORES["muted"],
            font=self._fonte(10),
        ).pack(anchor="w", padx=30, pady=(0, 18))

        campos = tk.Frame(janela_configuracoes, bg=self.CORES["surface"])
        campos.pack(fill="x", padx=30)
        valores_campos = {}
        rotulos_modos = {
            "focus": "Foco",
            "short_break": "Pausa curta",
            "long_break": "Pausa longa",
        }
        tk.Label(
            janela_configuracoes,
            text="Som do alarme",
            bg=self.CORES["surface"],
            fg=self.CORES["text"],
            font=self._fonte(11, "bold"),
        ).pack(anchor="w", padx=30, pady=(20, 6))
        selecao_som = tk.StringVar(value=self.som_alarme)
        controles_som = tk.Frame(janela_configuracoes, bg=self.CORES["surface"])
        controles_som.pack(fill="x", padx=30)
        seletor_som = ttk.Combobox(
            controles_som,
            textvariable=selecao_som,
            values=tuple(self.arquivos_audio) or ("Nenhum MP3 encontrado",),
            state="readonly" if self.arquivos_audio else "disabled",
            style="Pomodoro.TCombobox",
        )
        seletor_som.pack(side="left", fill="x", expand=True)
        tk.Button(
            controles_som,
            text="OUVIR SOM",
            command=lambda: self._tocar_som_alarme(
                selecao_som.get(), volume.get() / 100
            ),
            state="normal" if self.arquivos_audio else "disabled",
            bg=cor_fundo_acao,
            fg=cor_texto_acao,
            activebackground=cor_ativa_acao,
            activeforeground=cor_texto_acao,
            font=self._fonte(9, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=12,
            pady=7,
            cursor="hand2",
        ).pack(side="right", padx=(8, 0))

        for modo, rotulo in rotulos_modos.items():
            linha = tk.Frame(campos, bg=self.CORES["surface"])
            linha.pack(fill="x", pady=4)
            tk.Label(
                linha,
                text=rotulo,
                bg=self.CORES["surface"],
                fg=self.CORES["text"],
                font=self._fonte(10),
                width=16,
                anchor="w",
            ).pack(side="left")
            valor = tk.StringVar(value=str(self.duracoes[modo]))
            valores_campos[modo] = valor
            ttk.Spinbox(
                linha,
                from_=1,
                to=180,
                textvariable=valor,
                width=6,
                justify="center",
                style="Pomodoro.TSpinbox",
            ).pack(side="right")

        linha_intervalo = tk.Frame(janela_configuracoes, bg=self.CORES["surface"])
        linha_intervalo.pack(fill="x", padx=30, pady=(12, 4))
        tk.Label(
            linha_intervalo,
            text="Pausa longa a cada focos",
            bg=self.CORES["surface"],
            fg=self.CORES["text"],
            font=self._fonte(10),
        ).pack(side="left")
        intervalo = tk.StringVar(value=str(self.intervalo_pausa_longa))
        ttk.Spinbox(
            linha_intervalo,
            from_=2,
            to=12,
            textvariable=intervalo,
            width=6,
            justify="center",
            style="Pomodoro.TSpinbox",
        ).pack(side="right")

        auto_pausas = tk.BooleanVar(value=self.iniciar_pausas_automaticamente)
        ttk.Checkbutton(
            janela_configuracoes,
            text="Iniciar pausas automaticamente",
            variable=auto_pausas,
            style="Pomodoro.TCheckbutton",
        ).pack(anchor="w", padx=26, pady=2)
        auto_focos = tk.BooleanVar(value=self.iniciar_focos_automaticamente)
        ttk.Checkbutton(
            janela_configuracoes,
            text="Iniciar Pomodoros automaticamente",
            variable=auto_focos,
            style="Pomodoro.TCheckbutton",
        ).pack(anchor="w", padx=26, pady=2)

        tk.Label(
            janela_configuracoes,
            text="Tema de cores",
            bg=self.CORES["surface"],
            fg=self.CORES["text"],
            font=self._fonte(11, "bold"),
        ).pack(anchor="w", padx=30, pady=(12, 5))
        selecao_tema = tk.StringVar(value=self.tema)
        ttk.Combobox(
            janela_configuracoes,
            textvariable=selecao_tema,
            values=tuple(self.TEMAS),
            state="readonly",
            style="Pomodoro.TCombobox",
        ).pack(fill="x", padx=30)

        tk.Label(
            janela_configuracoes,
            text="Volume do som",
            bg=self.CORES["surface"],
            fg=self.CORES["text"],
            font=self._fonte(11, "bold"),
        ).pack(anchor="w", padx=30, pady=(12, 2))
        volume = tk.IntVar(value=self.volume_som)
        rotulo_volume = tk.Label(
            janela_configuracoes,
            text=f"{volume.get()}%",
            width=5,
            anchor="e",
            bg=self.CORES["surface"],
            fg=self.CORES["muted"],
            font=self._fonte(10, "bold"),
        )

        def atualizar_volume(valor):
            percentual = int(round(float(valor)))
            rotulo_volume.config(text=f"{percentual}%")
            self._ajustar_volume_alarme(percentual)

        linha_volume = tk.Frame(janela_configuracoes, bg=self.CORES["surface"])
        linha_volume.pack(fill="x", padx=26)
        tk.Scale(
            linha_volume,
            variable=volume,
            command=atualizar_volume,
            from_=0,
            to=100,
            resolution=5,
            orient="horizontal",
            showvalue=False,
            bg=self.CORES["surface"],
            fg=self.CORES["muted"],
            troughcolor=self.CORES["surface_alt"],
            relief="flat",
            bd=1,
            sliderrelief="raised",
            sliderlength=24,
            width=15,
            highlightthickness=0,
            activebackground=self.CORES["accent"],
        ).pack(side="left", fill="x", expand=True)
        rotulo_volume.pack(in_=linha_volume, side="right", padx=(10, 0))

        def salvar_configuracoes():
            # Valida todos os valores antes de alterar o estado atual do aplicativo.
            self._parar_som_alarme()
            try:
                novas_duracoes = {
                    modo: int(valor.get()) for modo, valor in valores_campos.items()
                }
                if any(minutos < 1 or minutos > 180 for minutos in novas_duracoes.values()):
                    raise ValueError
                novo_intervalo = int(intervalo.get())
                if not 2 <= novo_intervalo <= 12:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Valor invalido",
                    "Use duracoes de 1 a 180 minutos e intervalo de 2 a 12 focos.",
                    parent=janela_configuracoes,
                )
                return

            self.duracoes.update(novas_duracoes)
            self.intervalo_pausa_longa = novo_intervalo
            self.iniciar_pausas_automaticamente = auto_pausas.get()
            self.iniciar_focos_automaticamente = auto_focos.get()
            self.volume_som = volume.get()
            self.tema = selecao_tema.get()
            if self.arquivos_audio:
                self.som_alarme = selecao_som.get()
            self.em_execucao = False
            self._cancelar_contagem()
            self.segundos_restantes = self.duracoes[self.modo] * 60
            janela_configuracoes.destroy()
            self._aplicar_tema()

        tk.Button(
            janela_configuracoes,
            text="SALVAR",
            command=salvar_configuracoes,
            bg=self.CORES["accent"],
            fg=self.CORES["accent_text"],
            activebackground=self.CORES["accent_dark"],
            activeforeground=self.CORES["accent_text"],
            font=self._fonte(10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=18,
            pady=9,
            cursor="hand2",
        ).pack(pady=(24, 20))

    def _atualizar_interface(self):
        info_modo = self.MODOS[self.modo]
        cor_modo = self._cor_modo(self.modo)
        minutos, segundos = divmod(self.segundos_restantes, 60)
        self.rotulo_cronometro.config(text=f"{minutos:02d}:{segundos:02d}", fg=cor_modo)
        self.rotulo_cronometro_compacto.config(text=f"{minutos:02d}:{segundos:02d}", fg=cor_modo)
        self.rotulo_modo.config(text=info_modo["label"], fg=cor_modo)
        self.rotulo_modo_compacto.config(text=info_modo["label"], fg=cor_modo)
        self.botao_iniciar.config(
            text="PAUSAR" if self.em_execucao else "INICIAR",
            bg=cor_modo,
            fg=self.CORES["accent_text"],
        )
        self.rotulo_status.config(
            text="Em andamento" if self.em_execucao else "Pronto para comecar?"
        )
        self.rotulo_ciclos.config(
            text=f"{self.ciclos_foco_concluidos} ciclo{'s' if self.ciclos_foco_concluidos != 1 else ''} concluido{'s' if self.ciclos_foco_concluidos != 1 else ''}"
        )

        # A barra representa a fração já transcorrida no modo atual.
        duracao_total = self.duracoes[self.modo] * 60
        largura_barra = self.barra_progresso.winfo_width()
        if largura_barra <= 1:
            largura_barra = 560
        proporcao_decorrida = 1 - (self.segundos_restantes / duracao_total)
        largura_preenchida = max(0, largura_barra * proporcao_decorrida)
        self.barra_progresso.delete("all")
        self.barra_progresso.create_rectangle(
            0, 0, largura_preenchida, 8, fill=cor_modo, outline=""
        )
