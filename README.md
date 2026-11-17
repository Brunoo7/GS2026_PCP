# Citizen Assist AI

Assistente digital de orientação ao cidadão, executado no terminal, desenvolvido em Python para a Global Solution 2026.2 (Pensamento Computacional e Automação com Python, desafio CitizenTech).

## Integrantes

| Nome | RM |
|---|---|
| Bernardo Zauza Amorim | 568808 |
| Bruno Almeida de Oliveira | 572648 |
| Gabriel Góes Nunes Pereira | 571735 |

## Público e problema escolhidos

**Público:** jovens que estão entrando na vida adulta e no primeiro emprego.

**Problema:** quem está começando precisa de vários documentos e serviços (título de eleitor, identidade, CPF, carteira de trabalho, alistamento militar, Cartão SUS, conta gov.br, CadÚnico, MEI), mas a informação está espalhada, em linguagem técnica e misturada com sites que parecem oficiais e não são. O Citizen Assist AI responde dúvidas com base em orientações verificadas, mostra a fonte oficial e a data de verificação, avisa que não é um canal oficial e nunca coleta dados pessoais.

## ODS relacionados

- **ODS 16 (Paz, justiça e instituições eficazes):** acesso à informação pública e a serviços de forma transparente.
- **ODS 10 (Redução das desigualdades):** informação simples para quem tem menos acesso a canais de atendimento.
- **ODS 8 (Trabalho decente e crescimento econômico):** apoio ao primeiro emprego e à formalização (Carteira de Trabalho Digital, MEI).

## Como executar

Requisitos: Python 3.8 ou superior. Nenhuma biblioteca externa.

```
python main.py
```

Estrutura do projeto:

```
citizen-assist-ai/
├── README.md
├── main.py                  # menu principal
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento (+ normalizar e merge_sort)
├── assistente.py            # classe Assistente (+ No e ListaEncadeada)
└── data/
    ├── base_conhecimento.json   # 10 orientações, 4 categorias
    ├── historico.json           # atendimentos registrados
    └── atendimentos.csv         # gerado pela opção 4 do menu
```

O menu tem: 1 - fazer uma pergunta, 2 - navegar por categorias, 3 - ver indicadores, 4 - exportar atendimentos (CSV) e 0 - sair (pede uma nota de facilidade de 1 a 5).

## Classes e composição

- `Orientacao`: um registro do JSON (id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em). Valida os dados e exibe a orientação (`exibir()`).
- `BaseConhecimento`: lê o JSON (`carregar()`), lista as categorias (`categorias()`, `por_categoria()`), pontua e busca (`pontuar()`, `buscar()`). Tem o atributo `orientacoes`, uma lista de objetos `Orientacao`.
- `Assistente`: faz o atendimento (`perguntar()`, `navegar()`), guarda o histórico (`registrar()`), calcula os indicadores (`indicadores()`) e exporta o CSV (`exportar_csv()`).

Composição: `Assistente` tem uma `BaseConhecimento` (atributo `base`), que tem uma lista de `Orientacao`.

## Regra de pontuação

A pergunta, as palavras-chave e o título são normalizados (minúsculas, sem acentos, sem pontuação) por `normalizar()`. Cada orientação recebe pontos:

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta com 4 letras ou mais que aparece no título | +1 |

| Melhor orientação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança ALTA |
| 3 a 5 pontos | Confiança MÉDIA |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas (com pelo menos 3 pontos). Mantivemos os pesos e limites sugeridos no enunciado.

Exemplo: em "Como faço o cartão do SUS?", a orientação 7 recebe +3 por "cartao do sus", +3 por "sus" e +1 porque "cartao" está no título: 7 pontos, confiança ALTA.

## Regras de atendimento

- **Navegação por categorias** com "0 para voltar" em todas as telas.
- **Entradas inválidas** (opção fora da faixa, letras, resposta vazia, s/n inválido) nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos ou com @ é recusada e não é registrada.
- **Transparência:** toda resposta mostra a fonte, a data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** JSON da base ou do histórico ausente ou corrompido não trava o programa.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, origem (pergunta ou categoria), pergunta, id da orientação, se encontrou, se ajudou, tentativas e tempo em segundos (medido com `time.time()`). Ao sair, o assistente pede a nota de facilidade (1 a 5), que fica guardada nos atendimentos daquela sessão.

Indicadores exibidos (opção 3): resposta encontrada (%), taxa de acerto: ajudou (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução.

A opção 4 exporta os atendimentos para `data/atendimentos.csv` com `csv.DictWriter`.

## Integração com outras disciplinas

Reaproveitamos conceitos da GS de **Data Structures and Algorithms (DSA)**, mantendo a busca por pontuação como regra principal:

- **Lista encadeada:** o histórico de atendimentos fica em memória em uma lista encadeada própria (classes `No` e `ListaEncadeada`, em `assistente.py`), com inserção no fim em O(1) usando a referência da cauda e percurso por `__iter__`. Ela é gravada em `historico.json` a cada atendimento.
- **Merge Sort:** a ordenação dos resultados da busca (do maior para o menor número de pontos) e das categorias é feita pela função `merge_sort` (em `base_conhecimento.py`), implementada por nós, sem `sorted()` nem `list.sort()`. Ela divide a lista ao meio, ordena cada metade e intercala as duas, com custo O(n log n), e é estável (empates mantêm a ordem original).

## Fontes consultadas

Fontes oficiais usadas em cada orientação (todas conferidas em 16/11/2026; a data de cada conferência está no campo `verificado_em` do JSON):

| Orientação | Fonte oficial |
|---|---|
| 1. Título de eleitor (primeira via) | https://www.tse.jus.br/comunicacao/noticias/2021/Dezembro/veja-o-passo-a-passo-para-tirar-o-primeiro-titulo-pela-internet |
| 2. Segunda via do título e e-Título | https://www.tse.jus.br/comunicacao/noticias/2023/Marco/titulo-de-eleitor-uma-questao-de-cidadania |
| 3. Carteira de Identidade Nacional | https://www.gov.br/identidade |
| 4. CPF | https://gov.br/pt-br/servicos/inscrever-no-cpf |
| 5. Carteira de Trabalho Digital | https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho |
| 6. MEI | https://www.gov.br/pt-br/servicos/realizar-registro-como-microempreendedor-individual-mei |
| 7. Cartão SUS | https://meususdigital.saude.gov.br/ |
| 8. Conta gov.br | https://www.gov.br/gestao/pt-br/assuntos/editoria-2013-defeso-eleitoral/aumente-os-niveis-de-sua-conta-gov-br-para-ter-mais-seguranca-e-acesso-a-todos-os-servicos |
| 9. Alistamento militar | https://alistamento.eb.mil.br |
| 10. CadÚnico | https://cadunico.dataprev.gov.br |

Páginas oficiais e reportagens usadas para conferir detalhes:

- Ministério do Trabalho e Emprego, orientações sobre a Carteira de Trabalho Digital: https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/proteja/arquivos/ctpsdigital-2.pdf
- Governo de Minas Gerais, emissão da CIN: https://www.mg.gov.br/servico/obter-carteira-de-identidade-nacional
- Portal do Empreendedor, perguntas frequentes (limite de faturamento do MEI): https://www.gov.br/empreendedor/perguntas-frequentes
- Secretaria de Saúde da Bahia, Cartão Nacional de Saúde: https://www.saude.ba.gov.br/?p=340
- Agência Brasil (prazo do alistamento militar de 2026), publicada em: https://www.diariodepernambuco.com.br/brasil/2026/06/11717678-prazo-para-o-alistamento-militar-termina-nesta-terca-feira-30.html
- Tecnoblog, níveis da conta gov.br: https://tecnoblog.net/responde/como-aumentar-o-nivel-da-conta-gov/
- Tribuna do Norte, CIN e conta ouro: https://tribunadonorte.com/geral/carteira-de-identidade-nacional-possibilita-ter-conta-ouro-no-govbr-1148977
- Folha de Pernambuco, regras da CIN: https://www.folhape.com.br/noticias/saiba-como-tirar-a-nova-carteira-de-identidade-nacional/382040/
- Concursos no Brasil, regras do CadÚnico: https://concursosnobrasil.com/beneficios-sociais/2022/08/19/quem-pode-obter-inscricao-no-cadunico-veja-regras-atualizadas/

## Resultado do teste com usuários

> Preencher depois do teste: pelo menos 3 pessoas de fora da equipe e 10 atendimentos ou mais. Não registrar nomes nem dados dessas pessoas.

| Indicador | Resultado |
|---|---|
| Pessoas testadas | (preencher) |
| Atendimentos | (preencher) |
| Resposta encontrada (%) | (preencher) |
| Taxa de acerto: ajudou (%) | (preencher) |
| Tempo médio para encontrar | (preencher) |
| Tentativas por atendimento | (preencher) |
| Facilidade de uso (1 a 5) | (preencher) |

Dúvidas sem solução encontradas no teste: (preencher)

Melhoria feita a partir do teste: (preencher, por exemplo: palavra-chave que foi adicionada)

## Limitações

- A base tem apenas 10 orientações; o assistente não responde nada fora dela.
- A busca compara palavras: não entende sinônimos nem corrige erros de digitação (por exemplo, "alistar" só funciona porque foi cadastrada como palavra-chave).
- As informações podem mudar com o tempo (prazos, valores e limites, como o limite de faturamento do MEI, e regras de cada estado, como as da CIN). Por isso cada resposta mostra a data de verificação e o aviso de que o assistente não é um canal oficial.
- O assistente só funciona no terminal, em português.

## Vídeo técnico

Link do vídeo no YouTube (não listado): (preencher)