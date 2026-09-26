import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


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

MODOS = {
    "focus": {"label": "FOCO", "minutes": 25},
    "short_break": {"label": "PAUSA CURTA", "minutes": 5},
    "long_break": {"label": "PAUSA LONGA", "minutes": 15},
}


class EstilosTemas:
    """Aplica paletas e fontes à janela e aos widgets existentes."""

    def _fonte(self, tamanho: int, peso: str = "normal"):
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

        # Atualiza a árvore de widgets sem recriar a tela nem perder seu estado.
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
