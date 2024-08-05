import socket
import threading
import unittest
import time

# TODO: precisa garantir que o contador de threads puxe o resultado de todos os núcleos da forma correta por meio de semáforos


client_thread_count = 0  # Contador global para threads de clientes
client_thread_lock = threading.Lock()  # Lock para proteger o contador


# Função do servidor que será usada nos testes
def server_task(port, received_messages, stop_event):
    def handle_client(conexao, cliente):
        while True:
            mensagem = conexao.recv(1024)
            if not mensagem:
                break  # Se não houver mensagem, sai do loop
            received_messages.append(
                mensagem.decode("utf-8")
            )  # Adiciona mensagem recebida à lista
        conexao.close()

    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soquete.bind(("127.0.0.1", port))
    soquete.listen()
    print("\nServidor iniciado e aguardando conexões...")

    while not stop_event.is_set():
        try:
            soquete.settimeout(1)  # Define timeout para aceitar conexões
            conexao, cliente = soquete.accept()
            client_thread = threading.Thread(
                target=handle_client, args=(conexao, cliente)
            )  # Cria uma nova thread para lidar com o cliente
            client_thread.start()
        except socket.timeout:
            continue
    soquete.close()
    print("\nServidor encerrado após receber todas as mensagens.")


# Função de teste do cliente
def client_task(client_id, port):
    global client_thread_count

    with client_thread_lock:
        client_thread_count += 1  # Incrementa o contador de threads de clientes

    host = "127.0.0.1"
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destino = (host, port)

    try:
        soquete.connect(destino)
        mensagem = f"Olá Mundo! -> from client {client_id}"
        soquete.send(mensagem.encode("utf-8"))  # Envia a mensagem codificada em bytes
        print(f"\nCliente {client_id} enviou: {mensagem}")
    finally:
        soquete.close()
        print(f"\nCliente {client_id} fechou a conexão")


# Classe de teste unittests para o servidor
class TestServer(unittest.TestCase):
    def setUp(self):
        self.port = 5001
        self.received_messages = []  # Lista para armazenar mensagens recebidas
        self.stop_event = threading.Event()
        self.server_thread = threading.Thread(
            target=server_task,
            args=(self.port, self.received_messages, self.stop_event),
        )  # Cria uma thread para o servidor
        self.server_thread.start()
        time.sleep(1)  # Aguarda servidor iniciar

    def test_server_handles_multiple_clients(self):
        global client_thread_count
        client_thread_count = 0  # Reseta o contador

        num_clients = 10
        client_threads = []
        for i in range(num_clients):
            t = threading.Thread(target=client_task, args=(i, self.port))
            client_threads.append(t)
            t.start()  # Inicia a thread do cliente

        for t in client_threads:
            t.join()  # Aguarda todas as threads de clientes finalizarem

        time.sleep(2)  # Espera o servidor processar as mensagens

        expected_messages = [
            f"Olá Mundo! -> from client {i}" for i in range(num_clients)
        ]  # Lista de mensagens esperadas

        # Verificar se todas as mensagens esperadas foram recebidas
        missing_messages = [
            msg for msg in expected_messages if msg not in self.received_messages
        ]
        if missing_messages:
            print(f"\nMensagens ausentes: {missing_messages}")

        self.assertCountEqual(
            self.received_messages, expected_messages
        )  # Verifica se as listas têm os mesmos elementos

        print(f"\nTotal de threads de cliente utilizadas: {client_thread_count}")
        self.assertEqual(
            client_thread_count,
            num_clients,
            "\nO servidor não utilizou a quantidade esperada de threads de clientes.",
        )

    def tearDown(self):
        self.stop_event.set()  # Sinaliza para o servidor encerrar
        self.server_thread.join(timeout=2)  # Aguarda a thread do servidor encerrar


if __name__ == "__main__":
    unittest.main()
