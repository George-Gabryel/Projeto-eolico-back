"""
menu.py  --  ARQUIVO PRINCIPAL DO SISTEMA
==========================================
Roda no terminal/CMD. Faz login com e-mail e senha e mostra os menus
de acordo com o perfil do usuario:

  Gerente     : acesso total ao sistema.
  Funcionario : acesso a tudo, exceto a Visao Geral Financeira (relatorios
                de clientes). Pode ver/criar relatorios, mas nao o painel
                financeiro consolidado de clientes.
  Cliente     : so visualiza ocorrencias, relatorios e dashboards do
                PROPRIO parque. Nao cadastra nada.

Para rodar:  python menu.py
"""

import database as db
import validacao as validar
import funcoes_usuarios as fun_user
import funcoes_parques as fun_parq
import funcoes_turbinas as fun_turb
import funcoes_drones as fun_drone
import funcoes_ocorrencias as fun_oc
import funcoes_relatorios as fun_rel


# ==========================================================
#  PRIMEIRO ACESSO: garante que exista pelo menos 1 gerente
# ==========================================================
def garantir_gerente_inicial():
    gerentes = db.consultar(
        "SELECT email FROM usuarios WHERE tipo_perfil = 'Gerente'")
    if not gerentes:
        print("\n[PRIMEIRO ACESSO] Nenhum gerente cadastrado.")
        print("Vamos criar o gerente administrador do sistema.")
        email = "admin@sistema.com"
        db.executar("""
            INSERT INTO usuarios (email, usuario, telefone, senha, tipo_perfil)
            VALUES (:e, 'Administrador', '81 90000-0000', :s, 'Gerente')
        """, {"e": email, "s": validar.gerar_hash("admin123")})
        print("  Login : admin@sistema.com")
        print("  Senha : admin123")
        print("  (troque a senha depois, no menu de usuarios)\n")


# ==========================================================
#  LOGIN
# ==========================================================
def fazer_login():
    print("\n" + "=" * 45)
    print("   SISTEMA DE GESTAO EOLICA - LOGIN")
    print("=" * 45)

    tentativas = 3
    while tentativas > 0:
        email = input("\nE-mail: ").strip()
        senha = input("Senha: ").strip()

        achou = db.consultar(
            "SELECT * FROM usuarios WHERE email = :e", {"e": email})

        if achou and validar.conferir_senha(senha, achou[0]["senha"]):
            usuario = achou[0]
            print(f"\n[OK] Bem-vindo, {usuario['usuario']} ({usuario['tipo_perfil']})!")
            return usuario

        tentativas -= 1
        print(f"E-mail ou senha incorretos. Tentativas restantes: {tentativas}")

    print("\nNumero de tentativas esgotado.")
    return None


# ==========================================================
#  MENUS POR ASSUNTO (reaproveitados pelos perfis)
# ==========================================================
def menu_usuarios():
    while True:
        print("\n--- USUARIOS ---")
        print("  1 - Cadastrar usuario")
        print("  2 - Visualizar usuarios")
        print("  3 - Alterar nome")
        print("  4 - Alterar telefone")
        print("  5 - Alterar senha")
        print("  6 - Apagar usuario")
        print("  0 - Voltar")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   fun_user.cadastrar_usuario()
        elif op == 2: fun_user.visualizar_usuarios()
        elif op == 3: fun_user.alterar_usuario()
        elif op == 4: fun_user.alterar_telefone()
        elif op == 5: fun_user.alterar_senha()
        elif op == 6: fun_user.apagar_usuario()
        elif op == 0: break
        else: print("Opcao invalida.")


def menu_parques():
    while True:
        print("\n--- PARQUES ---")
        print("  1 - Cadastrar parque")
        print("  2 - Visualizar parques")
        print("  3 - Dashboard de um parque")
        print("  4 - Estatisticas gerais")
        print("  5 - Atualizar producao")
        print("  6 - Atualizar configuracoes")
        print("  7 - Desativar / Remover parque")
        print("  0 - Voltar")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   fun_parq.cadastrar_parque()
        elif op == 2: fun_parq.visualizar_parques()
        elif op == 3: fun_parq.dashboard_parque()
        elif op == 4: fun_parq.estatisticas_parques()
        elif op == 5: fun_parq.atualizar_producao()
        elif op == 6: fun_parq.atualizar_configuracoes()
        elif op == 7: fun_parq.remover_ou_desativar_parque()
        elif op == 0: break
        else: print("Opcao invalida.")


def menu_turbinas():
    while True:
        print("\n--- TURBINAS ---")
        print("  1 - Cadastrar turbina")
        print("  2 - Visualizar turbinas")
        print("  3 - Filtrar por parque")
        print("  4 - Estatisticas")
        print("  5 - Atualizar status")
        print("  6 - Atualizar horas")
        print("  7 - Inativar / Remover turbina")
        print("  0 - Voltar")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   fun_turb.cadastrar_turbina()
        elif op == 2: fun_turb.visualizar_turbinas()
        elif op == 3: fun_turb.visualizar_por_parque()
        elif op == 4: fun_turb.estatisticas_turbinas()
        elif op == 5: fun_turb.atualizar_status()
        elif op == 6: fun_turb.atualizar_horas()
        elif op == 7: fun_turb.inativar_ou_remover_turbina()
        elif op == 0: break
        else: print("Opcao invalida.")


def menu_drones():
    while True:
        print("\n--- DRONES ---")
        print("  1 - Cadastrar drone")
        print("  2 - Visualizar drones")
        print("  3 - Estatisticas")
        print("  4 - Atualizar bateria")
        print("  5 - Alterar limite de voo")
        print("  6 - Aposentar / Remover drone")
        print("  0 - Voltar")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   fun_drone.cadastrar_drone()
        elif op == 2: fun_drone.visualizar_drones()
        elif op == 3: fun_drone.estatisticas_drones()
        elif op == 4: fun_drone.atualizar_bateria()
        elif op == 5: fun_drone.alterar_limite_voo()
        elif op == 6: fun_drone.aposentar_ou_remover_drone()
        elif op == 0: break
        else: print("Opcao invalida.")


def menu_ocorrencias():
    while True:
        print("\n--- OCORRENCIAS ---")
        print("  1 - Registrar ocorrencia")
        print("  2 - Visualizar todas")
        print("  3 - Filtrar por parque")
        print("  4 - Resumo estatistico")
        print("  5 - Reclassificar")
        print("  6 - Corrigir falso-positivo")
        print("  7 - Excluir ocorrencia")
        print("  0 - Voltar")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   fun_oc.registrar_ocorrencia()
        elif op == 2: fun_oc.visualizar_ocorrencias()
        elif op == 3: fun_oc.filtrar_por_parque()
        elif op == 4: fun_oc.resumo_estatisticas()
        elif op == 5: fun_oc.reclassificar_ocorrencia()
        elif op == 6: fun_oc.corrigir_falso_positivo()
        elif op == 7: fun_oc.excluir_ocorrencia()
        elif op == 0: break
        else: print("Opcao invalida.")


def menu_relatorios(mostrar_financeiro=True):
    """
    mostrar_financeiro = False esconde a Visao Geral Financeira.
    Usado para o Funcionario, que nao acessa relatorios financeiros
    consolidados de clientes.
    """
    while True:
        print("\n--- RELATORIOS ---")
        print("  1 - Criar relatorio")
        print("  2 - Visualizar relatorios")
        if mostrar_financeiro:
            print("  3 - Visao geral financeira")
        print("  4 - Atualizar relatorio")
        print("  5 - Arquivar / Excluir relatorio")
        print("  0 - Voltar")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   fun_rel.criar_relatorio()
        elif op == 2: fun_rel.visualizar_relatorios()
        elif op == 3:
            if mostrar_financeiro:
                fun_rel.visao_geral_financeira()
            else:
                print("Acesso negado: relatorios financeiros sao restritos.")
        elif op == 4: fun_rel.atualizar_relatorio()
        elif op == 5: fun_rel.arquivar_ou_excluir_relatorio()
        elif op == 0: break
        else: print("Opcao invalida.")


# ==========================================================
#  PAINEL DO GERENTE  (acesso total)
# ==========================================================
def painel_gerente(usuario):
    while True:
        print("\n" + "=" * 45)
        print(f"   PAINEL DO GERENTE - {usuario['usuario']}")
        print("=" * 45)
        print("  1 - Usuarios")
        print("  2 - Parques")
        print("  3 - Turbinas")
        print("  4 - Drones")
        print("  5 - Ocorrencias")
        print("  6 - Relatorios (com financeiro)")
        print("  0 - Sair (logout)")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   menu_usuarios()
        elif op == 2: menu_parques()
        elif op == 3: menu_turbinas()
        elif op == 4: menu_drones()
        elif op == 5: menu_ocorrencias()
        elif op == 6: menu_relatorios(mostrar_financeiro=True)
        elif op == 0: print("\nLogout efetuado."); break
        else: print("Opcao invalida.")


# ==========================================================
#  PAINEL DO FUNCIONARIO  (tudo, exceto relatorio financeiro)
# ==========================================================
def painel_funcionario(usuario):
    while True:
        print("\n" + "=" * 45)
        print(f"   PAINEL DO FUNCIONARIO - {usuario['usuario']}")
        print("=" * 45)
        print("  1 - Parques")
        print("  2 - Turbinas")
        print("  3 - Drones")
        print("  4 - Ocorrencias")
        print("  5 - Relatorios (sem financeiro de clientes)")
        print("  0 - Sair (logout)")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   menu_parques()
        elif op == 2: menu_turbinas()
        elif op == 3: menu_drones()
        elif op == 4: menu_ocorrencias()
        elif op == 5: menu_relatorios(mostrar_financeiro=False)
        elif op == 0: print("\nLogout efetuado."); break
        else: print("Opcao invalida.")


# ==========================================================
#  PAINEL DO CLIENTE  (so visualiza o proprio parque)
# ==========================================================
def painel_cliente(usuario):
    email = usuario["email"]
    while True:
        print("\n" + "=" * 45)
        print(f"   PAINEL DO CLIENTE - {usuario['usuario']}")
        print("=" * 45)
        print("  1 - Meus parques (visualizar)")
        print("  2 - Dashboard de um parque meu")
        print("  3 - Minhas ocorrencias")
        print("  4 - Meus relatorios")
        print("  0 - Sair (logout)")
        try:
            op = int(input("Escolha: "))
        except ValueError:
            print("Digite um numero valido."); continue
        if op == 1:   fun_parq.visualizar_parques(email_cliente=email)
        elif op == 2: fun_parq.dashboard_parque(email_cliente=email)
        elif op == 3: fun_oc.visualizar_ocorrencias(email_cliente=email)
        elif op == 4: fun_rel.visualizar_relatorios(email_cliente=email)
        elif op == 0: print("\nLogout efetuado."); break
        else: print("Opcao invalida.")


# ==========================================================
#  PROGRAMA PRINCIPAL
# ==========================================================
def main():
    db.criar_tabelas()
    garantir_gerente_inicial()

    print("\n" + "#" * 45)
    print("#  SISTEMA DE GESTAO DE PARQUES EOLICOS")
    print("#" * 45)

    while True:
        usuario = fazer_login()
        if usuario is None:
            print("\nSaindo do sistema...")
            break

        perfil = usuario["tipo_perfil"]
        if perfil == "Gerente":
            painel_gerente(usuario)
        elif perfil == "Funcionario":
            painel_funcionario(usuario)
        elif perfil == "Cliente":
            painel_cliente(usuario)
        else:
            print("Perfil desconhecido. Contate o administrador.")

        # Apos o logout, pergunta se quer entrar com outro usuario
        again = input("\nDeseja entrar com outro usuario? (s/n): ").strip().lower()
        if again != "s":
            print("\nAte mais!")
            break


if __name__ == "__main__":
    main()
