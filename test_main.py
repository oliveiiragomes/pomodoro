import unittest
from unittest.mock import Mock, patch

from main import PomodoroApp, pygame


def criar_app_sem_interface():
    app = PomodoroApp.__new__(PomodoroApp)
    app.janela = Mock()
    app.janela.after.return_value = "after-1"
    app.id_agendamento_contagem = None
    app.modo = "focus"
    app.em_execucao = False
    app.duracoes = {"focus": 25, "short_break": 5, "long_break": 15}
    app.segundos_restantes = 25 * 60
    app.ciclos_foco_concluidos = 0
    app.intervalo_pausa_longa = 4
    app.iniciar_pausas_automaticamente = False
    app.iniciar_focos_automaticamente = False
    app._atualizar_interface = Mock()
    app._tocar_som_alarme = Mock()
    app._parar_som_alarme = Mock()
    return app


class TimerLogicTests(unittest.TestCase):
    def test_start_waits_one_second_before_decrementing(self):
        app = criar_app_sem_interface()

        app.alternar_timer()

        self.assertTrue(app.em_execucao)
        self.assertEqual(app.segundos_restantes, 25 * 60)
        self.assertEqual(app.janela.after.call_args.args[0], 1000)

    def test_pause_cancels_the_pending_tick_without_changing_time(self):
        app = criar_app_sem_interface()
        app.alternar_timer()

        app.alternar_timer()

        self.assertFalse(app.em_execucao)
        self.assertEqual(app.segundos_restantes, 25 * 60)
        app.janela.after_cancel.assert_called_once_with("after-1")

    def test_intermediate_tick_decrements_and_schedules_the_next_tick(self):
        app = criar_app_sem_interface()
        app.em_execucao = True
        app.segundos_restantes = 3
        app.id_agendamento_contagem = "previous-tick"

        app._contar_segundo()

        self.assertEqual(app.segundos_restantes, 2)
        self.assertEqual(app.id_agendamento_contagem, "after-1")
        self.assertEqual(app.janela.after.call_args.args[0], 1000)

    def test_zero_completes_on_the_tick_that_reaches_it(self):
        app = criar_app_sem_interface()
        app.em_execucao = True
        app.segundos_restantes = 1

        with patch("main.messagebox.showinfo"):
            app._contar_segundo()

        self.assertEqual(app.modo, "short_break")
        self.assertEqual(app.segundos_restantes, 5 * 60)
        self.assertFalse(app.em_execucao)
        app.janela.after.assert_not_called()

    def test_auto_started_mode_keeps_its_full_duration_until_first_tick(self):
        app = criar_app_sem_interface()
        app.modo = "short_break"
        app.iniciar_focos_automaticamente = True

        with patch("main.messagebox.showinfo"):
            app._concluir_modo()

        self.assertEqual(app.modo, "focus")
        self.assertTrue(app.em_execucao)
        self.assertEqual(app.segundos_restantes, 25 * 60)
        self.assertEqual(app.janela.after.call_args.args[0], 1000)

    def test_auto_started_break_keeps_its_full_duration_until_first_tick(self):
        app = criar_app_sem_interface()
        app.iniciar_pausas_automaticamente = True

        with patch("main.messagebox.showinfo"):
            app._concluir_modo()

        self.assertEqual(app.modo, "short_break")
        self.assertTrue(app.em_execucao)
        self.assertEqual(app.segundos_restantes, 5 * 60)
        self.assertEqual(app.janela.after.call_args.args[0], 1000)

    def test_completed_mode_stays_paused_when_auto_start_is_disabled(self):
        app = criar_app_sem_interface()
        app.iniciar_pausas_automaticamente = False

        with patch("main.messagebox.showinfo"):
            app._concluir_modo()

        self.assertEqual(app.modo, "short_break")
        self.assertFalse(app.em_execucao)
        app.janela.after.assert_not_called()

    def test_long_break_uses_the_configured_focus_interval(self):
        app = criar_app_sem_interface()

        modos_padrao = [app._concluir_ciclo_foco() for _ in range(4)]
        self.assertEqual(
            modos_padrao,
            ["short_break", "short_break", "short_break", "long_break"],
        )

        app.intervalo_pausa_longa = 2
        app.ciclos_foco_concluidos = 0
        self.assertEqual(
            [app._concluir_ciclo_foco() for _ in range(4)],
            ["short_break", "long_break", "short_break", "long_break"],
        )

    def test_theme_source_colors_are_unique_for_role_mapping(self):
        for theme, colors in PomodoroApp.TEMAS.items():
            with self.subTest(theme=theme):
                mapped_colors = [
                    color for role, color in colors.items() if role != "accent_text"
                ]
                self.assertEqual(len(mapped_colors), len(set(mapped_colors)))

    def test_live_volume_callback_updates_only_playing_audio(self):
        app = criar_app_sem_interface()

        with patch.object(pygame, "mixer", Mock()) as mixer_mock:
            mixer_mock.get_init.return_value = True
            mixer_mock.music.get_busy.return_value = True
            app._ajustar_volume_alarme("35")
            mixer_mock.music.set_volume.assert_called_once_with(0.35)

            mixer_mock.music.set_volume.reset_mock()
            mixer_mock.music.get_busy.return_value = False
            app._ajustar_volume_alarme("80")
            mixer_mock.music.set_volume.assert_not_called()

    def test_window_sizing_helper_expands_to_fit_current_theme(self):
        app = criar_app_sem_interface()
        app.modo_compacto = False
        app.interface_completa = Mock()
        app.interface_completa.winfo_reqwidth.return_value = 800
        app.interface_completa.winfo_reqheight.return_value = 700
        app.janela.winfo_width.return_value = 720
        app.janela.winfo_height.return_value = 620

        app._ajustar_tamanho_janela()

        app.janela.minsize.assert_called_once_with(800, 700)
        app.janela.geometry.assert_called_once_with("800x700")

    def test_skipping_focus_counts_it_but_skipping_break_does_not(self):
        app = criar_app_sem_interface()

        app.pular_modo()
        self.assertEqual((app.modo, app.ciclos_foco_concluidos), ("short_break", 1))

        app.pular_modo()
        self.assertEqual((app.modo, app.ciclos_foco_concluidos), ("focus", 1))
        self.assertFalse(app.em_execucao)

    def test_restart_cancels_pending_tick_and_preserves_cycle_count(self):
        app = criar_app_sem_interface()
        app.modo = "short_break"
        app.segundos_restantes = 17
        app.ciclos_foco_concluidos = 3
        app.em_execucao = True
        app.id_agendamento_contagem = "after-1"

        app.reiniciar_timer()

        app.janela.after_cancel.assert_called_once_with("after-1")
        self.assertEqual(app.segundos_restantes, 5 * 60)
        self.assertEqual(app.ciclos_foco_concluidos, 3)
        self.assertFalse(app.em_execucao)


if __name__ == "__main__":
    unittest.main()