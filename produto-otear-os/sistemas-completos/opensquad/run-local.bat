@echo off
REM ============================================================
REM run-local.bat — Roda o pipeline direto do terminal Windows
REM Uso: run-local.bat "tema" [periodo] [modelo]
REM
REM Exemplos:
REM   run-local.bat "IA e Agentes"
REM   run-local.bat "Automacao" "Ultimas 24h" claude-haiku-4-5-20251001
REM   run-local.bat "Empreendedorismo" "" claude-opus-4-6
REM ============================================================

SET TOPIC=%~1
IF "%TOPIC%"=="" SET TOPIC=IA e Agentes

SET PERIOD=%~2
IF "%PERIOD%"=="" SET PERIOD=Ultimas 24h

SET MODEL=%~3
IF "%MODEL%"=="" SET MODEL=claude-haiku-4-5-20251001

echo.
echo ==========================================
echo   O Tear Carrosseis - Local Run
echo ==========================================
echo   Tema:    %TOPIC%
echo   Periodo: %PERIOD%
echo   Modelo:  %MODEL%
echo ==========================================
echo.

claude -p "Execute /opensquad run noticias-carrossel-ia\n\nRESPOSTAS PRE-DEFINIDAS PARA OS CHECKPOINTS:\n\nCheckpoint 1 - Foco do Dia:\n- Tema: opcao 4 (Noticia especifica) - o tema e: %TOPIC%\n- Periodo: %PERIOD%\n\nCheckpoint 2 - Estrategia de Imagens:\n- Imagens: opcao 2 (Sim — gerar com IA via Gemini)\n- Slides com imagem: capa\n\nCheckpoint 3 - Aprovacao Final:\n- Escolha: opcao 3 (Salvar sem publicar)\n\nExecute o pipeline completo do inicio ao fim usando essas respostas. Nao pause para pedir confirmacao." --model %MODEL% --dangerously-skip-permissions --output-format text --verbose

echo.
echo Concluido. Slides em: squads\noticias-carrossel-ia\output\
