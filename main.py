import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import pygame

from functions import FuncoesTemporizador
from screens import ConstrucaoTelas
from styles import EstilosTemas, MODOS, TEMAS


class AplicativoPomodoro(FuncoesTemporizador, ConstrucaoTelas, EstilosTemas):
    """Coordena o estado do Pomodoro e combina seus módulos de interface."""

    TEMAS = TEMAS
    MODOS = MODOS

    def __init__(self, janela: tk.Tk):
        self.janela = janela
        self.janela.title("Pomodoro")
        self.janela.geometry("720x620")
        self.janela.minsize(620, 560)
        self.tema = "Claro"
        self.CORES = dict(self.TEMAS[self.tema])
        self.janela.configure(bg=self.CORES["background"])

        self.modo = "focus"
        self.em_execucao = False
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
        self.modo_compacto = False
        self.id_agendamento_botao_restaurar = None

        self._montar_interface()
        self._atualizar_interface()


# Mantém compatibilidade com código que já importa o nome antigo.
PomodoroApp = AplicativoPomodoro


if __name__ == "__main__":
    janela_principal = tk.Tk()
    AplicativoPomodoro(janela_principal)
    janela_principal.mainloop()
