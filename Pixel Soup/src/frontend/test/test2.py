import socket
from pickle import loads, dumps


class Pipe:
    def __init__(self, server: str, port: int) -> None:
        self.server = server
        self.port = port
        self.tcp = socket.socket()
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connected = False
        self.username = None
        self.udp_password = None
        self.game_port = None

    def connect(self) -> bool:
        try:
            self.tcp.connect((self.server, self.port))
            self.connected = True
            return True
        except ConnectionError:
            return False

    def login(self, entry: str, room_name: str, username: str) -> list:
        self.username = username
        if not self.connected:
            success = self.connect()
            if not success:
                return False, "error in connection"

        self.tcp.send(f"{entry},,{room_name},,{username}".encode())
        response = self.tcp.recv(100)

        if entry == "create":
            if response == b"Rename":
                return False, "rename"

            elif response == b"Done":
                return True, "created"

            else:
                return False, "invalid"

        else:
            if response == b"Missing":
                return False, "missing"

            elif response == b"Full":
                return False, "full"

            else:
                return True, "joined"

    def await_response(self) -> list:
        try:
            data = self.tcp.recv(1000)
            data = data.decode().split(",,")

            if data[0] == "Start":
                self.game_port = int(data[1])
                self.udp_password = int(data[2])

            return data

        except ConnectionAbortedError:
            return [False]

    def transport(self, game_data: list) -> tuple:
        game_data = [self.udp_password, self.username] + game_data
        game_data = (dumps(game_data)) + b"||||"

        self.udp.sendto(game_data, (self.server, self.game_port))

        data, _ = self.udp.recvfrom(2000)
        data = data.split(b"||||")

        if len(data) > 1:
            data = data[0].split(b"||")
            data = [loads(game) for game in data]

            return True, data
        else:
            return False, None


pl = Pipe(server=socket.gethostname(), port=9000)
print(pl.login(entry="join", room_name="game3", username="Pancho"))

while True:
    packet = pl.await_response()
    print(packet)
    if packet[0] == "Start":
        while True:
            text = input(":::> ")
            print(pl.transport(["press", int(text)]))
