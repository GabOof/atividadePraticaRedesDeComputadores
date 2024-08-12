# Redes de Computadores - Atividade Prática 1

### Objetivo

Desenvolver uma solução utilizando `multithreading` em um código projetado para o estudo de `sockets`, permitindo a conexão de múltiplos clientes simultaneamente.

### Tarefa

- Implementar um servidor que aceite conexões de múltiplos clientes.
- Utilizar `threads` para gerenciar as conexões paralelas dos clientes.

---

# Redes de Computadores - Atividade Prática 2

### Requisitos

- Implementar 3 processos no mínimo:
  - 1 servidor
  - 2 clientes

### Funcionalidade

- **Servidor:** Deve gerenciar as conexões e as mensagens entre os clientes.
- **Clientes:**
  - Cliente A pode enviar mensagens ao Cliente B através do servidor.
  - Cliente B deve solicitar ao servidor, periodicamente, suas mensagens pendentes.

### Implementação

Dentro da `thread` do servidor:

- Implementar a lógica para permitir dois tipos de ações:
  - Enviar mensagens
  - Listar mensagens

---

# Redes de Computadores - Atividade Prática 3

### Requisitos

- O servidor deve administrar os clientes e saber onde eles estão (pelo IP), sem armazenar as mensagens.
- Os clientes verificam se já entraram em contato com o destinatário antes de enviar uma mensagem.
  - Caso contrário, devem solicitar ao servidor a localização do destinatário.
- Periodicamente, o servidor verifica os IPs e portas dos clientes conectados.

### Funcionalidade

- **Clientes:**

  - Devem ter threads separadas para armazenar mensagens e para a comunicação (menu).
  - O menu permite a comunicação direta entre clientes sem a intervenção do servidor.
  - O cliente transforma o nome do destinatário em um hash para ser usado como identificador.
  - O IP dos clientes é coletado e utilizado na comunicação.

- **Servidor:**
  - Serve apenas para a passagem e coleta das informações dos clientes conectados.
  - Verifica se o campo destinatário foi preenchido:
    - Se não preenchido, envia a mensagem para todos os clientes conectados.
    - Se preenchido, envia apenas para o destinatário específico.
