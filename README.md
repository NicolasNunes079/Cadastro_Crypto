# Cadastro e login seguro — Entrega 2

Projeto Integrador de Segurança da Informação do curso de Análise e Desenvolvimento de Sistemas da Universidade Tiradentes (UNIT).

**Autores** — Arthur Santiago, Nicolas Nunes e Victor Alexandre Brito.  
**Docente** — Profª. Ana Carla do Nascimento Santos.

## Problema e objetivo

Uma aplicação precisa cadastrar usuários e autenticar seu acesso sem gravar senhas em texto puro. Este protótipo usa scrypt, salt aleatório por cadastro e comparação segura dos hashes. O menu permite demonstrar cadastro, login correto, login incorreto e armazenamento protegido.

## Arquivos

| Arquivo | Finalidade |
| --- | --- |
| `cadastro_simples (1).py` | Aplicação de terminal com cadastro e login |
| `usuarios.db` | Banco SQLite criado automaticamente pelo programa |
| `Entrega2_Documentacao_ABNT_CadastroSimples.docx` | Documentação técnica e acadêmica |
| `Evidencias.mp4` | Arquivo de vídeo fornecido com o projeto |

## Requisitos e execução

Use Python 3.9 ou superior com suporte a `hashlib.scrypt` e `sqlite3`. O código utiliza somente módulos da biblioteca padrão, sem instalação de pacotes externos.

Abra o terminal na pasta do projeto e execute o nome exato do arquivo, entre aspas por conter espaços e parênteses.

```powershell
python -X utf8 "cadastro_simples (1).py"
```

O banco `usuarios.db` é aberto ou criado no diretório de trabalho do terminal. Execute sempre a partir da mesma pasta para utilizar o mesmo banco.

A senha é solicitada por `getpass` e fica oculta em terminais compatíveis. Digite-a e pressione Enter, mesmo que nenhum caractere apareça.

## Como usar

| Opção | Ação |
| --- | --- |
| 1 | Cadastrar um usuário |
| 2 | Fazer login |
| 3 | Exibir usuários, salts e hashes armazenados |
| 4 | Demonstrar SHA-256 puro e scrypt com salts diferentes |
| 0 | Encerrar o programa |

O usuário precisa ter pelo menos 3 caracteres e a senha, pelo menos 8 caracteres. Pelo menu, o nome de usuário é convertido para minúsculas e tem os espaços das extremidades removidos. A senha preserva os caracteres digitados.

No login, pressionar Enter no campo de usuário seleciona o último cadastrado. Esse nome continua disponível após reiniciar o programa porque é consultado no banco.

## Algoritmos e parâmetros

| Componente | Configuração no código |
| --- | --- |
| Derivação de senha | `hashlib.scrypt` |
| Custo | `n=2**14`, `r=8`, `p=1` |
| Salt | 16 bytes gerados por `os.urandom(16)` em cada cadastro |
| Hash derivado | 64 bytes, tamanho padrão de `hashlib.scrypt` |
| Comparação | `hmac.compare_digest` |
| Persistência | SQLite com usuário, salt e hash |
| Consultas SQL | Parâmetros `?` para os valores informados |
| Leitura da senha | `getpass.getpass` |

No cadastro, o programa valida os tamanhos mínimos, gera o salt, deriva o hash da senha e grava usuário, salt e hash. O salt é público e pode ser armazenado junto ao hash. Usuários repetidos são recusados pela chave primária da tabela.

No login, o programa busca o salt e o hash do usuário, deriva novamente o hash da senha informada e compara os resultados com `hmac.compare_digest`. A comparação reduz vazamentos de temporização na comparação dos hashes. Usuário inexistente e senha incorreta recebem a mesma mensagem.

A senha permanece temporariamente na memória durante o processamento. O código grava no banco apenas o salt e o hash associado ao usuário.

## Por que SHA-256 isolado é inadequado para senhas

SHA-256 é uma função rápida de hash. Essa rapidez facilita testar muitas senhas candidatas quando um banco vaza. Sem salt, senhas iguais também produzem hashes iguais.

O scrypt acrescenta custo de processamento e de memória, tornando cada tentativa mais cara. O salt aleatório dificulta o reaproveitamento de cálculos entre usuários e o uso de tabelas pré-computadas. Mesmo com essas proteções, senhas fracas podem ser descobertas por tentativas.

A opção 4 ilustra que SHA-256 sem salt repete o resultado para uma mesma senha, enquanto scrypt com salts diferentes produz resultados diferentes. A demonstração exibe hashes e não mede a velocidade dos algoritmos.

## Roteiro de testes

Use dados fictícios e um nome de usuário ainda não cadastrado. A tabela apresenta os resultados esperados para reprodução pelo menu.

| Teste | Entrada ou ação | Resultado esperado |
| --- | --- | --- |
| Usuário curto | Cadastrar `ab` com senha de 8 ou mais caracteres | Cadastro recusado |
| Senha curta | Cadastrar `aluno_teste` com `curta` | Cadastro recusado |
| Cadastro válido | Cadastrar `aluno_teste` com `SenhaTeste123` | Cadastro realizado |
| Usuário duplicado | Repetir o cadastro válido | Usuário já existe |
| Login correto | Informar `aluno_teste` e `SenhaTeste123` | Login realizado com sucesso |
| Login incorreto | Informar `aluno_teste` e outra senha | Usuário ou senha inválidos |
| Usuário inexistente | Informar um nome ausente do banco | Mesma mensagem de credenciais inválidas |
| Persistência | Encerrar, reabrir e fazer login | Cadastro permanece disponível |
| Armazenamento | Selecionar a opção 3 | Usuário, salt e hash são exibidos |
| Comparação de hashes | Selecionar a opção 4 | SHA-256 repetido e hashes scrypt diferentes |

A documentação em Word inclui uma relação de testes e saídas de execução. Registre a reprodução com capturas de tela ou vídeo para compor as evidências da entrega.

## Riscos e limitações

- Os parâmetros de scrypt são fixos e didáticos. O programa não registra sua versão por usuário nem faz atualização automática dos hashes.
- Não há limite de tentativas de login, autenticação multifator, recuperação de senha ou verificação de senhas vazadas.
- A mensagem genérica de login reduz a exposição de informações, mas o fluxo de usuário inexistente termina antes do cálculo de scrypt e pode ter tempo de resposta diferente.
- A opção 3 expõe salts e hashes no terminal para demonstração. Um vazamento desses dados permite tentativas offline de adivinhar senhas.
- O arquivo SQLite depende das permissões de acesso do sistema operacional. O código não cifra o banco.
- A aplicação é local e não implementa sessões nem comunicação de rede.
- O projeto usa bibliotecas prontas para as operações criptográficas.

## Referências e documentação de apoio

- `Entrega2_Documentacao_ABNT_CadastroSimples.docx`, fornecido com o projeto.
- Python Software Foundation — documentação de `hashlib`, `hmac`, `sqlite3` e `getpass`.
- RFC 7914 — The scrypt Password-Based Key Derivation Function.
- OWASP — Password Storage Cheat Sheet.

