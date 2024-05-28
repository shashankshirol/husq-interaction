import rclpy
import threading
import sys
import tty
import termios
import socket
import time


from rclpy.node import Node
from hqv_public_interface.msg import RemoteDriverDriveCommand


keep_going = True
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

def GetchUnix():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def thread_function(keyboard_controller, sock: socket.socket):
    global keep_going
    menu = """
        Menu:

        q - quit
        w - move forward
        s - move backward
        a - move left
        d - move right

        c - clear
        b - strobe light (attention)
        n - waiting
        m - set solid

        u - yield way - interaction 1
        y - make move - interaction 3
    """

    print(menu)
    s = 0.95
    delay = 1.5

    MODE = 0
    light = 1

    while True:
        key = GetchUnix()

        if key == 'q':
            keep_going = False
            sock.sendall("q".encode())
            sock.close()
            keyboard_controller.executor.shutdown()
            return
        elif key == 'w':
            keyboard_controller.move(s, 0.0)
            if(MODE and not light):
                sock.sendall("y-2".encode())
                light = 1

        elif key == 's':
            keyboard_controller.move(-s, 0.0)
            if(MODE and light):
                sock.sendall("y-1".encode())
                light = 0
        
        elif key == 'a':
            keyboard_controller.move(s, 2.0)
        elif key == 'd':
            keyboard_controller.move(s, -2.0)
        
        elif key == "c":
            sock.sendall("c".encode())

        elif key == 'u':
            ## Yield way interaction
            sock.sendall("u-1".encode())
            start_t = time.monotonic()
            while(time.monotonic() <= start_t + delay):
                keyboard_controller.move(-s, 0.0)

            time.sleep(1)
            sock.sendall("u-2".encode())
            start_t = time.monotonic()
            while(time.monotonic() <= start_t + delay - 0.1):
                keyboard_controller.move(s, 2.0)

            start_t = time.monotonic()
            while(time.monotonic() <= start_t + delay + 0.3):
                keyboard_controller.move(-s, 0.0)
            
            sock.sendall("n".encode())

        elif key == "n":
            ## Waiting light
            sock.sendall("n".encode())
        
        elif key == "m":
            ## Solid light
            sock.sendall("m".encode())
        
        elif key == "b":
            ## Stroble light
            sock.sendall("b".encode())

        elif key == "y":
            ## Make human move
            MODE = 1 if not MODE else 0
            # for i in range(3):
            #     time.sleep(0.2)
            #     sock.sendall("y-1".encode())
            #     start_t = time.monotonic()
            #     while(time.monotonic() <= start_t + delay):
            #         keyboard_controller.move(-s, 0.0)

            #     sock.sendall("y-2".encode())
            #     start_t = time.monotonic()
            #     while(time.monotonic() <= start_t + delay):
            #         keyboard_controller.move(s, 0.0)
                
            # keyboard_controller.move(-s, 0.0)
            # sock.sendall("m".encode())




class Enhanced_RD(Node):

    def __init__(self):
        super().__init__('remote_drive')
        self.drive_publisher = self.create_publisher(RemoteDriverDriveCommand, '/hqv_mower/remote_driver/drive', 100)

    def move(self, speed, steering):
        msg = RemoteDriverDriveCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.speed = speed
        msg.steering = steering
        self.drive_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    remote_drive = Enhanced_RD()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    thread = threading.Thread(target=thread_function, args=(remote_drive, sock))
    thread.start()

    while keep_going:
        rclpy.spin_once(remote_drive)

    remote_drive.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
