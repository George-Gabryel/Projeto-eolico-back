# Sistema de Gestão de Parques Eólicos

Sistema de linha de comando (CMD/terminal) para gerenciar parques eólicos,
turbinas, drones, ocorrências de dispersão de aves e relatórios.
Possui tela de **login** e **permissões diferentes** por tipo de perfil.

---

## Tecnologias usadas

- **Python 3**
- **SQLAlchemy + SQLite** — persistência dos dados (arquivo `sistema.db`)
- **Pandas** — estatísticas e dashboards
- **hashlib** — guarda as senhas com hash (a senha real nunca fica salva)

Instalar as dependências (uma vez só):

```
pip install sqlalchemy pandas
```

---

## Como rodar

1. Coloque **todos os arquivos `.py` na mesma pasta**.
2. No terminal, dentro dessa pasta, execute:

```
python menu.py
```

3. Na primeira execução o sistema cria sozinho um **gerente administrador**:

```
Login : admin@sistema.com
Senha : admin123
```

> Recomenda-se trocar a senha depois, no menu de Usuários.

O arquivo `sistema.db` é criado automaticamente e guarda os dados entre
as execuções (não se perde ao fechar o programa).

---

## Estrutura dos arquivos

| Arquivo                    | O que faz                                                        |
|----------------------------|------------------------------------------------------------------|
| `menu.py`                  | **Arquivo principal.** Login + menus de cada perfil.             |
| `database.py`              | Conexão com o SQLite e criação das tabelas.                      |
| `validacao.py`             | Validação de e-mail/telefone e hash de senha.                    |
| `funcoes_usuarios.py`      | CRUD de usuários.                                                |
| `funcoes_parques.py`       | CRUD de parques (cada parque é vinculado a um cliente).          |
| `funcoes_turbinas.py`      | CRUD de turbinas (vinculadas a um parque).                       |
| `funcoes_drones.py`        | CRUD de drones (vinculados a um parque).                         |
| `funcoes_ocorrencias.py`   | CRUD de ocorrências de dispersão (vinculadas a um parque).       |
| `funcoes_relatorios.py`    | CRUD de relatórios/dashboards (vinculados a um parque).          |

---

## Perfis e permissões

O controle de acesso é feito no `menu.py`: cada perfil enxerga apenas
as funções que tem direito de usar.

### Gerente — acesso total
Pode usar tudo: usuários, parques, turbinas, drones, ocorrências e
relatórios (incluindo a **visão geral financeira**).

### Funcionário — acesso a tudo, exceto relatório financeiro de clientes
Pode gerenciar parques, turbinas, drones, ocorrências e relatórios.
A opção **"Visão geral financeira"** não aparece no menu dele e é
bloqueada mesmo se o número for digitado manualmente.

### Cliente — apenas visualização do próprio parque
Só consegue **visualizar** (não cadastra nada):
- seus parques;
- o dashboard de um parque seu;
- as ocorrências do(s) parque(s) dele;
- os relatórios do(s) parque(s) dele.

O cliente nunca vê dados de parques de outros clientes.

---

## Vínculo Cliente ↔ Parque

Ao cadastrar um parque, o sistema mostra a lista de clientes já
cadastrados e exige escolher o **e-mail do cliente dono**. Como turbinas,
drones, ocorrências e relatórios são todos ligados a um parque, o cliente
acaba enxergando somente o que pertence ao parque dele.

Por isso, a ordem recomendada de cadastro é:

1. Gerente cadastra um **usuário Cliente**.
2. Gerente cadastra um **Parque** e vincula a esse cliente.
3. Gerente/Funcionário cadastra **turbinas, drones, ocorrências e relatórios**
   apontando para o ID daquele parque.

---

## Observação técnica

As permissões são controladas no menu (cada perfil só acessa as funções
liberadas). Em um sistema profissional, a permissão também seria checada
dentro de cada função, mas isso foge do escopo deste projeto.
