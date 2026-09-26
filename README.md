# Pomodoro

Aplicativo desktop para organizar períodos de foco e descanso usando a técnica Pomodoro. A tela mostra o tempo restante, o progresso do ciclo e a quantidade de focos concluídos.

## Instalação e execução

```bash
python -m pip install -r requirements.txt
python main.py
```

## Ciclo padrão

- Foco: 25 minutos.
- Pausa curta: 5 minutos.
- Pausa longa: 15 minutos a cada 4 focos.

As durações podem ser ajustadas entre 1 e 180 minutos, e o intervalo da pausa longa entre 2 e 12 focos.

## Recursos

- Iniciar, pausar, reiniciar ou pular um ciclo.
- Iniciar focos e pausas automaticamente, com opções independentes.
- Escolher entre os temas Claro, Neon escuro, Retro e Verde Floresta.
- Reproduzir um alarme MP3 da pasta `audios` e ajustar seu volume durante a reprodução.
- Usar o modo mini para manter o cronômetro em uma janela compacta.

As configurações ficam ativas durante a sessão e voltam aos valores padrão quando o aplicativo é reiniciado.
