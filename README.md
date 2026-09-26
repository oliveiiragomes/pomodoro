# Pomodoro

**Trabalhe com foco. Faça pausas no ritmo certo.**

Um timer desktop baseado na técnica Pomodoro, com contagem regressiva, progresso do ciclo e acompanhamento dos focos concluídos.

`Python` · `Tkinter` · `pygame-ce`

## O ciclo

| Etapa | Duração padrão |
| --- | ---: |
| Foco | 25 min |
| Pausa curta | 5 min |
| Pausa longa | 15 min a cada 4 focos |

## Recursos

- Inicie, pause, reinicie ou pule a etapa atual.
- Ative o início automático de focos e pausas de forma independente.
- Ajuste as durações de 1 a 180 minutos e o intervalo da pausa longa de 2 a 12 focos.
- Escolha entre os temas Claro, Neon escuro, Retro e Verde Floresta.
- Selecione um alarme MP3 da pasta `audios`, ouça uma prévia e ajuste o volume durante a reprodução.
- Use o modo mini para manter o cronômetro em uma janela compacta.

As configurações permanecem ativas durante a sessão e voltam aos valores padrão quando o aplicativo é reiniciado.

## Comece

Requer Python com Tkinter disponível.

```bash
python -m pip install -r requirements.txt
python main.py
```

## Testes

```bash
python -m unittest -v
```
