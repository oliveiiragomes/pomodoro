# Eu importo o Tkinter para criar a janela, os componentes visuais e o temporizador.
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter import font as tkfont
# Eu importo caixas de mensagem para avisar o usuario quando um ciclo termina.
from tkinter import messagebox
import pygame


# Eu concentro nesta classe toda a interface e toda a logica do Pomodoro.
class PomodoroApp:
    # Eu centralizo as paletas para que o tema possa ser trocado em tempo de execucao.
    TEMAS = {
        "Claro": {
            "background": "#F4F7FB", "surface": "#FFFFFF",
            "surface_alt": "#EAF0F7", "text": "#172033",
            "muted": "#718096", "accent": "#F06C5B",
            "accent_dark": "#D95647", "accent_text": "#FFFFFF",
            "border": "#DCE4EE", "focus": "#E85D4A", "break": "#4AAE8B",
        },
        "Neon escuro": {
            "background": "#10131F", "surface": "#1B2031",
            "surface_alt": "#292F45", "text": "#F5F7FF",
            "muted": "#A5ADC4", "accent": "#39F0C8",
            "accent_dark": "#17B89A", "accent_text": "#10131F",
            "border": "#39415A", "focus": "#58FFD6", "break": "#F44FD8",
        },
        "Retro": {
            "background": "#1B1B1B", "surface": "#292929",
            "surface_alt": "#383838", "text": "#F2F2F2",
            "muted": "#B8B8B8", "accent": "#E6E6E6",
            "accent_dark": "#BFBFBF", "accent_text": "#111111",
            "border": "#505050", "focus": "#D6D6D6", "break": "#A0A0A0",
        },
        "Verde Floresta": {
            "background": "#172A24", "surface": "#294438",
            "surface_alt": "#3F5B45", "text": "#FFF0C2",
            "muted": "#D5B875", "accent": "#F2B705",
            "accent_dark": "#D9820D", "accent_text": "#272016",
            "border": "#68814F", "focus": "#E65162", "break": "#55C29A",
        },
    }
    # Eu defino o rotulo e a duracao padrao de cada tipo de ciclo.
    MODOS = {
        "focus": {"label": "FOCO", "minutes": 25},
        "short_break": {"label": "PAUSA CURTA", "minutes": 5},
        "long_break": {"label": "PAUSA LONGA", "minutes": 15},
    }

    def __init__(self, janela: tk.Tk):
        # Eu guardo a janela principal e configuro seu titulo, tamanho e fundo.
        self.janela = janela
        self.janela.title("Pomodoro")
        self.janela.geometry("720x620")
        self.janela.minsize(620, 560)
        self.tema = "Claro"
        self.CORES = dict(self.TEMAS[self.tema])
        self.janela.configure(bg=self.CORES["background"])

        # Eu inicio o aplicativo no modo foco, parado e com 25 minutos restantes.
        self.modo = "focus"
        self.em_execucao = False
        # Eu copio as duracoes padrao para permitir que o usuario as altere em tempo de execucao.
        self.duracoes = {
            modo: info["minutes"] for modo, info in self.MODOS.items()
        }
        self.segundos_restantes = self.duracoes[self.modo] * 60
        self.ciclos_foco_concluidos = 0
        self.intervalo_pausa_longa = 4
        self.iniciar_pausas_automaticamente = False
        self.iniciar_focos_automaticamente = False
        self.volume_som = 70
        self.id_agendamento_contagem = None
        pasta_audios = Path(__file__).resolve().parent / "audios"
        self.arquivos_audio = {
            arquivo.name: arquivo for arquivo in sorted(pasta_audios.glob("*.mp3"))
        }
        self.som_alarme = next(iter(self.arquivos_audio), "")
        # Eu guardo o estado da visualizacao compacta e o agendamento do botao de retorno.
        self.modo_compacto = False
        self.id_agendamento_botao_restaurar = None

        # Eu monto os componentes visuais e sincronizo a tela com o estado inicial.
        self._montar_interface()
        self._atualizar_interface()

    def _fonte(self, tamanho: int, peso: str = "normal"):
        # Eu padronizo a familia, o tamanho e o peso das fontes da interface.
        return (self._familia_fonte(), tamanho, peso)

    def _familia_fonte(self):
        return {
            "Retro": "Courier New",
            "Verde Floresta": "Segoe Print",
        }.get(self.tema, "Segoe UI")

    def _cor_modo(self, modo):
        return self.CORES["focus"] if modo == "focus" else self.CORES["break"]

    def _aplicar_tema(self):
        cores_anteriores = self.CORES
        self.CORES = dict(self.TEMAS[self.tema])
        substituicoes = {
            cores_anteriores[chave]: self.CORES[chave]
            for chave in cores_anteriores
            if chave != "accent_text"
        }
        substituicoes["white"] = self.CORES["accent_text"]
        opcoes_cor = (
            "background", "bg", "foreground", "fg", "activebackground",
            "activeforeground", "highlightbackground", "insertbackground",
            "troughcolor", "selectbackground", "selectforeground",
        )

        def atualizar_widget(widget):
            for opcao in opcoes_cor:
                try:
                    cor_atual = widget.cget(opcao)
                    cor_nova = substituicoes.get(cor_atual)
                    if cor_nova:
                        widget.configure(**{opcao: cor_nova})
                except tk.TclError:
                    continue
            try:
                fonte_atual = tkfont.Font(root=widget, font=widget.cget("font")).actual()
                if fonte_atual["family"] in {"Segoe UI", "Courier New", "Segoe Print"}:
                    widget.configure(
                        font=(self._familia_fonte(), fonte_atual["size"], fonte_atual["weight"])
                    )
            except (tk.TclError, TypeError, ValueError):
                pass
            for filho in widget.winfo_children():
                atualizar_widget(filho)

        atualizar_widget(self.janela)
        estilo = ttk.Style(self.janela)
        estilo.configure(
            "TCombobox",
            fieldbackground=self.CORES["surface"],
            background=self.CORES["surface"],
            foreground=self.CORES["text"],
        )
        estilo.map(
            "TCombobox",
            fieldbackground=[("readonly", self.CORES["surface"])],
            foreground=[("readonly", self.CORES["text"])],
        )
        cor_fundo_botao = (
            self.CORES["surface_alt"] if self.tema == "Verde Floresta"
            else self.CORES["surface"]
        )
        cor_texto_botao = (
            self.CORES["text"] if self.tema == "Verde Floresta"
            else self.CORES["muted"]
        )
        cor_ativa_botao = (
            self.CORES["accent"] if self.tema == "Verde Floresta"
            else self.CORES["surface"]
        )
        for botao in self.acoes_rodape.winfo_children():
            botao.configure(
                bg=cor_fundo_botao,
                fg=cor_texto_botao,
                activebackground=cor_ativa_botao,
                activeforeground=self.CORES["accent_text"] if self.tema == "Verde Floresta" else self.CORES["text"],
                relief="solid" if self.tema == "Verde Floresta" else "flat",
                bd=1 if self.tema == "Verde Floresta" else 0,
                font=self._fonte(8 if self.tema == "Verde Floresta" else 9, "bold"),
            )
        self._atualizar_interface()
        self._ajustar_tamanho_janela()

    def _ajustar_tamanho_janela(self):
        if self.modo_compacto:
            return
        self.janela.update_idletasks()
        largura_minima = max(620, self.interface_completa.winfo_reqwidth())
        altura_minima = max(560, self.interface_completa.winfo_reqheight())
        largura_atual = self.janela.winfo_width()
        altura_atual = self.janela.winfo_height()
        self.janela.minsize(largura_minima, altura_minima)
        if largura_atual < largura_minima or altura_atual < altura_minima:
            self.janela.geometry(
                f"{max(largura_atual, largura_minima)}x{max(altura_atual, altura_minima)}"
            )

    def _montar_interface(self):
        # Eu crio o cabecalho, o timer, os controles, a barra de progresso e o rodape.
        janela = self.janela
        cores = self.CORES

        # Eu agrupo a interface completa para poder esconde-la quando o modo compacto for ativado.
        self.interface_completa = tk.Frame(janela, bg=cores["background"])
        self.interface_completa.pack(fill="both", expand=True)

        # Eu monto o cabecalho com o nome do app e uma descricao curta.
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
        
        # Eu organizo o conteudo principal no centro da janela.
        conteudo = tk.Frame(self.interface_completa, bg=cores["background"])
        conteudo.pack(fill="both", expand=True, padx=54, pady=30)

        # Eu mostro o nome do modo atual acima do contador.
        self.rotulo_modo = tk.Label(
            conteudo,
            text="FOCO",
            bg=cores["background"],
            fg=cores["accent"],
            font=self._fonte(11, "bold"),
        )
        self.rotulo_modo.pack(pady=(8, 14))

        # Eu mostro o tempo restante em destaque para facilitar a leitura.
        self.rotulo_cronometro = tk.Label(
            conteudo,
            text="25:00",
            bg=cores["background"],
            fg=cores["text"],
            font=self._fonte(92, "bold"),
        )
        self.rotulo_cronometro.pack()

        # Eu informo se o timer esta parado ou em andamento.
        self.rotulo_status = tk.Label(
            conteudo,
            text="Pronto para comecar?",
            bg=cores["background"],
            fg=cores["muted"],
            font=self._fonte(11),
        )
        self.rotulo_status.pack(pady=(0, 26))

        # Eu uso um Canvas para desenhar uma barra que representa o progresso.
        self.barra_progresso = tk.Canvas(
            conteudo,
            height=8,
            bg=cores["surface_alt"],
            highlightthickness=0,
            bd=0,
        )
        self.barra_progresso.pack(fill="x", pady=(0, 34))

        # Eu agrupo os botoes de controle na mesma linha.
        controles = tk.Frame(conteudo, bg=cores["background"])
        controles.pack()

        # Botao INICIAR/PAUSAR: controla o inicio e a pausa da contagem.
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

        # Botoes REINICIAR e PULAR: controlam o ciclo atual.
        self._botao_secundario(controles, "REINICIAR", self.reiniciar_timer).pack(side="left", padx=6)
        self._botao_secundario(controles, "PULAR", self.pular_modo).pack(side="left", padx=6)

        # Eu monto o rodape com a contagem de ciclos e o acesso a explicacao.
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

        # Eu coloco as acoes de ajuda e configuracao agrupadas no canto direito.
        acoes_rodape = tk.Frame(conteudo_rodape, bg=cores["surface"])
        acoes_rodape.pack(side="right")
        self.acoes_rodape = acoes_rodape

        # Botao MODO MINI: reduz a interface para exibir somente o cronometro.
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

        # Botao CONFIGURAR: abre os campos de duracao dos ciclos.
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

        # Botao COMO FUNCIONA: exibe as instrucoes do Pomodoro.
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

        # Eu preparo a visao compacta, mas mantenho-a escondida ate o usuario pedir.
        self._montar_interface_mini()

    def _montar_interface_mini(self):
        # Eu crio uma tela pequena que exibe somente o tempo restante.
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

        # Botao VOLTAR: retorna da tela mini para a interface completa.
        # Ele fica invisivel ate o mouse entrar na tela compacta.
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

    def entrar_modo_compacto(self):
        # Eu escondo a interface completa e redimensiono a janela para exibir apenas o timer.
        self.modo_compacto = True
        self.interface_completa.pack_forget()
        self.interface_compacta.pack(fill="both", expand=True)
        self.janela.geometry("110x48")
        self.janela.minsize(110, 48)
        self.janela.resizable(False, False)
        self._ocultar_botao_restaurar()
        self._atualizar_interface()

    def sair_modo_compacto(self):
        # Eu restauro a interface e redimensiono para caber o tema atual.
        self.modo_compacto = False
        self._cancelar_ocultacao_botao_restaurar()
        self._ocultar_botao_restaurar()
        self.interface_compacta.pack_forget()
        self.interface_completa.pack(fill="both", expand=True)
        self.janela.geometry("720x620")
        self.janela.minsize(620, 560)
        self.janela.resizable(True, True)
        self._atualizar_interface()
        self._ajustar_tamanho_janela()

    def _mostrar_botao_restaurar(self, _=None):
        # Eu mostro o pequeno botao de retorno quando o mouse entra na tela compacta.
        self._cancelar_ocultacao_botao_restaurar()
        self.botao_restaurar.place(relx=1.0, x=-12, y=12, anchor="ne")

    def _ocultar_botao_restaurar(self):
        # Eu escondo o botao para deixar a visualizacao compacta limpa.
        self.botao_restaurar.place_forget()
        self.id_agendamento_botao_restaurar = None

    def _agendar_ocultacao_botao_restaurar(self, _=None):
        # Eu aguardo um instante antes de esconder o botao para facilitar o clique.
        self._cancelar_ocultacao_botao_restaurar()
        self.id_agendamento_botao_restaurar = self.janela.after(150, self._ocultar_botao_restaurar)

    def _cancelar_ocultacao_botao_restaurar(self, _=None):
        # Eu cancelo o desaparecimento agendado quando o mouse ainda esta sobre o botao.
        if self.id_agendamento_botao_restaurar is not None:
            self.janela.after_cancel(self.id_agendamento_botao_restaurar)
            self.id_agendamento_botao_restaurar = None

    def _botao_secundario(self, componente_pai, texto, comando):
        # Botoes secundarios reutilizaveis: REINICIAR e PULAR.
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

    def alternar_timer(self):
        # Eu inicio a contagem ou cancelo o proximo tick ao pausar.
        if self.em_execucao:
            self.em_execucao = False
            self._cancelar_contagem()
            self._atualizar_interface()
        else:
            self._iniciar_contagem()

    def _iniciar_contagem(self):
        if self.em_execucao:
            return
        self.em_execucao = True
        self.id_agendamento_contagem = self.janela.after(1000, self._contar_segundo)
        self._atualizar_interface()

    def _contar_segundo(self):
        # Eu reduzo um segundo por tick e concluo o ciclo assim que chega a zero.
        self.id_agendamento_contagem = None
        if not self.em_execucao:
            return
        if self.segundos_restantes > 0:
            self.segundos_restantes -= 1
            self._atualizar_interface()
            if self.segundos_restantes > 0:
                self.id_agendamento_contagem = self.janela.after(
                    1000, self._contar_segundo
                )
            else:
                self._concluir_modo()
        else:
            self._concluir_modo()

    def _concluir_modo(self):
        # Eu finalizo o modo atual, conto ciclos de foco e escolho a proxima pausa.
        self.em_execucao = False
        self._cancelar_contagem()
        if self.modo == "focus":
            proximo_modo = self._concluir_ciclo_foco()
        else:
            proximo_modo = "focus"
        self.modo = proximo_modo
        self.segundos_restantes = self.duracoes[self.modo] * 60
        self._atualizar_interface()
        self._tocar_som_alarme()
        messagebox.showinfo("Pomodoro", f"Tempo concluido. Agora: {self.MODOS[self.modo]['label'].lower()}.")
        self._parar_som_alarme()
        iniciar_proximo = (
            self.iniciar_focos_automaticamente
            if self.modo == "focus"
            else self.iniciar_pausas_automaticamente
        )
        if iniciar_proximo:
            self._iniciar_contagem()
    
    def _concluir_ciclo_foco(self):
        # Eu conto o foco e escolho uma pausa longa no intervalo configurado.
        self.ciclos_foco_concluidos += 1
        return (
            "long_break"
            if self.ciclos_foco_concluidos % self.intervalo_pausa_longa == 0
            else "short_break"
        )

    def reiniciar_timer(self):
        # Eu paro a contagem e devolvo o modo atual para sua duracao original.
        self.em_execucao = False
        self._cancelar_contagem()
        self.segundos_restantes = self.duracoes[self.modo] * 60
        self._atualizar_interface()

    def pular_modo(self):
        # Eu paro o timer e alterno manualmente entre foco e a pausa adequada.
        self.em_execucao = False
        self._cancelar_contagem()
        if self.modo == "focus":
            proximo_modo = self._concluir_ciclo_foco()
        else:
            proximo_modo = "focus"
        self.modo = proximo_modo
        self.segundos_restantes = self.duracoes[self.modo] * 60
        self._atualizar_interface()
               
    def _cancelar_contagem(self):
        # Eu cancelo o evento agendado para evitar varias contagens ao mesmo tempo.
        if self.id_agendamento_contagem is not None:
            self.janela.after_cancel(self.id_agendamento_contagem)
            self.id_agendamento_contagem = None
    
    def abrir_configuracoes(self):
        # Eu abro uma janela modal para o usuario informar as duracoes dos tres modos.
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
        # Eu apresento os valores atuais para que o usuario possa ajusta-los facilmente.
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
            # Eu crio um campo numerico para cada modo e preencho seu valor atual.
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

        # Eu salvo os novos valores somente depois de validar todos os campos.
        def salvar_configuracoes():
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

            # Eu aplico os tempos, paro a contagem e reinicio o modo atual com a nova duracao.
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

        # Botao SALVAR: aplica as duracoes informadas pelo usuario.
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

    def _tocar_som_alarme(self, som=None, volume=None):
        arquivo_audio = self.arquivos_audio.get(som or self.som_alarme)
        if arquivo_audio is None:
            self.janela.bell()
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(str(arquivo_audio))
            pygame.mixer.music.set_volume(
                self.volume_som / 100 if volume is None else volume
            )
            pygame.mixer.music.play()
        except (OSError, pygame.error):
            self.janela.bell()

    def _ajustar_volume_alarme(self, volume):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(max(0.0, min(1.0, float(volume) / 100)))

    def _parar_som_alarme(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def _atualizar_interface(self):
        # Eu atualizo textos, cores, botoes e a barra para refletir o estado atual.
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

        # Eu calculo quanto da barra deve estar preenchido desde o inicio do ciclo.
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

    def mostrar_ajuda(self):
        # Eu explico ao usuario a duracao dos ciclos e a regra da pausa longa.
        messagebox.showinfo(
            "Como funciona",
            f"Trabalhe por {self.duracoes['focus']} minutos e faca uma pausa curta de "
            f"{self.duracoes['short_break']} minutos.\n\n"
            f"A cada {self.intervalo_pausa_longa} ciclos de foco, a pausa fica mais longa: "
            f"{self.duracoes['long_break']} minutos.",
        )


# Eu crio a janela e inicio o loop de eventos somente quando executo este arquivo diretamente.
if __name__ == "__main__":
    janela_principal = tk.Tk()
    PomodoroApp(janela_principal)
    janela_principal.mainloop()
