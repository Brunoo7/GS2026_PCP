"""Citizen Assist AI - Assistente Digital de Orientação ao Cidadão.

Executar:  python main.py
"""
import os
import sys

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def exibir_menu():
    print("\n=== CITIZEN ASSIST AI ===")
    print("1 - Fazer uma pergunta")
    print("2 - Navegar por categorias")
    print("3 - Ver indicadores")
    print("4 - Exportar atendimentos (CSV)")
    print("0 - Sair")


def main():
    # garante acentos corretos no terminal
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    pasta = os.path.dirname(os.path.abspath(__file__))
    base = BaseConhecimento(os.path.join(pasta, "data", "base_conhecimento.json"))
    if not base.carregar():
        print(f"Atenção: {base.erro}.")
        print("O assistente não conseguirá responder até a base ser corrigida.")
    for aviso in base.avisos:
        print(f"Aviso: orientação ignorada ({aviso}).")

    assistente = Assistente("Citizen Assist AI", base)

    print(f"\nBem-vindo ao {assistente.nome}!")
    print("Este assistente NÃO é um canal oficial. Nunca digite CPF, telefone ou e-mail.")

    try:
        while True:
            exibir_menu()
            opcao = input("Opção: ").strip()
            if opcao == "1":
                assistente.perguntar()
            elif opcao == "2":
                assistente.navegar()
            elif opcao == "3":
                assistente.indicadores()
            elif opcao == "4":
                assistente.exportar_csv()
            elif opcao == "0":
                assistente.pedir_nota()
                print("Obrigado por usar o Citizen Assist AI. Até logo!")
                break
            else:
                print("Opção inválida. Digite um número de 0 a 4.")
    except (EOFError, KeyboardInterrupt):
        print("\nEncerrando o assistente.")


if __name__ == "__main__":
    main()