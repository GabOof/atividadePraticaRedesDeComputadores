import unittest
import socket
import threading
import time
import sys
import os

# Adiciona o diretório pai ao PYTHONPATH para importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_server():
    import servidor2  # Assumindo que o servidor está no arquivo 'servidor2.py'

    servidor2.main()  # Executa a função main do servidor


def run_cliente(cliente_id):
    import cliente2  # Assumindo que o cliente está no arquivo 'cliente2.py'

    cliente2.client_task(cliente_id)  # Executa a tarefa do cliente com o ID fornecido


class TestClienteServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configura o servidor e o semáforo para os testes"""
        cls.host = "127.0.0.1"
        cls.porta = 5001
        cls.server_thread = threading.Thread(target=run_server)
        cls.server_thread.start()
        time.sleep(2)  # Espera o servidor iniciar

        # Configura um semáforo para garantir a sincronização das threads
        cls.semaforo = threading.Semaphore()
        cls.thread_count = 0

    @classmethod
    def tearDownClass(cls):
        """Encerra o servidor"""
        # Isso geralmente requer um mecanismo para sinalizar o servidor para parar.
        # Aqui, para simplicidade, assumimos que o servidor pode ser interrompido manualmente.
        cls.server_thread.join()

    def test_envio_mensagem(self):
        cliente_id = "1"
        with self.semaforo:
            self.thread_count += 1

        cliente_thread = threading.Thread(target=self.run_cliente, args=(cliente_id,))
        cliente_thread.start()
        cliente_thread.join()

        soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soquete.connect((self.host, self.porta))
        soquete.send(f"{cliente_id} SEND 2 Olá".encode("utf-8"))
        resposta = soquete.recv(1024).decode("utf-8")
        soquete.close()

        with self.semaforo:
            self.thread_count -= 1

        self.assertEqual(resposta, "Mensagem enviada para 2")

    def test_listar_mensagens(self):
        cliente_id = "2"
        with self.semaforo:
            self.thread_count += 1

        cliente_thread = threading.Thread(target=self.run_cliente, args=(cliente_id,))
        cliente_thread.start()
        cliente_thread.join()

        soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soquete.connect((self.host, self.porta))
        soquete.send(f"{cliente_id} LIST {cliente_id}".encode("utf-8"))
        resposta = soquete.recv(1024).decode("utf-8")
        soquete.close()

        with self.semaforo:
            self.thread_count -= 1

        self.assertIn("Mensagens:", resposta)

    def run_cliente(self, cliente_id):
        run_cliente(cliente_id)

    @classmethod
    def tearDown(cls):
        # Imprime o número de threads utilizadas
        print(f"Threads ativas: {cls.thread_count}")


if __name__ == "__main__":
    # Redireciona a saída padrão para capturar prints
    import io

    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    unittest.main(exit=False)

    # Imprime a saída capturada
    output = sys.stdout.getvalue()
    sys.stdout = original_stdout
    print(output)
