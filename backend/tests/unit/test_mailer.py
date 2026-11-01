import socketserver
import threading
from types import SimpleNamespace

import pytest

from beront.modules.orders.infrastructure.mailer import BackgroundMailer, SmtpMailer


class Handler(socketserver.StreamRequestHandler):
    def reply(self, line):
        self.wfile.write(line.encode() + b"\r\n")

    def handle(self):
        self.reply("220 test")
        data = False
        for raw in self.rfile:
            line = raw.decode(errors="replace").rstrip("\r\n")
            if data:
                if line == ".":
                    data = False
                    self.reply("250 queued")
                else:
                    self.server.captured.append(line)
                continue
            command = line.split(" ", 1)[0].upper()
            if command in {"EHLO", "HELO"}:
                self.reply("250 test")
            elif command in {"MAIL", "RCPT", "NOOP"}:
                self.reply("250 ok")
            elif command == "DATA":
                data = True
                self.reply("354 go")
            elif command == "QUIT":
                self.reply("221 bye")
                return
            else:
                self.reply("502 unsupported")


@pytest.fixture
def smtp_server():
    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
    server.captured = []
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def settings(port, **extra):
    values = {
        "smtp_host": "127.0.0.1",
        "smtp_port": port,
        "smtp_username": "",
        "smtp_password": "",
        "smtp_sender": "tienda@example.test",
        "smtp_security": "none",
    }
    return SimpleNamespace(**{**values, **extra})


def test_message_is_delivered_to_the_local_smtp_server(smtp_server):
    mailer = SmtpMailer(settings(smtp_server.server_address[1]))
    assert mailer.configured
    mailer.send("cliente@example.test", "Asunto de prueba", "Cuerpo de prueba")
    text = "\n".join(smtp_server.captured)
    assert "To: cliente@example.test" in text and "From: tienda@example.test" in text
    assert "Subject: Asunto de prueba" in text


def test_unconfigured_mailer_reports_it():
    assert not SmtpMailer(settings(25, smtp_host="")).configured


def test_background_delivery_never_raises_to_the_request():
    mailer = BackgroundMailer(SmtpMailer(settings(9)))
    mailer.send("cliente@example.test", "Asunto", "Cuerpo")
    mailer.executor.shutdown(wait=True)
    assert mailer.configured


def test_background_delivery_uses_the_wrapped_mailer(smtp_server):
    mailer = BackgroundMailer(SmtpMailer(settings(smtp_server.server_address[1])))
    mailer.send("cliente@example.test", "Asunto", "Cuerpo")
    mailer.executor.shutdown(wait=True)
    assert any("Subject: Asunto" in line for line in smtp_server.captured)
