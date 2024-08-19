import socket  # Importa o módulo para operações de rede usando sockets
import threading  # Importa o módulo para criar e gerenciar threads
from datetime import (
    datetime,
)  # Importa a classe datetime para manipulação de datas e horas
import hashlib  # Importa o módulo para criar hashes de strings
from typing import Any, Tuple, Dict  # Importa tipos para anotações

# Dicionário para armazenar informações dos clientes conectados
clientes_conectados: Dict[str, Tuple[str, str, int]] = {}


# Função para gerar um hash SHA-256 a partir do nome do cliente
def generate_client_hash(nome_cliente: str) -> str:
    return hashlib.sha256(nome_cliente.encode()).hexdigest()


# Função para armazenar informações do cliente conectado
def store_client_info(id_cliente: str, nome_cliente: str, endereco: str, porta: int):
    clientes_conectados[id_cliente] = (nome_cliente, endereco, porta)
    # Exibe informações do cliente conectado no console
    print(f"\n{'-'*40}")
    print(f"Cliente {nome_cliente} (ID: {id_cliente}) conectado:")
    print(f"Endereço: {endereco}:{porta}")
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'-'*40}\n")


# Função para enviar a localização do destinatário para o cliente
def send_location(conexao: Any, nome_destinatario: str):
    destinatario_hash = generate_client_hash(nome_destinatario)
    # Verifica se o destinatário está na lista de clientes conectados
    if destinatario_hash in clientes_conectados:
        _, ip, porta = clientes_conectados[destinatario_hash]
        conexao.send(f"{ip} {porta}".encode("utf-8"))  # Envia IP e porta para o cliente
    else:
        conexao.send(
            "Destinatário não encontrado".encode("utf-8")
        )  # Responde se destinatário não encontrado


# Função para enviar o hash do cliente para o cliente
def send_client_hash(conexao: Any, nome_destinatario: str):
    destinatario_hash = generate_client_hash(nome_destinatario)
    if destinatario_hash in clientes_conectados:
        conexao.send(destinatario_hash.encode("utf-8"))  # Envia o hash para o cliente
    else:
        conexao.send(
            "Destinatário não encontrado".encode("utf-8")
        )  # Responde se destinatário não encontrado


# Função para processar comandos recebidos dos clientes
def handle_commands(conexao: Any, id_cliente: str, nome_cliente: str, endereco: str):
    try:
        while True:
            dados = conexao.recv(1024).decode("utf-8")  # Recebe dados do cliente
            if not dados:  # Verifica se não há mais dados (cliente desconectado)
                break

            comando, *argumentos = dados.split(
                maxsplit=1
            )  # Divide o comando e os argumentos
            if comando == "PORT":
                porta = int(argumentos[0])  # Converte a porta para inteiro
                store_client_info(
                    id_cliente, nome_cliente, endereco[0], porta
                )  # Armazena informações do cliente
            elif comando == "LOCATE":
                send_location(
                    conexao, " ".join(argumentos)
                )  # Envia localização do destinatário
            elif comando == "GET_HASH":
                send_client_hash(
                    conexao, " ".join(argumentos)
                )  # Envia hash do destinatário
            elif comando == "BROADCAST":
                conteudo = argumentos[0]  # Conteúdo da mensagem
                mensagem = f"{nome_cliente} {conteudo}"  # Formata a mensagem
                # Envia a mensagem para todos os clientes conectados
                for id_cliente_destinatario, (
                    nome_destinatario,
                    ip,
                    porta,
                ) in clientes_conectados.items():
                    if id_cliente_destinatario != id_cliente:
                        try:
                            with socket.socket(
                                socket.AF_INET, socket.SOCK_STREAM
                            ) as soquete_destinatario:
                                soquete_destinatario.connect((ip, porta))
                                soquete_destinatario.send(mensagem.encode("utf-8"))
                        except Exception as e:
                            print(f"Erro ao enviar mensagem para {ip}:{porta} - {e}")
    except Exception as e:
        print(
            f"Erro: {e}"
        )  # Exibe erro caso ocorra durante o processamento dos comandos
    finally:
        # Exibe informações do cliente desconectado no console
        print(f"\n{'-'*40}")
        print(f"Cliente {nome_cliente} (ID: {id_cliente}) desconectado:")
        print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*40}\n")
        if id_cliente in clientes_conectados:
            del clientes_conectados[id_cliente]  # Remove o cliente da lista
        conexao.close()  # Fecha a conexão com o cliente


# Função para lidar com um cliente específico
def handle_client(conexao, endereco):
    try:
        nome_cliente = conexao.recv(1024).decode("utf-8")  # Recebe o nome do cliente
        id_cliente = generate_client_hash(nome_cliente)  # Gera hash do cliente
        handle_commands(
            conexao, id_cliente, nome_cliente, endereco
        )  # Processa comandos do cliente
    except Exception as e:
        print(f"Erro: {e}")  # Exibe erro se ocorrer durante o manuseio do cliente
    finally:
        conexao.close()  # Fecha a conexão com o cliente


# Função principal para iniciar o servidor
def main():
    host = "127.0.0.1"  # Endereço IP do servidor
    porta = 5001  # Porta do servidor
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
    soquete.bind((host, porta))  # Associa o socket ao endereço e porta
    soquete.listen(
        0
    )  # Define o socket para escutar conexões (0 para conexões indefinidas)
    print(f"Servidor iniciado em {host}:{porta}")

    while True:
        conexao, endereco = soquete.accept()  # Aceita uma conexão do cliente
        print(f"Conexão aceita de {endereco}")
        # Cria uma nova thread para lidar com o cliente
        thread_cliente = threading.Thread(
            target=handle_client, args=(conexao, endereco)
        )
        thread_cliente.start()  # Inicia a thread


if __name__ == "__main__":
    main()  # Executa a função principal quando o script é executado
