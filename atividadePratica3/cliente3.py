from datetime import datetime
import socket
import threading
import hashlib

# TODO: falta ainda a parte de enviar mensagem para todos quando o destinatário não é fornecido (acho que só falta isso!!)

# Dicionário para armazenar mensagens recebidas
# Chave: remetente, Valor: lista de mensagens recebidas desse remetente
mensagens = {}

# Dicionário para armazenar os destinatários contatados
# Chave: hash do nome do destinatário, Valor: (IP, porta)
destinatarios_contatados = {}


def exibir_menu():

    # Exibe o menu de opções para o usuário e captura sua escolha.

    print(f"\n{'='*80}")
    print("Escolha uma ação:")
    print("1. Enviar mensagem")
    print("2. Listar mensagens")
    print("3. Sair")
    print(f"{'='*80}\n")
    # Captura a escolha do usuário
    escolha = input("Digite o número da ação desejada: ")
    return escolha


def enviar_mensagem(soquete, nome_cliente):

    # Envia uma mensagem para um destinatário, conectando diretamente a ele.

    # Args:
    #     soquete: O objeto de conexão com o servidor.
    #     nome_cliente: O nome do cliente que está enviando a mensagem.

    # Captura o nome do destinatário
    nome_destinatario = input("\nDigite o nome do destinatário: ")
    # Captura o conteúdo da mensagem
    conteudo = input("\nDigite a mensagem: ")

    # Gera o hash do destinatário para identificação
    destinatario_hash = hashlib.sha256(nome_destinatario.encode()).hexdigest()

    if destinatario_hash in destinatarios_contatados:
        # Obtém IP e porta do destinatário a partir do dicionário
        ip, porta = destinatarios_contatados[destinatario_hash]
        porta = int(porta)  # Converte a porta para inteiro
    else:
        # Solicita a localização do destinatário ao servidor
        soquete.send(f"LOCATE {nome_destinatario}".encode("utf-8"))
        resposta = soquete.recv(1024).decode("utf-8")

        if resposta == "Destinatário não encontrado":
            print(
                resposta
            )  # Imprime a mensagem de erro se o destinatário não for encontrado
            return

        # Separa o IP e a porta do destinatário
        ip, porta = resposta.split()
        porta = int(porta)  # Converte a porta para inteiro

        # Armazena o destinatário contatado para futuras referências
        destinatarios_contatados[destinatario_hash] = (ip, porta)

    # Conecta diretamente ao destinatário e envia a mensagem
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soquete_destinatario:
        soquete_destinatario.connect((ip, porta))  # Conecta ao destinatário
        mensagem = f"{nome_cliente} {conteudo}"  # Prepara a mensagem para envio
        soquete_destinatario.send(mensagem.encode("utf-8"))  # Envia a mensagem
        # Imprime informações sobre a mensagem enviada
        print(f"\n{'-'*40}")
        print(f"Mensagem enviada para {nome_destinatario}")
        print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*40}\n")


def listar_mensagens():

    # Lista todas as mensagens recebidas, agrupadas por remetente.

    print("\nMensagens recebidas: ")  # Exibe as mensagens recebidas
    for remetente, mensagens_cliente in mensagens.items():
        print(f"\nDe: {remetente}")  # Exibe o remetente
        for mensagem in mensagens_cliente:
            print(f"\t- {mensagem}")  # Exibe cada mensagem recebida


def receber_mensagem(soquete_cliente):

    # Recebe mensagens diretamente de outros clientes e armazena no dicionário.

    # Args:
    #     soquete_cliente: O objeto de socket para receber conexões de outros clientes.

    while True:
        # Aceita uma conexão do cliente
        conexao, _ = soquete_cliente.accept()
        # Recebe a mensagem do cliente
        mensagem = conexao.recv(1024).decode("utf-8")
        remetente, conteudo = mensagem.split(
            maxsplit=1
        )  # Separa o remetente do conteúdo
        # Armazena a mensagem recebida
        mensagens.setdefault(remetente, []).append(conteudo)


def client_task(nome_cliente):

    # Tarefa principal do cliente, incluindo conexão com o servidor e gerenciamento de mensagens.

    # Args:
    #     nome_cliente: O nome do cliente que está executando esta tarefa.

    host = "127.0.0.1"  # Endereço IP do servidor (localhost)
    porta = 5001  # Porta onde o servidor estará escutando
    # Cria um socket TCP/IP
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = (host, porta)
    soquete.connect(destino)  # Conecta ao servidor

    # Envia nome do cliente para o servidor
    soquete.send(nome_cliente.encode("utf-8"))

    # Cria um socket para receber mensagens diretamente de outros clientes
    soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soquete_cliente.bind(("", 0))  # Vincula o socket a uma porta disponível
    soquete_cliente.listen(1)  # Começa a escutar por conexões
    porta_cliente = soquete_cliente.getsockname()[1]  # Obtém a porta do cliente

    # Envia a porta para o servidor
    soquete.send(f"PORT {porta_cliente}".encode("utf-8"))

    # Inicia a thread para receber mensagens diretamente
    receber_mensagem_thread = threading.Thread(
        target=receber_mensagem, args=(soquete_cliente,)
    )
    receber_mensagem_thread.start()

    while True:
        escolha = exibir_menu()  # Exibe o menu e captura a escolha do usuário
        if escolha == "1":
            enviar_mensagem(soquete, nome_cliente)  # Envia uma mensagem
        elif escolha == "2":
            listar_mensagens()  # Lista mensagens recebidas
        elif escolha == "3":
            print("\nFechando conexão...")
            break  # Sai do loop e encerra a conexão
        else:
            print(
                "\nEscolha inválida. Tente novamente."
            )  # Mensagem para escolha inválida

    soquete.close()  # Fecha a conexão com o servidor
    # Imprime informações sobre o encerramento da conexão
    print(f"\n{'='*80}")
    print(f"Cliente {nome_cliente} fechou a conexão")
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")


# Entrada do programa
if __name__ == "__main__":
    nome_cliente = input("\nDigite o nome do cliente: ")  # Captura o nome do cliente
    client_task(nome_cliente)  # Executa a tarefa do cliente com o nome fornecido
