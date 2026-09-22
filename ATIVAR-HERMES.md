# Ativar o Hermes nesta vault

## Resultado esperado

O Hermes trabalha a partir desta pasta, lê `SOUL.md` como instrução principal e
descobre todos os componentes pelo catálogo. Não é preciso usar caminhos como
`D:\...`, `{OTEAR_VAULT_ROOT}` ou a pasta do autor do material.

## Ativação portátil

1. Abra esta pasta como vault no Obsidian (ou como pasta/projeto no Hermes).
2. No Hermes, selecione **esta mesma pasta** como diretório de trabalho. A raiz
   é a pasta que contém `SOUL.md`, `START AQUI.md` e `produto-otear-os`.
3. Em uma conversa nova, envie o texto de `OTEAR-BOOTSTRAP.md` ou cole o bloco
   abaixo.
4. Peça uma tarefa normal. Antes de executar, o Hermes deve confirmar a rota
   no roteador e os requisitos no catálogo.

```text
Você está na raiz desta vault do Otear OS. Leia nesta ordem:
1. SOUL.md
2. MAPA DO OTEAR OS.md
3. produto-otear-os/nucleo-otear/CONTRATO-OPERACIONAL.md
4. produto-otear-os/nucleo-otear/roteador-otear.yaml
5. produto-otear-os/catalogo-integracao.json
6. .system/USER.md e .system/MEMORY.md

Use somente caminhos relativos a esta vault. Para cada pedido, selecione a rota
do Otear OS, verifique se os arquivos existem e informe qualquer pré-requisito
externo antes de tentar rodar um sistema.
```

## Camada Hermes-native recomendada

O modo recomendado para alunos é instalar as 31 skills portáteis do Otear OS. Elas
incluem roteamento, criação de skills, agentes e squads, os sistemas públicos,
capacidades complementares e o `Otear Modo Leigo`. AIOX/Nirvana são usados apenas como
biblioteca de método, nunca como runtime obrigatório.

No PowerShell, na raiz desta vault, execute uma vez, informando a pasta Hermes que o
aluno escolheu:

```powershell
powershell -ExecutionPolicy Bypass -File .\produto-otear-os\hermes-native\scripts\Instalar-HermesNative.ps1 -HermesHome "C:\caminho\para\Hermes"
```

O instalador só cria `<HermesHome>\skills\otear-os`. Ele não lê, copia ou altera
chaves, sessões, memória, configurações ou skills já existentes. Para atualizar apenas
essa pasta no futuro, acrescente `-Force`.

Em uma nova conversa, teste:

```text
Use a skill Otear Router para localizar esta vault e criar uma skill de qualificação de leads.
Ative Otear Modo Leigo e me explique o que é um squad.
```

Veja `produto-otear-os/hermes-native/README.md` e `VALIDAR-ALUNO.md` para o aceite.

## Perfil Hermes legado (referência técnica)

O pacote em `produto-otear-os/sistemas-completos/hermes-profile-agenciasemesforco`
é um perfil complementar: ele oferece skills e configurações do Hermes, mas não
substitui a raiz desta vault. Importe-o somente pela tela/comando de importação
da versão do Hermes instalada e mantenha o diretório de trabalho apontando para
esta vault.

Ele é material de referência técnica, não o caminho recomendado para o aluno. Prefira
sempre a camada em `produto-otear-os/hermes-native`.

O arquivo `SOUL.md` do perfil usa o mapa relativo
`MAPA-PORTAVEL-OTEAR.md`; não há caminho absoluto para ajustar. Se sua versão do
Hermes não importar perfis, a ativação acima continua suficiente, pois o
bootstrap abre o mapa principal diretamente.

## Verificação antes de entregar ao aluno

No PowerShell, na raiz da vault, execute:

```powershell
npx . doctor --profile essencial
npx . validate
```

O `npx .` executa o validador que está nesta própria vault; ele não publica,
não baixa Docker e não instala dependências. Veja `VALIDAR-ALUNO.md` para os
perfis opcionais de criação, automação local e infraestrutura Docker.

Como alternativa sem Node.js, execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\produto-otear-os\nucleo-otear\scripts\Validar-OtearOS.ps1
```

O comando não instala nada e não acessa a internet. Ele confirma os caminhos
internos declarados no catálogo e no roteador. Pré-requisitos como Docker,
Python, contas, modelos e chaves de API continuam sendo verificados por cada
sistema quando ele for configurado.
