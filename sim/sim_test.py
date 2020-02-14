import unittest
import threading

from .client import Client
from .server.server import Server


test_config = dict(
    hostname='localhost',
    port=8282,
    db='data/test.db',
)


class SimTest(unittest.TestCase):
    def _start_server_thread(self):
        self._client_response = None
        httpd = Server(test_config)

        server_thread = threading.Thread(target=httpd.handle_request)
        server_thread.start()
        return server_thread

    def do_single_request(self, path):
        """do_single_request

        Creates threads for both the server and client and
        executes a single request between the two.
        """
        server_thread = self._start_server_thread()

        def client_thread_target(path):
            client = Client(test_config['hostname'], test_config['port'])
            self._client_response = client.execute(path)

        client_thread = threading.Thread(
            target=client_thread_target,
            args=(path,)
        )
        client_thread.start()

        server_thread.join()
        client_thread.join()

        return self._client_response

    def do_data_request(self, path: str, data: dict):
        """do_data_request

        Creates threads for both the server and client and
        executes a single request between the two.
        """
        server_thread = self._start_server_thread()

        def client_thread_target(path: str, data: dict):
            client = Client(test_config['hostname'], test_config['port'])
            self._client_response = client.execute(path, data)

        client_thread = threading.Thread(
            target=client_thread_target,
            args=(path, data)
        )
        client_thread.start()

        server_thread.join()
        client_thread.join()

        return self._client_response

    def test_status(self):
        response = self.do_single_request('status')
        self.assertEqual(response, {'status': 'ok'})

    def test_animals(self):
        response = self.do_single_request('animals')
        self.assertEqual(len(response['animals']), 10)

    def test_animal_by_id(self):
        response = self.do_single_request('animal/1')
        self.assertEqual(
            response,
            {'id': 1, 'name': 'Bob', 'species': 'Llama'},
            'Fixing this test seems like a good place to start!',
        )

    def test_store_animal(self):
        response = self.do_data_request(
            'store_animal',
            {'name': 'Harambe', 'species': 'Gorilla'}
        )
        self.assertEqual(
            response,
            True
        )

    def test_store_user(self):
        response = self.do_data_request(
            'store_user',
            {'email': 'blah@gmail.com', 'api_key': 'blah'}
        )
        self.assertEqual(response, True)

    def test_authenticate_user(self):
        response = self.do_single_request('store_user?api_key=blah&who=dat')
        self.assertEqual(response, True)

    def test_404(self):
        response = self.do_single_request('some-missing-path')
        self.assertEqual(response[:3], '404')
