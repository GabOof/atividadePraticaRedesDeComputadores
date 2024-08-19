import socket  # Importa o módulo para operações de rede usando sockets
import threading  # Importa o módulo para criar e gerenciar threads
from datetime import (
    datetime,
)  # Importa a classe datetime para manipulação de datas e horas
import hashlib  # Importa o módulo para criar hashes de strings
from typing import Dict, Tuple  # Importa tipos para anotações

# Dicionário para armazenar mensagens recebidas por remetente
mensagens: Dict[str, list[str]] = {}
# Dicionário para armazenar destinatários contatados com seu IP e porta
destinatarios_contatados: Dict[str, Tuple[str, int]] = {}


# Função para exibir o menu de opções para o usuário
def exibir_menu() -> str:
    print(f"\n{'='*80}")
    print("Escolha uma ação:")
    print("1. Enviar mensagem")
    print("2. Listar mensagens")
    print("3. Sair")
    print(f"{'='*80}\n")
    escolha = input("Digite o número da ação desejada: ")  # Recebe a escolha do usuário
    return escolha


# Função para enviar uma mensagem para um destinatário ou para todos
def enviar_mensagem(soquete: socket.socket, nome_cliente: str):
    nome_destinatario = input(
        "\nDigite o nome do destinatário: "
    )  # Recebe o nome do destinatário
    conteudo = input("\nDigite a mensagem: ")  # Recebe o conteúdo da mensagem

    if nome_destinatario == "":  # Se o nome do destinatário estiver vazio
        soquete.send(
            f"BROADCAST {conteudo}".encode("utf-8")
        )  # Envia a mensagem para todos
        print(f"\n{'-'*40}")
        print("Mensagem enviada para todos")
        print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*40}\n")
        return

    destinatario_hash = hashlib.sha256(
        nome_destinatario.encode()
    ).hexdigest()  # Gera hash do destinatário

    # Verifica se o destinatário já foi contatado e se seu IP e porta estão armazenados
    if destinatario_hash in destinatarios_contatados:
        ip, porta = destinatarios_contatados[destinatario_hash]
    else:
        # Se o destinatário não está no dicionário, solicita localização ao servidor
        soquete.send(f"LOCATE {nome_destinatario}".encode("utf-8"))
        resposta = soquete.recv(1024).decode("utf-8")  # Recebe a resposta do servidor

        if resposta == "Destinatário não encontrado":
            print(resposta)  # Exibe mensagem se destinatário não for encontrado
            return

        try:
            ip, porta = resposta.split()  # Divide a resposta em IP e porta
            porta = int(porta)  # Converte a porta para inteiro
            destinatarios_contatados[destinatario_hash] = (
                ip,
                porta,
            )  # Armazena IP e porta
        except ValueError:
            print(
                "Resposta inválida do servidor."
            )  # Exibe mensagem de erro se a resposta estiver incorreta
            return

    # Tenta enviar a mensagem para o destinatário usando um novo socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soquete_destinatario:
            soquete_destinatario.connect(
                (ip, porta)
            )  # Conecta ao IP e porta do destinatário
            mensagem = f"{nome_cliente} {conteudo}"  # Formata a mensagem
            soquete_destinatario.send(mensagem.encode("utf-8"))  # Envia a mensagem
            print(f"\n{'-'*40}")
            print(f"Mensagem enviada para {nome_destinatario}")
            print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'-'*40}\n")
    except Exception as e:
        print(
            f"Erro ao enviar a mensagem: {e}"
        )  # Exibe mensagem de erro se ocorrer um problema


# Função para listar todas as mensagens recebidas
def listar_mensagens():
    print("\nMensagens recebidas: ")
    for (
        remetente,
        mensagens_cliente,
    ) in mensagens.items():  # Itera sobre as mensagens de cada remetente
        print(f"\nDe: {remetente}")
        for mensagem in mensagens_cliente:
            print(f"\t- {mensagem}")


# Função para receber mensagens de outros clientes
def receber_mensagem(soquete_cliente: socket.socket):
    while True:
        conexao, _ = soquete_cliente.accept()  # Aceita uma nova conexão
        mensagem = conexao.recv(1024).decode("utf-8")  # Recebe a mensagem
        partes = mensagem.split(maxsplit=1)  # Divide a mensagem em remetente e conteúdo
        if len(partes) < 2:
            continue  # Ignora mensagens mal formatadas
        remetente = partes[0]  # Extrai o remetente
        conteudo = partes[1]  # Extrai o conteúdo da mensagem
        mensagens.setdefault(remetente, []).append(
            conteudo
        )  # Armazena a mensagem na lista correspondente


# Função principal que gerencia a tarefa do cliente
def client_task(nome_cliente: str):
    host = "127.0.0.1"  # Endereço IP do servidor
    porta = 5001  # Porta do servidor
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
    soquete.connect((host, porta))  # Conecta ao servidor

    soquete.send(nome_cliente.encode("utf-8"))  # Envia o nome do cliente ao servidor
    print(f"Nome do cliente {nome_cliente} enviado ao servidor.")

    soquete_cliente = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    )  # Cria um socket para receber mensagens
    soquete_cliente.bind(("", 0))  # Associa o socket a uma porta disponível
    soquete_cliente.listen(1)  # Define o socket para escutar uma conexão
    porta_cliente = soquete_cliente.getsockname()[
        1
    ]  # Obtém a porta local usada pelo socket

    soquete.send(
        f"PORT {porta_cliente}".encode("utf-8")
    )  # Envia a porta local ao servidor

    # Cria uma nova thread para receber mensagens
    receber_mensagem_thread = threading.Thread(
        target=receber_mensagem, args=(soquete_cliente,)
    )
    receber_mensagem_thread.start()  # Inicia a thread para receber mensagens

    while True:
        escolha = exibir_menu()  # Exibe o menu e obtém a escolha do usuário
        if escolha == "1":
            enviar_mensagem(soquete, nome_cliente)  # Envia uma mensagem
        elif escolha == "2":
            listar_mensagens()  # Lista as mensagens recebidas
        elif escolha == "3":
            print("Saindo...")
            soquete.close()  # Fecha a conexão com o servidor
            soquete_cliente.close()  # Fecha o socket de recebimento de mensagens
            break  # Sai do loop
        else:
            print("Escolha inválida.")  # Mensagem de erro para escolha inválida


# Verifica se o script está sendo executado diretamente e não importado como módulo
if __name__ == "__main__":
    nome_cliente = input("Digite o nome do cliente: ")  # Solicita o nome do cliente
    client_task(nome_cliente)  # Executa a função principal do cliente
