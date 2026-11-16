"""Classe BaseConhecimento: lê o JSON, lista categorias e busca a melhor orientação.

Integração com DSA (Data Structures and Algorithms): a ordenação dos resultados
da busca e das categorias usa o Merge Sort implementado aqui (merge_sort), em
vez de sorted() ou list.sort().
"""
import json

from orientacao import Orientacao

ACENTOS = {
    "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ç": "c",
}

SINAIS = "?!.,;:()\"'-/"


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação.
    O resultado tem um espaço no começo e outro no fim, para que a busca
    compare palavras inteiras (" sus " não casa com " sustento ")."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def merge_sort(itens, chave=lambda x: x, reverso=False):
    """Merge Sort (estável). Devolve uma lista nova ordenada.
    Divide a lista ao meio, ordena cada metade e intercala as duas.
    Tempo O(n log n)."""
    if len(itens) <= 1:
        return list(itens)

    meio = len(itens) // 2
    esquerda = merge_sort(itens[:meio], chave, reverso)
    direita = merge_sort(itens[meio:], chave, reverso)

    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        a, b = chave(esquerda[i]), chave(direita[j])
        pega_esquerda = (a >= b) if reverso else (a <= b)  # empate: esquerda (estável)
        if pega_esquerda:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


class BaseConhecimento:
    """O conjunto de todas as orientações, carregado de um arquivo JSON."""

    PONTOS_PALAVRA_CHAVE = 3   # palavra-chave da orientação que aparece na pergunta
    PONTOS_TITULO = 1          # palavra da pergunta (4+ letras) que aparece no título
    MIN_LETRAS_TITULO = 4
    LIMITE_ALTA = 6            # melhor orientação com 6 pontos ou mais: confiança ALTA
    LIMITE_MEDIA = 3           # de 3 a 5 pontos: confiança MÉDIA; abaixo de 3: não encontrei

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []   # lista de objetos Orientacao
        self.avisos = []        # registros ignorados ao carregar
        self.erro = ""

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao.
        Retorna True se carregou ao menos uma orientação válida. Arquivo ausente,
        corrompido ou com registros inválidos nunca derruba o programa."""
        self.orientacoes = []
        self.avisos = []
        self.erro = ""

        try:
            with open(self.caminho, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"arquivo da base de conhecimento não encontrado ({self.caminho})"
            return False
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as erro:
            self.erro = f"não foi possível ler a base de conhecimento ({erro})"
            return False

        if not isinstance(dados, list):
            self.erro = "a base de conhecimento deve ser uma lista de dicionários"
            return False

        ids_vistos = set()
        for posicao, item in enumerate(dados, start=1):
            try:
                orientacao = Orientacao.de_dicionario(item)
            except ValueError as erro:
                self.avisos.append(f"registro {posicao}: {erro}")
                continue
            if orientacao.id in ids_vistos:
                self.avisos.append(f"registro {posicao}: id {orientacao.id} repetido")
                continue
            ids_vistos.add(orientacao.id)
            self.orientacoes.append(orientacao)

        if not self.orientacoes:
            self.erro = "nenhuma orientação válida foi encontrada na base de conhecimento"
            return False
        return True

    def categorias(self):
        """Lista de categorias (sem repetir), em ordem alfabética (Merge Sort)."""
        encontradas = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in encontradas:
                encontradas.append(orientacao.categoria)
        return merge_sort(encontradas, chave=normalizar)

    def por_categoria(self, categoria):
        """Orientações de uma categoria, em ordem alfabética de título."""
        daquela = [o for o in self.orientacoes if o.categoria == categoria]
        return merge_sort(daquela, chave=lambda o: normalizar(o.titulo))

    def pontuar(self, pergunta_normalizada, orientacao):
        """Pontos de uma orientação para uma pergunta já normalizada:
        +3 por palavra-chave que aparece na pergunta;
        +1 por palavra da pergunta (4 letras ou mais) que aparece no título."""
        pontos = 0

        palavras_chave = set()
        for palavra_chave in orientacao.palavras_chave:
            normal = normalizar(palavra_chave)
            if normal.strip():
                palavras_chave.add(normal)
        for normal in palavras_chave:
            if normal in pergunta_normalizada:
                pontos += self.PONTOS_PALAVRA_CHAVE

        titulo = normalizar(orientacao.titulo)
        ja_contadas = set()
        for palavra in pergunta_normalizada.split():
            if len(palavra) >= self.MIN_LETRAS_TITULO and palavra not in ja_contadas:
                ja_contadas.add(palavra)
                if f" {palavra} " in titulo:
                    pontos += self.PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a menor
        pontuação. Só entram orientações com pelo menos 1 ponto."""
        normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(normalizada, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        return merge_sort(resultados, chave=lambda tupla: tupla[0], reverso=True)

    @classmethod
    def confianca(cls, pontos):
        """'ALTA' (6+), 'MÉDIA' (3 a 5) ou None (menos de 3: não encontrei)."""
        if pontos >= cls.LIMITE_ALTA:
            return "ALTA"
        if pontos >= cls.LIMITE_MEDIA:
            return "MÉDIA"
        return None