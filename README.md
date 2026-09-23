# Otear OS para Alunos

Bem-vindo ao Otear OS. Esta pasta é a sua cópia local do ambiente de trabalho: nela estão o guia de uso, as instruções para o Hermes, agentes, skills, squads, workflows, exemplos e sistemas incluídos na entrega.

O Otear OS organiza esses recursos para ajudar você a transformar um pedido em um processo de trabalho com IA. A vault não é, por si só, um modelo de IA nem um serviço hospedado: para conversar e executar tarefas, use o Hermes e um modelo/provedor configurado nele. Alguns recursos também dependem de ferramentas, contas ou integrações externas; quando for o caso, a documentação do sistema informa os requisitos.

## Comece por aqui

1. Baixe e extraia a pasta completa `otear-os-aluno` no seu computador. Não abra somente o arquivo ZIP nem mova apenas o `README.md`.
2. Abra [`START AQUI.md`](START%20AQUI.md) ou siga a trilha em [`00-COMECE-AQUI/00 - Leia Primeiro.md`](00-COMECE-AQUI/00%20-%20Leia%20Primeiro.md).
3. Leia [`01-PRE-REQUISITOS/Checklist Inicial.md`](01-PRE-REQUISITOS/Checklist%20Inicial.md) e confira se você tem acesso ao Hermes.
4. Abra esta pasta no Obsidian, se quiser navegar pelas notas como uma vault. O Obsidian é recomendado, mas não é necessário para ler os arquivos ou usar a pasta com o Hermes.
5. Configure o Hermes para trabalhar com **a raiz desta pasta** — a pasta onde estão `SOUL.md`, `OTEAR-BOOTSTRAP.md` e `produto-otear-os` — seguindo [`ATIVAR-HERMES.md`](ATIVAR-HERMES.md).
6. Em uma conversa nova do Hermes, use o texto de [`OTEAR-BOOTSTRAP.md`](OTEAR-BOOTSTRAP.md) e faca um pedido simples, por exemplo: `Otear OS, me ajude a planejar uma campanha para este produto: ...`.

> Dica: mantenha a pasta inteira no mesmo lugar. O mapa, o catálogo e os links internos dependem da estrutura de pastas.

## O que e cada recurso

| Recurso | O que faz |
|---|---|
| **Vault** | Esta pasta completa com documentacao, biblioteca e arquivos de trabalho do aluno. |
| **Agente** | Define uma função especializada, como pesquisar, revisar ou planejar. |
| **Skill** | Ensina um procedimento reutilizável para uma tarefa. |
| **Squad** | Organiza várias funções em etapas para uma entrega maior. No Hermes, a execução pode ser sequencial; subagentes só estão disponíveis se a sessão oferecer `delegate_task`. |
| **Workflow** | Um roteiro ordenado para conduzir um processo. |
| **Sistema** | Um conjunto mais completo de instruções, arquivos e, em alguns casos, aplicações e dependências externas. |
| **Hermes-native** | Skills portateis do Otear preparadas para serem instaladas na home do Hermes. |

## O que esta incluido

- **Comece aqui e suporte:** orientacao inicial, pre-requisitos, exemplos e diagnostico.
- **Nucleo do Otear OS:** contrato operacional, roteador, catalogo de integracao e criterios de qualidade.
- **Biblioteca de trabalho:** agentes, skills, squads, workflows, templates, conteudo de copy e exemplos.
- **Criacao e personalizacao:** areas para guardar seus proprios agentes, skills e squads.
- **Sistemas prontos e completos:** materiais e ferramentas para atividades como prospeccao, sites, video, marketing, pesquisa, conteudo e outras rotas descritas no mapa e no catalogo.
- **Skills Hermes-native:** conjunto de skills do Otear que voce pode instalar pelo script documentado em [`produto-otear-os/hermes-native/README.md`](produto-otear-os/hermes-native/README.md).
- **Validacao local:** uma CLI pequena e scripts para conferir arquivos e dependencias sem instalar Docker.

O mapa principal é [`MAPA DO OTEAR OS.md`](MAPA%20DO%20OTEAR%20OS.md). Consulte também [`INDICE-DA-VAULT.md`](INDICE-DA-VAULT.md) para localizar notas e componentes.

## Ativar as skills no Hermes

O Hermes pode ler a vault como contexto de trabalho. Para disponibilizar tambem as skills portateis do Otear, abra o PowerShell nesta pasta e execute o instalador, informando a pasta de configuracao do Hermes usada no seu computador:

```powershell
powershell -ExecutionPolicy Bypass -File .\produto-otear-os\hermes-native\scripts\Instalar-HermesNative.ps1 -HermesHome "C:\caminho\para\Hermes"
```

O script copia somente as skills do Otear para `<HermesHome>\skills\otear-os`. Feche e abra uma nova conversa no Hermes depois da instalacao. Antes de instalar, leia [`ATIVAR-HERMES.md`](ATIVAR-HERMES.md); para validar as skills e os passos de aceite, consulte [`VALIDAR-ALUNO.md`](VALIDAR-ALUNO.md).

O Hermes e o provedor/modelo de IA não estão embutidos nesta pasta. A disponibilidade de modelos, ferramentas e delegação depende da configuração da sua sessão Hermes.

## Dependencias: o que e necessario e o que e opcional

- **Para ler e navegar:** nenhum ambiente de programação é necessário. Obsidian é opcional.
- **Para conversar e executar com IA:** Hermes funcionando, acesso a um modelo/provedor configurado e esta pasta selecionada como contexto/diretorio de trabalho.
- **Para validar a vault pela CLI:** Node.js 18 ou superior. Na raiz da pasta, use os comandos locais abaixo. A CLI não é necessária para conversar com o Hermes.
- **Para um sistema especifico:** podem ser necessarios Python, um navegador, Playwright, Docker, credenciais ou integracoes externas. Isso varia por sistema; consulte o README e o catalogo dele antes de configurar.

Docker não é requisito para o uso comum da vault e não é instalado automaticamente. A ausência de uma dependência opcional não impede o uso das notas, skills e rotas que não dependem dela.

### Validacao opcional com Node.js

Na raiz desta pasta, abra o terminal e execute:

```powershell
npx . profiles
npx . doctor --profile essencial
npx . validate
```

Esses comandos usam o `package.json` e a CLI presentes nesta própria pasta. Eles não publicam o pacote, não instalam Docker e não validam contas externas, chaves ou todos os sistemas de ponta a ponta. Para detalhes e critérios de aceite, veja [`VALIDAR-ALUNO.md`](VALIDAR-ALUNO.md).

> O `package.json` atual é privado e local. Não é necessário publicar ou instalar a vault via npm para usar esta entrega. `npx .` serve apenas para executar a CLI local quando Node.js estiver instalado.

## Como pedir uma tarefa

Explique o resultado desejado e passe o contexto que você já tem. Por exemplo:

```text
Otear OS, planeje uma campanha para o meu produto.

Produto/servico: [descreva]
Publico: [para quem]
Objetivo: [o que precisa acontecer]
Canal: [onde vai usar]
Prazo ou restricoes: [se houver]
```

Para trabalhos maiores, voce pode pedir que o Hermes escolha ou use um squad. Para uma atividade pontual, peca uma skill ou agente. Se nao souber qual escolher, descreva o objetivo e deixe o roteador indicar a rota. Veja [`02-COMO-USAR/Atalhos de Pedido do Otear OS.md`](02-COMO-USAR/Atalhos%20de%20Pedido%20do%20Otear%20OS.md) para mais exemplos.

O Hermes deve conferir os arquivos e requisitos disponíveis, explicar limitações relevantes e pedir informações quando necessário. A revisão e aprovação final continuam sendo suas: não autorize publicações, gastos ou alterações em serviços externos sem conferir exatamente o que será feito.

## Memoria e privacidade

Esta entrega é uma pasta local. O Hermes pode usar arquivos da vault como contexto, e os arquivos em `.system` podem guardar preferências e memória de trabalho. Revise o que será salvo e mantenha um backup privado. Não coloque senhas, chaves de API, cookies ou arquivos `.env` em notas, prompts, repositórios públicos ou pastas compartilhadas. Use os mecanismos seguros oferecidos pelo serviço correspondente.

Os materiais desta vault não incluem automaticamente suas contas, credenciais, dados de clientes, modelo de IA ou serviços de terceiros. Você configura qualquer integração externa somente quando decidir usar o sistema que precisa dela.

## Ajuda e diagnostico

- Se estiver comecando, volte a [`START AQUI.md`](START%20AQUI.md).
- Se uma skill, sistema ou integracao nao funcionar, consulte [`06-SUPORTE-E-DIAGNOSTICO/Se Algo Nao Funcionar.md`](06-SUPORTE-E-DIAGNOSTICO/Se%20Algo%20Nao%20Funcionar.md).
- Para requisitos e validacao da entrega, consulte [`VALIDAR-ALUNO.md`](VALIDAR-ALUNO.md).
- Para detalhes de um sistema, abra o README ou `LEIA-ME-ALUNO.md` dentro da pasta desse sistema.

## Licenca de uso

Use esta cópia conforme os termos de acesso e licença fornecidos com sua turma. Não publique nem redistribua a vault, seus sistemas ou materiais privados sem autorização.
