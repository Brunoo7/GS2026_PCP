"""Classe Assistente: faz o atendimento, guarda o histórico e calcula os indicadores.

Integração com DSA (Data Structures and Algorithms): o histórico de atendimentos
é mantido em memória em uma lista encadeada implementada aqui (No e
ListaEncadeada), em vez de uma list do Python.
"""
import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import BaseConhecimento


# ---------------------------------------------------------------------------
# Lista encadeada (DSA)
# ---------------------------------------------------------------------------
class No:
    """Nó da lista: guarda um dado e a referência ao próximo nó."""

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class ListaEncadeada:
    """Lista encadeada simples com referências de cabeça e cauda."""

    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.tamanho = 0

    def inserir_fim(self, dado):
        """Insere no fim em O(1), usando a referência da cauda."""
        novo = No(dado)
        if self.cabeca is None:
            self.cabeca = novo
            self.cauda = novo
        else:
            self.cauda.proximo = novo
            self.cauda = novo
        self.tamanho += 1

    def __iter__(self):
        """Percorre a lista da cabeça até a cauda."""
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def __len__(self):
        return self.tamanho


# ---------------------------------------------------------------------------
# Assistente
# ---------------------------------------------------------------------------
class Assistente:
    """Quem conversa com o cidadão."""

    CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
                  "ajudou", "tentativas", "tempo_segundos", "nota_facilidade"]
    CAMPOS_HISTORICO = ("data", "origem", "pergunta", "id_orientacao",
                        "encontrou", "ajudou", "tentativas", "tempo_segundos")

    def __init__(self, nome, base, pasta_dados=None):
        self.nome = nome
        self.base = base
        self.historico = ListaEncadeada()   # atendimentos (dicionários)
        if pasta_dados is None:
            pasta_dados = os.path.dirname(os.path.abspath(base.caminho))
        self.caminho_historico = os.path.join(pasta_dados, "historico.json")
        self.caminho_csv = os.path.join(pasta_dados, "atendimentos.csv")
        self.sessao = datetime.now().isoformat(timespec="seconds")
        self._carregar_historico()

    # -- entrada de dados com validação -------------------------------------
    @staticmethod
    def ler_sim_nao(mensagem):
        """Repete até o usuário digitar s ou n. Entrada inválida nunca encerra."""
        while True:
            resposta = input(mensagem).strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("Resposta inválida. Digite s para sim ou n para não.")

    @staticmethod
    def ler_numero(mensagem, maximo):
        """Lê um número de 0 até 'maximo'. Retorna None se a entrada for inválida."""
        texto = input(mensagem).strip()
        if not texto.isdigit() or int(texto) > maximo:
            print(f"Opção inválida. Digite um número de 0 a {maximo}.")
            return None
        return int(texto)

    @staticmethod
    def contem_dado_pessoal(texto):
        """Pergunta com 8 ou mais dígitos ou com @ é recusada (CPF, telefone, e-mail)."""
        digitos = sum(1 for letra in texto if letra.isdigit())
        return "@" in texto or digitos >= 8

    # -- atendimento por pergunta -------------------------------------------
    def perguntar(self):
        """Atendimento por texto livre. Continua até a pessoa resolver a dúvida
        ou digitar 0 para voltar. Cada atendimento é registrado no histórico."""
        if not self.base.orientacoes:
            print("A base de conhecimento está vazia. Não é possível responder agora.")
            return

        inicio = time.time()
        tentativas = 0
        ultima = {"pergunta": "", "id": None, "encontrou": False}

        while True:
            texto = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if texto == "0":
                break
            if not texto:
                print("Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if self.contem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            resultados = self.base.buscar(texto)
            melhor_pontos = resultados[0][0] if resultados else 0
            confianca = BaseConhecimento.confianca(melhor_pontos)

            if confianca is None:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (por exemplo, o nome do documento ou do "
                      "serviço) ou navegue pelas categorias.")
                print("Categorias:", ", ".join(self.base.categorias()))
                ultima = {"pergunta": texto, "id": None, "encontrou": False}
                continue

            melhor = resultados[0][1]
            print(f"\nConfiança da resposta: {confianca} ({melhor_pontos} pontos)\n")
            melhor.exibir()

            alternativas = [o for p, o in resultados[1:3]
                            if p >= BaseConhecimento.LIMITE_MEDIA]
            if alternativas:
                print("\nOutras orientações parecidas:")
                for outra in alternativas:
                    print(f"  - {outra.titulo} [{outra.categoria}]")

            ultima = {"pergunta": texto, "id": melhor.id, "encontrou": True}
            ajudou = self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if ajudou:
                self.registrar("pergunta", texto, melhor.id, True, True,
                               tentativas, time.time() - inicio)
                return
            print("Tudo bem. Tente reescrever a dúvida com outras palavras.")

        if tentativas > 0:   # saiu sem resolver
            self.registrar("pergunta", ultima["pergunta"], ultima["id"],
                           ultima["encontrou"], False, tentativas, time.time() - inicio)

    # -- atendimento por categorias -----------------------------------------
    def navegar(self):
        """Navegação por categorias, com 0 para voltar em todas as telas."""
        if not self.base.orientacoes:
            print("A base de conhecimento está vazia. Não é possível navegar agora.")
            return

        categorias = self.base.categorias()
        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero} - {categoria}")
            print("  0 - Voltar")
            escolha = self.ler_numero("Escolha uma categoria: ", len(categorias))
            if escolha is None:
                continue
            if escolha == 0:
                return
            self._navegar_categoria(categorias[escolha - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        inicio = time.time()
        tentativas = 0
        ultima = None

        while True:
            print(f"\n{categoria}:")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero} - {orientacao.titulo}")
            print("  0 - Voltar")
            escolha = self.ler_numero("Escolha uma orientação: ", len(orientacoes))
            if escolha is None:
                continue
            if escolha == 0:
                break

            escolhida = orientacoes[escolha - 1]
            tentativas += 1
            print()
            escolhida.exibir()
            ultima = escolhida
            if self.ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                self.registrar("categoria", f"[navegação] {categoria}", escolhida.id,
                               True, True, tentativas, time.time() - inicio)
                return

        if tentativas > 0:   # saiu sem resolver
            self.registrar("categoria", f"[navegação] {categoria}", ultima.id,
                           True, False, tentativas, time.time() - inicio)

    # -- histórico ----------------------------------------------------------
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        """Guarda o atendimento na lista encadeada e salva em historico.json."""
        atendimento = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "origem": origem,                       # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(tempo, 1),
            "sessao": self.sessao,
            "nota_facilidade": None,
        }
        self.historico.inserir_fim(atendimento)
        self._salvar_historico()

    def _salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(list(self.historico), arquivo, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"Aviso: não foi possível salvar o histórico ({erro}).")

    def _carregar_historico(self):
        """Lê historico.json. Arquivo ausente ou corrompido não trava o programa."""
        try:
            with open(self.caminho_historico, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            print("Aviso: o arquivo de histórico está corrompido. Um novo histórico será iniciado.")
            try:
                os.replace(self.caminho_historico, self.caminho_historico + ".corrompido")
            except OSError:
                pass
            return

        if not isinstance(dados, list):
            return
        for item in dados:
            if isinstance(item, dict) and all(c in item for c in self.CAMPOS_HISTORICO):
                item.setdefault("sessao", "")
                item.setdefault("nota_facilidade", None)
                self.historico.inserir_fim(item)

    # -- indicadores --------------------------------------------------------
    def indicadores(self):
        """Calcula e exibe os indicadores. Retorna um dicionário com os valores."""
        registros = list(self.historico)
        total = len(registros)
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return None

        encontrados = [r for r in registros if r["encontrou"]]
        ajudaram = [r for r in registros if r["ajudou"]]

        pct_encontrada = 100 * len(encontrados) / total
        pct_ajudou = 100 * len(ajudaram) / total
        tempo_medio = (sum(r["tempo_segundos"] for r in encontrados) / len(encontrados)
                       if encontrados else None)
        tentativas_medias = sum(r["tentativas"] for r in registros) / total

        notas = {}   # uma nota por sessão de uso
        for r in registros:
            if r.get("nota_facilidade") is not None:
                notas[r["sessao"]] = r["nota_facilidade"]
        facilidade = sum(notas.values()) / len(notas) if notas else None

        sem_solucao = []
        for r in registros:
            if not r["ajudou"] and r["pergunta"] not in sem_solucao:
                sem_solucao.append(r["pergunta"])

        print(f"\n=== Indicadores ({total} atendimento(s)) ===")
        print(f"Resposta encontrada (%)      : {pct_encontrada:.1f}")
        print(f"Taxa de acerto: ajudou (%)   : {pct_ajudou:.1f}")
        if tempo_medio is None:
            print("Tempo médio para encontrar   : sem dados")
        else:
            print(f"Tempo médio para encontrar   : {tempo_medio:.1f} s")
        print(f"Tentativas por atendimento   : {tentativas_medias:.1f}")
        if facilidade is None:
            print("Facilidade de uso (1 a 5)    : sem notas ainda")
        else:
            print(f"Facilidade de uso (1 a 5)    : {facilidade:.1f}")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  (nenhuma)")

        return {
            "total": total,
            "encontrada_pct": pct_encontrada,
            "ajudou_pct": pct_ajudou,
            "tempo_medio": tempo_medio,
            "tentativas_medias": tentativas_medias,
            "facilidade": facilidade,
            "sem_solucao": sem_solucao,
        }

    # -- exportação ---------------------------------------------------------
    def exportar_csv(self):
        """Exporta os atendimentos para atendimentos.csv com csv.DictWriter."""
        if len(self.historico) == 0:
            print("Não há atendimentos para exportar.")
            return False

        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=self.CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                for r in self.historico:
                    linha = dict(r)
                    linha["encontrou"] = "sim" if r["encontrou"] else "nao"
                    linha["ajudou"] = "sim" if r["ajudou"] else "nao"
                    linha["id_orientacao"] = "" if r["id_orientacao"] is None else r["id_orientacao"]
                    linha["nota_facilidade"] = "" if r.get("nota_facilidade") is None else r["nota_facilidade"]
                    escritor.writerow(linha)
        except OSError as erro:
            print(f"Aviso: não foi possível exportar o CSV ({erro}).")
            return False

        print(f"{len(self.historico)} atendimento(s) exportado(s) para {self.caminho_csv}")
        return True

    # -- encerramento -------------------------------------------------------
    def pedir_nota(self):
        """Ao sair, pede uma nota de facilidade de 1 a 5 (se houve atendimento
        nesta sessão) e guarda a nota nos atendimentos da sessão."""
        da_sessao = [r for r in self.historico if r["sessao"] == self.sessao]
        if not da_sessao:
            return
        while True:
            texto = input("\nDe 1 a 5, quão fácil foi usar o assistente? ").strip()
            if texto in ("1", "2", "3", "4", "5"):
                break
            print("Nota inválida. Digite um número de 1 a 5.")
        for r in da_sessao:
            r["nota_facilidade"] = int(texto)
        self._salvar_historico()