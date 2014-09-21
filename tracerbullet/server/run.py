from tracerbullet.server.app import ServerProcess
import time

if __name__ == '__main__':
    server_process = ServerProcess()
    server_process.start()
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            server_process.terminate()
            break
