@echo off
chcp 65001 >nul
title Limpeza de Branches de PRs Fechados - CarimboPDF

echo.
echo =====================================================
echo  🧹 LIMPEZA DE BRANCHES DE PRS FECHADOS
echo =====================================================
echo.
echo Este script irá ajudar a limpar branches de Pull 
echo Requests que foram fechados ou merged.
echo.
echo IMPORTANTE:
echo - GitHub NÃO permite excluir PRs (isso é normal)
echo - PRs fechados ficam visíveis no histórico
echo - Este script apenas limpa os BRANCHES
echo.

python scripts\cleanup_closed_pr_branches.py

echo.
echo =====================================================
echo  📖 INFORMAÇÕES ADICIONAIS
echo =====================================================
echo.
echo Para ver PRs fechados no GitHub, acesse:
echo https://github.com/maandrake/CarimboPDF/pulls?q=is:pr+is:closed
echo.
echo Para ver PRs merged:
echo https://github.com/maandrake/CarimboPDF/pulls?q=is:pr+is:merged
echo.

pause