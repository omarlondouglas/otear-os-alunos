# Validar a entrega do aluno

O aluno recebe uma **vault**: a pasta inteira que contém `SOUL.md`, agentes,
skills, squads, sistemas e memória local. O comando `npx` não substitui essa
vault; ele somente executa diagnóstico e validação nela.

## Antes de entregar

Na raiz da vault, rode:

```powershell
npx . profiles
npx . doctor --profile essencial
npx . validate
```

O aceite mínimo é: `doctor` terminar com `OK` no perfil `essencial` e
`validate` informar que as verificações internas passaram. Depois abra
`ATIVAR-HERMES.md`, selecione esta mesma pasta como diretório de trabalho no
Hermes e faça um pedido simples. O Hermes deve citar a rota escolhida e avisar
pré-requisitos externos antes de rodar sistemas técnicos.

## Aceite Hermes-native

Com o Hermes fechado ou em uma nova sessão, instale apenas as skills Otear em uma home
Hermes escolhida pelo aluno:

```powershell
powershell -ExecutionPolicy Bypass -File .\produto-otear-os\hermes-native\scripts\Validar-HermesNative.ps1
powershell -ExecutionPolicy Bypass -File .\produto-otear-os\hermes-native\scripts\Instalar-HermesNative.ps1 -HermesHome "C:\caminho\para\Hermes"
```

Abra uma conversa nova no Hermes com esta vault como diretório de trabalho e teste,
um por vez:

```text
Use Otear Router e diga qual rota atende uma campanha de captação de leads.
Ative Otear Modo Leigo e me explique o que é um squad.
Crie uma skill Otear para qualificar leads e salve na minha área do aluno.
Crie um agente Otear para revisar uma copy e salve na minha área do aluno.
Crie um squad Otear para uma campanha e salve na minha área do aluno.
```

O aceite exige os três arquivos em `produto-otear-os/minhas-skills`,
`produto-otear-os/meus-agentes` e `produto-otear-os/meus-squads`. A execução com
subagentes só pode ser aceita se a sessão Hermes disponibilizar `delegate_task`; sem
essa ferramenta, o squad deve ser executado sequencialmente. AIOX e Nirvana são
bibliotecas internas e não são runtimes Hermes. A instalação inclui 31 skills: quatro
de núcleo, 18 de sistemas e nove capacidades complementares. Confira o mapeamento de cada rota em
`produto-otear-os/hermes-native/route-skill-map.json`; `Otear Trafego Pago` usa a
mesma skill de `Otear Trafego`.

## Perfis opcionais

```powershell
npx . doctor --profile criacao
npx . doctor --profile automacao-local
npx . doctor --profile infra-docker
```

Ausência de Python é aviso no perfil `automacao-local`; ausência de Docker só é
falha no perfil `infra-docker`. Portanto, **Docker não é requisito do aluno
comum** e nunca é instalado automaticamente.

Para ver os passos de um perfil sem instalar nada:

```powershell
npx . setup --profile infra-docker
```

## Depois de publicar no NPM

Esta versão ainda é local: `npx .` funciona porque há um `package.json` na raiz
da vault. Só depois de publicar um pacote com nome disponível no NPM será
possível usar, de dentro de uma vault já baixada:

```powershell
npx <nome-publicado> validate --vault .
```

Não publique a vault inteira como dependência: o pacote público deve carregar a
CLI leve, enquanto o aluno mantém a vault entregue localmente.
