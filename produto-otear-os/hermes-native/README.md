# Hermes-native para Otear OS

Este pacote torna o Hermes o operador do aluno. Ele instala 31 skills namespaced:
quatro skills de núcleo e 18 skills operacionais, uma para cada sistema público do
Otear OS. A rota `Otear Trafego Pago` é um alias de `otear-trafego`, portanto não
cria uma segunda skill com comportamento diferente.

## Instalar

Na raiz da vault, indique a home Hermes que o aluno escolheu:

```powershell
powershell -ExecutionPolicy Bypass -File .\produto-otear-os\hermes-native\scripts\Instalar-HermesNative.ps1 -HermesHome "C:\caminho\para\Hermes"
```

Para atualizar uma instalacao anterior do Otear OS, acrescente `-Force`. O script
substitui somente `<HermesHome>\skills\otear-os`.

## Limites

## Capacidades complementares OpenSquad

`otear-apuracao-fontes`, `otear-pesquisa-noticias`, `otear-redacao-jornalistica`,
`otear-verificacao-factual`, `otear-criador-imagens`, `otear-buscador-imagens`,
`otear-canva` e `otear-publicador-instagram` complementam os sistemas públicos; não criam
novas rotas nem exigem que o aluno instale o runtime OpenSquad.

`otear-modo-leigo` é uma capacidade transversal: explica qualquer rota, agente, skill ou
dependência do Otear em linguagem simples. Ela não inicia sistemas técnicos; depois que o
aluno entender e aceitar, encaminha para a skill Otear adequada.

Pesquisa atual exige fontes acessíveis na sessão. Renderização exige browser/Playwright;
Canva exige integração MCP/OAuth; e publicação no Instagram exige dependências locais e
confirmação explícita final do aluno. Nenhuma dessas skills armazena segredos na vault.

As skills leem AIOX, Nirvana, OpenSquad e PI Squad apenas como bibliotecas de
método; elas não chamam os runtimes nativos desses projetos. A criação de
subagentes depende de a sessão Hermes oferecer `delegate_task`. A relação entre
rotas e skills está em `route-skill-map.json` e é verificada antes da entrega.
