---
id: prospeccao-google-maps
name: Prospecção de Negócios Locais via Google Maps
trigger: Quando o usuário precisar encontrar e listar empresas locais (restaurantes, clínicas, imobiliárias, escritórios) com nome, telefone, endereço, site e avaliações para prospecção comercial
version: 1.0.0
---

# Prospecção de Negócios Locais via Google Maps

Esta skill ensina e executa o levantamento ativo de empresas locais para criar listas qualificadas de prospecção comercial sem pagar por ferramentas caras de dados.

## Requisitos e Princípio de Funcionamento
* **Como funciona:** O robô navega pelo Google Maps buscando pelo `[Nicho / Termo]` na `[Cidade / Região]` desejada e extrai os dados públicos de cada estabelecimento.
* **Atenção sobre Bloqueios (IP):** O Google Maps costuma apresentar telas de consentimento/CAPTCHA quando acessado via servidores em nuvem (VPS/Datacenters). **O método mais seguro e confiável é rodar o script na sua máquina local com IP residencial.**

---

## Procedimento de Execução

### Passo 1: Definição do Alvo
Defina com clareza:
1. **Nicho de atuação:** Ex: *Clínicas Odontológicas*, *Restaurantes*, *Corretores de Imóveis*, *Escritórios de Contabilidade*.
2. **Localização geográfica:** Ex: *Campinas - SP*, *Barra da Tijuca - RJ*, *Curitiba - PR*.
3. **Volume desejado:** Recomendado de 20 a 50 contatos por lote para manter alta personalização na abordagem.

### Passo 2: Extração dos Dados
Para cada empresa listada no Google Maps, extraia os seguintes campos:
* **Nome da Empresa:** Nome comercial registrado.
* **Categoria:** Tipo de estabelecimento (ex: Clínica médica, Imobiliária).
* **Telefone / WhatsApp:** Número comercial para primeiro contato.
* **Avaliação (Rating) e Número de Reviews:** Indicador de maturidade e reputação.
* **Website / Redes:** Para checar se já possuem site rápido, automação de WhatsApp ou pixels instalados.
* **Endereço Completo:** Para geolocalização e contextualização na mensagem de abordagem.

### Passo 3: Qualificação e Triagem do Lead
Antes de disparar mensagens, classifique a lista:
* **Sem Site / Site Desatualizado:** Oportunidade para vender criação de página de alta conversão + automação.
* **Muitas avaliações e sem resposta:** Oportunidade para oferecer agente de atendimento e reputação no Google.
* **Sem botão direto de WhatsApp no site:** Oportunidade para implementar funil de atendimento e captura.

### Passo 4: Formato de Saída (Planilha de Prospecção)
A saída deve ser entregue em CSV ou tabela Markdown com as colunas:
`Nome | Nicho | Telefone | Cidade | Nota/Reviews | Tem Site? | Gancho de Abordagem`
