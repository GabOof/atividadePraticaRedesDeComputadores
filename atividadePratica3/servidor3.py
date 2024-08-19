import socket
import threading
from datetime import datetime

# Dicionário para armazenar informações dos clientes conectados (hash do nome -> (IP, porta))
clientes_conectados = {}


# Função para lidar com um cliente
def handle_client(conexao, endereco):
    try:
        # Recebe o hash do nome do cliente
        id_cliente = conexao.recv(1024).decode("utf-8")

        while True:  # Loop para lidar com o cliente enquanto ele estiver conectado
            # Recebe dados do cliente
            dados = conexao.recv(1024).decode("utf-8")
            if not dados:  # Verifica se não há mais dados
                break  # Sai do loop se não há mais dados
            # Separa o comando e seus argumentos
            comando, *argumentos = dados.split()

            if comando == "PORT":  # Verifica se o comando é "PORT"
                # Captura a porta do cliente
                porta = int(argumentos[0])
                # Armazena a informação do cliente
                clientes_conectados[id_cliente] = (endereco[0], porta)
                # Imprime informações do cliente conectado
                print(f"\n{'-'*40}")
                print(f"Cliente {id_cliente} conectado:")
                print(f"Endereço: {endereco[0]}:{porta}")
                print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'-'*40}\n")

            elif comando == "LOCATE":  # Verifica se o comando é "LOCATE"
                # Captura o hash do destinatário
                destinatario_hash = argumentos[0]
                if (
                    destinatario_hash in clientes_conectados
                ):  # Verifica se o destinatário está conectado
                    # Recupera as informações do destinatário
                    ip, porta = clientes_conectados[destinatario_hash]
                    # Envia as informações do destinatário para o cliente
                    conexao.send(f"{ip} {porta}".encode("utf-8"))
                else:
                    # Informa que o destinatário não foi encontrado
                    conexao.send("Destinatário não encontrado".encode("utf-8"))

    except Exception as e:  # Captura exceções
        print(f"Erro: {e}")  # Imprime qualquer erro que ocorrer

    finally:  # Bloco final que sempre executa
        # Imprime informações do cliente desconectado
        print(f"\n{'-'*40}")
        print(f"Cliente {id_cliente} desconectado:")
        print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*40}\n")
        if (
            id_cliente in clientes_conectados
        ):  # Verifica se o cliente está no dicionário de clientes conectados
            del clientes_conectados[id_cliente]  # Remove o cliente do dicionário
        conexao.close()  # Fecha a conexão com o cliente


# Função principal do servidor
def main():
    host = "127.0.0.1"  # Endereço IP do servidor (localhost)
    porta = 5001  # Porta onde o servidor estará escutando
    # Cria um socket TCP/IP
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soquete.bind((host, porta))  # Vincula o socket ao endereço e porta especificados
    soquete.listen(5)  # O socket começa a escutar por conexões
    print(
        f"Servidor iniciado em {host}:{porta}"
    )  # Imprime a mensagem informando que o servidor foi iniciado

    while True:  # Loop para aceitar conexões
        # Aceita uma nova conexão
        conexao, endereco = soquete.accept()
        # Cria e inicia uma nova thread para lidar com o cliente
        threading.Thread(target=handle_client, args=(conexao, endereco)).start()


# Código principal para iniciar o servidor
if __name__ == "__main__":
    main()  # Chama a função principal do servidor
