"""
CADASTRO E LOGIN SEGURO - VERSÃO SIMPLES
Segurança da Informação - Entrega 2

Como executar:   python cadastro_simples.py
Não precisa instalar nada (só Python 3.9+).

A IDEIA EM 3 PASSOS
  1. Cadastro: a senha NUNCA é salva. Salvamos só o "hash" dela.
  2. Login:    calculamos o hash da senha digitada e comparamos com o salvo.
  3. Se o banco vazar, o atacante vê só hashes, não as senhas.
"""
import hashlib      # contém o scrypt (função de hash feita para senhas)
import hmac         # contém a comparação segura
import os           # os.urandom gera números aleatórios seguros (para o salt)
import sqlite3      # banco de dados simples (vira um arquivo)
from getpass import getpass   # lê a senha sem mostrar na tela

ARQUIVO_BANCO = "usuarios.db"


# ----------------------------------------------------------------------------
# 1) BANCO DE DADOS: uma tabela com usuário, salt e hash (nunca a senha)
# ----------------------------------------------------------------------------
banco = sqlite3.connect(ARQUIVO_BANCO)
banco.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
        salt    BLOB NOT NULL,
        hash    BLOB NOT NULL
    )
""")


# ----------------------------------------------------------------------------
# 2) FUNÇÃO DE HASH (scrypt)
# ----------------------------------------------------------------------------
def gerar_hash(senha, salt):
    """
    Transforma a senha em um hash usando scrypt.
    - salt: texto aleatório misturado à senha (cada usuário tem o seu).
    - n=2**14, r=8, p=1: deixam o cálculo lento e pesado de propósito,
      o que atrapalha quem tenta adivinhar senhas em massa.
    """
    return hashlib.scrypt(senha.encode(), salt=salt, n=2**14, r=8, p=1)


# ----------------------------------------------------------------------------
# 3) CADASTRO
# ----------------------------------------------------------------------------
def cadastrar(usuario, senha):
    if len(usuario) < 3:
        return "Usuário muito curto (mínimo 3 letras)."
    if len(senha) < 8:
        return "Senha muito curta (mínimo 8 caracteres)."

    salt = os.urandom(16)               # salt novo e aleatório para este usuário
    hash_senha = gerar_hash(senha, salt)

    try:
        banco.execute("INSERT INTO usuarios VALUES (?, ?, ?)",
                      (usuario, salt, hash_senha))   # os "?" evitam SQL Injection
        banco.commit()
    except sqlite3.IntegrityError:
        return "Esse usuário já existe."
    return "Cadastro realizado! (a senha NÃO foi salva, só o hash)"


# ----------------------------------------------------------------------------
# 4) LOGIN
# ----------------------------------------------------------------------------
def entrar(usuario, senha):
    linha = banco.execute("SELECT salt, hash FROM usuarios WHERE usuario = ?",
                          (usuario,)).fetchone()

    # Mesma mensagem de erro para "usuário não existe" e "senha errada",
    # assim o atacante não descobre quais usuários existem.
    if linha is None:
        return "Usuário ou senha inválidos."

    salt, hash_salvo = linha
    hash_digitado = gerar_hash(senha, salt)   # refaz o hash com o MESMO salt

    # compare_digest compara em tempo constante (evita ataques de tempo)
    if hmac.compare_digest(hash_digitado, hash_salvo):
        return "Login realizado com sucesso!"
    return "Usuário ou senha inválidos."


# ----------------------------------------------------------------------------
# 4.1) USUÁRIO GUARDADO: pega o último cadastrado direto do banco
# ----------------------------------------------------------------------------
def ultimo_usuario():
    """Devolve o último usuário cadastrado (ou None). Fica salvo no banco,
    então continua valendo mesmo depois de fechar e abrir o programa."""
    linha = banco.execute(
        "SELECT usuario FROM usuarios ORDER BY rowid DESC LIMIT 1").fetchone()
    return linha[0] if linha else None


# ----------------------------------------------------------------------------
# 5) EXTRAS PARA ILUSTRAR
# ----------------------------------------------------------------------------
def mostrar_banco():
    """Mostra o que realmente está guardado: repare que não existe senha."""
    print("\n--- CONTEÚDO DO BANCO ---")
    linhas = banco.execute("SELECT usuario, salt, hash FROM usuarios").fetchall()
    if not linhas:
        print("(vazio)")
    for usuario, salt, hash_salvo in linhas:
        print(f"usuário: {usuario}")
        print(f"  salt: {salt.hex()}")
        print(f"  hash: {hash_salvo.hex()}")


def comparar_sha256():
    """Mostra por que SHA-256 puro não é bom para senhas."""
    senha = "senha12345"
    print("\n--- SHA-256 PURO (ruim para senhas) ---")
    print("Mesma senha, duas vezes -> resultado IGUAL (sem salt):")
    print(" ", hashlib.sha256(senha.encode()).hexdigest())
    print(" ", hashlib.sha256(senha.encode()).hexdigest())
    print("\n--- SCRYPT COM SALT (bom para senhas) ---")
    print("Mesma senha, duas vezes -> resultados DIFERENTES (salt aleatório):")
    print(" ", gerar_hash(senha, os.urandom(16)).hex())
    print(" ", gerar_hash(senha, os.urandom(16)).hex())
    print("\nAlém disso, o SHA-256 é muito rápido (atacante testa bilhões de")
    print("senhas por segundo). O scrypt é lento de propósito.")


# ----------------------------------------------------------------------------
# 6) MENU
# ----------------------------------------------------------------------------
def menu():
    while True:
        print("\n=== MENU ===")
        print("1 - Cadastrar")
        print("2 - Login")
        print("3 - Ver o que está salvo no banco")
        print("4 - Por que não usar SHA-256 puro?")
        print("0 - Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            usuario = input("Usuário: ").strip().lower()
            senha = getpass("Senha (não aparece na tela): ")
            print(cadastrar(usuario, senha))
        elif opcao == "2":
            guardado = ultimo_usuario()
            if guardado:
                # Basta apertar ENTER para testar o usuário que acabou de criar
                usuario = input(f"Usuário [ENTER = {guardado}]: ").strip().lower() or guardado
            else:
                usuario = input("Usuário: ").strip().lower()
            senha = getpass("Senha: ")
            print(entrar(usuario, senha))
        elif opcao == "3":
            mostrar_banco()
        elif opcao == "4":
            comparar_sha256()
        elif opcao == "0":
            break


if __name__ == "__main__":
    menu()
