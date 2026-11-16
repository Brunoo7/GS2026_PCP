"""Classe Orientacao: uma informação da base de conhecimento (um registro do JSON)."""
import textwrap
from datetime import datetime

AVISO = "este assistente NÃO é um canal oficial."


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    CAMPOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
              "documentos", "onde", "fonte", "verificado_em")

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Cria uma Orientacao a partir de um dicionário do JSON.
        Levanta ValueError (com mensagem clara) se o registro for inválido."""
        if not isinstance(dados, dict):
            raise ValueError("o registro não é um dicionário")

        faltando = [c for c in cls.CAMPOS if c not in dados]
        if faltando:
            raise ValueError("campos ausentes: " + ", ".join(faltando))

        if not isinstance(dados["id"], int) or isinstance(dados["id"], bool):
            raise ValueError("o campo id deve ser um número inteiro")

        for campo in ("categoria", "titulo", "resposta", "onde", "fonte"):
            if not isinstance(dados[campo], str) or not dados[campo].strip():
                raise ValueError(f"o campo {campo} deve ser um texto não vazio")

        for campo in ("palavras_chave", "documentos"):
            valor = dados[campo]
            if not isinstance(valor, list) or not all(isinstance(x, str) for x in valor):
                raise ValueError(f"o campo {campo} deve ser uma lista de textos")

        if len([p for p in dados["palavras_chave"] if p.strip()]) < 3:
            raise ValueError("cada orientação precisa de pelo menos 3 palavras-chave")

        try:
            datetime.strptime(dados["verificado_em"], "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError("verificado_em deve estar no formato AAAA-MM-DD")

        return cls(**{campo: dados[campo] for campo in cls.CAMPOS})

    def exibir(self):
        """Mostra a orientação na tela: resposta, documentos, onde, fonte e aviso."""
        print(f">> {self.titulo}  [{self.categoria}]")
        print(textwrap.fill(self.resposta, width=78))
        print("Documentos necessários:")
        if self.documentos:
            for documento in self.documentos:
                print(textwrap.fill(f"- {documento}", width=76,
                                    initial_indent="  ", subsequent_indent="    "))
        else:
            print("  - (nenhum documento específico)")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {AVISO}")