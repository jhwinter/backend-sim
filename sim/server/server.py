import argparse
import logging
import json
import random
import string
import urllib.parse

from http.server import HTTPServer, BaseHTTPRequestHandler

from . import db
from ..common.config import load_config


class BaseJSONHandler(BaseHTTPRequestHandler):
    """BaseJSONHandler

    This handler class manages incoming POST requests and returns
    JSON-formatted dictionaries.
    Subclasses are intended to implement the path handlers and associated
    execution methods.
    """
    def do_POST(self):
        try:
            # whitelisted paths
            no_data_paths = ['status', 'animals']
            retrieve_data_paths = ['animal']
            store_data_paths = ['store_animal', 'store_user']

            path = self.path.split('/')

            # authenticate user unless a user is being added
            if path[1] != 'store_user':
                url = urllib.parse.urlsplit(self.path).query
                api_key = dict(urllib.parse.parse_qsl(url))
                if self._authenticate_user(api_key) != True:
                    self.send_error(200, message='invalid api key')

            # process the request
            handler = self.get_handler_for_path(path[1])
            if handler is None:
                self.send_error(404)
            else:
                response_object = None
                if path[1] in no_data_paths:
                    response_object = handler()
                elif path[1] in retrieve_data_paths:
                    response_object = handler(path[2])
                elif path[1] in store_data_paths:
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length).decode('utf-8')
                    data = dict(urllib.parse.parse_qsl(body))
                    print(f"\n\n{data}\n\n")
                    response_object = handler(data)

                self._send_json_response(response_object)
        except Exception:
            logging.exception('Uncaught exception')
            self.send_error(500)

    def get_handler_for_path(self, path: str):
        """get_handler_for_path

        Should be implemented by subclasses.
        Returns:
            Callable if found, None otherwise.
        """
        raise NotImplementedError()

    def _send_json_response(self, json_object):
        response_content = json.dumps(json_object).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response_content))
        self.end_headers()
        self.wfile.write(response_content)

    def _authenticate_user(self, api_key: str):
        """authenticates users
        """
        session = self.server.database.create_session()
        try:
            user = session.query(db.User).filter(db.User.api_key == api_key)
            return False if not user else True
        finally:
            session.close()



class RequestHandler(BaseJSONHandler):
    """RequestHandler

    Implements path handlers for the server.
    """
    def get_handler_for_path(self, path: str):
        handlers = {
            'status': self._handle_status_request,
            'animals': self._handle_animals_request,
            'animal': self._handle_animal_request,
            'store_animal': self._handle_store_animal_request,
            'store_user': self._handle_store_user_request
        }
        return handlers.get(path)

    def _handle_status_request(self) -> dict:
        return {'status': 'ok'}

    def _handle_animals_request(self) -> dict:
        session = self.server.database.create_session()
        try:
            animals = session.query(db.Animal).all()
            return {'animals': [a.as_dict() for a in animals]}
        finally:
            session.close()

    def _handle_animal_request(self, id: int) -> dict:
        id = int(id)
        session = self.server.database.create_session()
        try:
            animal = session.query(db.Animal).get(id)
            return animal.as_dict()
        finally:
            session.close()

    def _handle_store_animal_request(self, data: dict) -> bool:
        session = self.server.database.create_session()
        try:
            animal = db.Animal(
                name=data["name"],
                species=data["species"]
            )
            session.add(animal)
            session.commit()
            return True
        finally:
            session.close()

    def _handle_store_user_request(self, data: dict) -> bool:
        session = self.server.database.create_session()
        try:
            user = db.User(
                email=data["email"],
                api_key=generate_random_string()
            )
            session.add(user)
            session.commit()
            return True
        finally:
            session.close()


class Server(HTTPServer):
    def __init__(self, config):
        super().__init__(
            (config['hostname'], config['port']),
            RequestHandler,
        )
        self.config = config
        self.database = db.Database(config)


def generate_random_string(length: int = 8) -> str:
    """randomly generate a cryptographically secure string

    https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits/23728630#23728630
    """
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Simulation server starting...')
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='simulation.cfg')
    args = parser.parse_args()

    httpd = Server(load_config(args.config))
    httpd.serve_forever()


if __name__ == '__main__':
    main()
