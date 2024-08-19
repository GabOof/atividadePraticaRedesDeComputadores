import socket
import threading
from datetime import datetime
import hashlib
from typing import Any

# Dicionário para armazenar informações dos clientes conectados
# Chave: hash do nome do cliente, Valor: (nome, IP, porta)
clientes_conectados = {}


def generate_client_hash(nome_cliente: str) -> str:
    # Gera um hash SHA-256 do nome do cliente para identificação única.
    return hashlib.sha256(nome_cliente.encode()).hexdigest()


def store_client_info(id_cliente: str, nome_cliente: str, endereco: str, porta: int):

    # Armazena as informações do cliente no dicionário e exibe detalhes da conexão.

    # Args:
    #     id_cliente (str): O hash do nome do cliente.
    #     nome_cliente (str): O nome do cliente.
    #     endereco (str): O endereço IP do cliente.
    #     porta (int): A porta do cliente.

    clientes_conectados[id_cliente] = (nome_cliente, endereco, porta)
    print(f"\n{'-'*40}")
    print(f"Cliente {nome_cliente} (ID: {id_cliente}) conectado:")
    print(f"Endereço: {endereco}:{porta}")
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'-'*40}\n")


def send_location(conexao: Any, nome_destinatario: str):

    # Envia a localização (IP e porta) do destinatário ao cliente.

    # Args:
    #     conexao (Any): O objeto de conexão do cliente.
    #     nome_destinatario (str): O nome do destinatário para localização.

    destinatario_hash = generate_client_hash(
        nome_destinatario
    )  # Gera o hash do nome do destinatário
    if destinatario_hash in clientes_conectados:
        _, ip, porta = clientes_conectados[destinatario_hash]
        conexao.send(f"{ip} {porta}".encode("utf-8"))  # Envia IP e porta para o cliente
    else:
        conexao.send(
            "Destinatário não encontrado".encode("utf-8")
        )  # Envia mensagem de erro


def send_client_hash(conexao: Any, nome_destinatario: str):

    # Envia o hash do nome do destinatário ao cliente.

    # Args:
    #     conexao (Any): O objeto de conexão do cliente.
    #     nome_destinatario (str): O nome do destinatário para obter o hash.

    destinatario_hash = generate_client_hash(
        nome_destinatario
    )  # Gera o hash do nome do destinatário
    if destinatario_hash in clientes_conectados:
        conexao.send(destinatario_hash.encode("utf-8"))  # Envia o hash para o cliente
    else:
        conexao.send(
            "Destinatário não encontrado".encode("utf-8")
        )  # Envia mensagem de erro


def handle_commands(conexao: Any, id_cliente: str, nome_cliente: str, endereco: str):

    # Processa os comandos recebidos do cliente e executa as ações apropriadas.

    # Args:
    #     conexao (Any): O objeto de conexão do cliente.
    #     id_cliente (str): O hash do nome do cliente.
    #     nome_cliente (str): O nome do cliente.
    #     endereco (str): O endereço IP do cliente.

    try:
        while True:
            dados = conexao.recv(1024).decode(
                "utf-8"
            )  # Recebe os dados enviados pelo cliente
            if not dados:
                break  # Encerra o loop se a conexão for fechada

            comando, *argumentos = dados.split()  # Separa o comando dos argumentos
            if comando == "PORT":
                porta = int(argumentos[0])
                store_client_info(
                    id_cliente, nome_cliente, endereco[0], porta
                )  # Armazena as informações do cliente
            elif comando == "LOCATE":
                send_location(
                    conexao, " ".join(argumentos)
                )  # Envia a localização do destinatário
            elif comando == "GET_HASH":
                send_client_hash(
                    conexao, " ".join(argumentos)
                )  # Envia o hash do destinatário
    except Exception as e:
        print(f"Erro: {e}")  # Captura e exibe qualquer erro que ocorra
    finally:
        print(f"\n{'-'*40}")
        print(f"Cliente {nome_cliente} (ID: {id_cliente}) desconectado:")
        print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*40}\n")
        if id_cliente in clientes_conectados:
            del clientes_conectados[
                id_cliente
            ]  # Remove o cliente desconectado do dicionário
        conexao.close()  # Fecha a conexão com o cliente


def handle_client(conexao, endereco):

    # Lida com a conexão de um cliente, recebendo e processando seus dados.

    # Args:
    #     conexao: O objeto de conexão do cliente.
    #     endereco: O endereço IP e porta do cliente.

    try:
        nome_cliente = conexao.recv(1024).decode("utf-8")  # Recebe o nome do cliente
        id_cliente = generate_client_hash(
            nome_cliente
        )  # Gera o hash do nome do cliente
        handle_commands(
            conexao, id_cliente, nome_cliente, endereco
        )  # Processa comandos do cliente
    except Exception as e:
        print(f"Erro: {e}")  # Captura e exibe qualquer erro que ocorra
    finally:
        conexao.close()  # Fecha a conexão com o cliente


def main():
    # Função principal que inicializa o servidor e aceita conexões de clientes.
    host = "127.0.0.1"  # Endereço IP onde o servidor vai escutar
    porta = 5001  # Porta onde o servidor vai escutar
    soquete = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    )  # Cria um objeto de socket TCP
    soquete.bind((host, porta))  # Associa o socket ao endereço e porta
    soquete.listen(0)  # Inicia o modo de escuta por conexões (0 conexões na fila)
    print(f"Servidor iniciado em {host}:{porta}")

    while True:
        conexao, endereco = soquete.accept()  # Aceita uma nova conexão
        print(f"Conexão aceita de {endereco}")
        thread_cliente = threading.Thread(
            target=handle_client, args=(conexao, endereco)
        )
        thread_cliente.start()  # Inicia uma nova thread para lidar com o cliente


if __name__ == "__main__":
    main()  # Executa a função principal quando o script é executado
