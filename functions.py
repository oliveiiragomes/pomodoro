from tkinter import messagebox
import pygame


class FuncoesTemporizador:
    """Ações do timer, transições entre modos, áudio e visualização mini."""

    def entrar_modo_compacto(self):
        self.modo_compacto = True
        self.interface_completa.pack_forget()
        self.interface_compacta.pack(fill="both", expand=True)
        self.janela.geometry("110x48")
        self.janela.minsize(110, 48)
        self.janela.resizable(False, False)
        self._ocultar_botao_restaurar()
        self._atualizar_interface()

    def sair_modo_compacto(self):
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
        self._cancelar_ocultacao_botao_restaurar()
        self.botao_restaurar.place(relx=1.0, x=-12, y=12, anchor="ne")

    def _ocultar_botao_restaurar(self):
        self.botao_restaurar.place_forget()
        self.id_agendamento_botao_restaurar = None

    def _agendar_ocultacao_botao_restaurar(self, _=None):
        self._cancelar_ocultacao_botao_restaurar()
        self.id_agendamento_botao_restaurar = self.janela.after(
            150, self._ocultar_botao_restaurar
        )

    def _cancelar_ocultacao_botao_restaurar(self, _=None):
        if self.id_agendamento_botao_restaurar is not None:
            self.janela.after_cancel(self.id_agendamento_botao_restaurar)
            self.id_agendamento_botao_restaurar = None

    def alternar_timer(self):
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
        messagebox.showinfo(
            "Pomodoro",
            f"Tempo concluido. Agora: {self.MODOS[self.modo]['label'].lower()}.",
        )
        self._parar_som_alarme()
        # O início automático depende do tipo do modo que acabou de ser selecionado.
        iniciar_proximo = (
            self.iniciar_focos_automaticamente
            if self.modo == "focus"
            else self.iniciar_pausas_automaticamente
        )
        if iniciar_proximo:
            self._iniciar_contagem()

    def _concluir_ciclo_foco(self):
        self.ciclos_foco_concluidos += 1
        # Cada intervalo configurado termina em pausa longa; os demais são curtos.
        return (
            "long_break"
            if self.ciclos_foco_concluidos % self.intervalo_pausa_longa == 0
            else "short_break"
        )

    def reiniciar_timer(self):
        self.em_execucao = False
        self._cancelar_contagem()
        self.segundos_restantes = self.duracoes[self.modo] * 60
        self._atualizar_interface()

    def pular_modo(self):
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
        if self.id_agendamento_contagem is not None:
            self.janela.after_cancel(self.id_agendamento_contagem)
            self.id_agendamento_contagem = None

    def _tocar_som_alarme(self, som=None, volume=None):
        arquivo_audio = self.arquivos_audio.get(som or self.som_alarme)
        if arquivo_audio is None:
            # O sino do Tk mantém o aviso funcional quando não há MP3 disponível.
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

    def mostrar_ajuda(self):
        messagebox.showinfo(
            "Como funciona",
            f"Trabalhe por {self.duracoes['focus']} minutos e faca uma pausa curta de "
            f"{self.duracoes['short_break']} minutos.\n\n"
            f"A cada {self.intervalo_pausa_longa} ciclos de foco, a pausa fica mais longa: "
            f"{self.duracoes['long_break']} minutos.",
        )
