import socket
import threading
import time
import keyboard
import os
import errno
import sys


def get_self_ip():
    """
    get IP address of host.
    :return: ip_address of this device
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()
    s.close()
    return ip[0]


def get_free_port():
    """
    ramdomly get an unoccupied port number.
    :return: (int) a free port number
    """
    s = socket.socket()
    s.bind(('', 0))
    _, port = s.getsockname()
    s.close()
    return port


def init_connection(srv_ip, srv_port):
    """
    Wait and listen to initialize TCP connection from IOS app

    :param srv_ip: (str) IPv4 address string.
    :param srv_port: (int) port number that used for laptop end.
    :return: (svrsock, db2socket, addr) connected socket and its addr(ip, port)
    """
    svrsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srvaddr = (srv_ip, srv_port)
    svrsock.bind(srvaddr)
    print('Laptop IP:', srv_ip)
    print('Laptop Port:', srv_port)
    svrsock.listen(1)
    print('waiting to be connected...')
    clnsock, clnaddr = svrsock.accept()
    print('\nconnected!\n')
    print('IOS IP:', clnaddr[0])
    print('IOS PORT:', clnaddr[1])
    svrsock.settimeout(0)
    clnsock.settimeout(0)
    return svrsock, clnsock, clnaddr


class KeyboardListen:

    def __init__(self, sock=None):
        self.sock = sock
        self.lastmesg = ''

    def kbaction_callback(self, kb_event):
        """
        triggered by keyboard activition. convert the keyboard event to double2 robot
        control command, and sand command via a connected socket.

        :param kb_event: (KeyboardEvent) a keyboard event triggered the function        :param db2sock: (socket) a connected STREAM(TCP) socket used to send command
        :return: no return
        """
        evtype = kb_event.event_type
        keyname = kb_event.name
        self.lastmesg = db2_movement_convert(evtype=evtype, kname=keyname)
        if self.lastmesg is None:
            return
        self.sock.send(self.lastmesg.encode())


class RecvMaintainer:

    def __init__(self, sock=None, buf_size=5, separator=',', end_indicator='\n', recv_rate=100):
        self.sock = sock
        self.state_list_size = buf_size
        self.separator = separator
        self.end_indicator = end_indicator
        self.recv_rate = recv_rate
        self.state_list = []
        self.state_buf_str = ''

    def recv_maintain(self):
        """
        keep running the receiver, read and parse the robot information
        received by connected TCP socket

        :return: None
        """
        while True:
            # maintain the state list size
            while len(self.state_list) > self.state_list_size:
                self.state_list = self.state_list[(len(self.state_list) - self.state_list_size):]

            # read from socket, decode the message, and append to state buffer
            try:
                mesg = self.sock.recv(1024).decode()
                time.sleep(1/self.recv_rate)
            except socket.error as e:
                err = e.args[0]
                # no data in buffer for non-blocking socket to copy
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    mesg = None
                # other error occurs
                else:
                    sys.exit(1)
            else:
                self.state_buf_str += mesg
            update_state = self.state_str_parse()
            if update_state is not None:
                for state in update_state:
                    self.state_list.append(state)
            update_state = None


    def state_str_parse(self):
        """
        parse the robot statu string to list

        :return: None
        """
        # no completed mesg received
        if self.state_buf_str.find(self.end_indicator) == -1:
            return None

        # split completed data and uncompleted data
        last_ei_idx = self.state_buf_str.rfind(self.end_indicator)
        temp = self.state_buf_str[:last_ei_idx]
        self.state_buf_str = self.state_buf_str[last_ei_idx+1:]

        # parse the string
        temp = temp.split(self.end_indicator)
        while '' in temp:
            temp.remove('')
        for i in range(len(temp)):
            temp[i] = temp[i].split(self.separator)
            while '' in temp[i]:
                temp[i] = temp[i].remove('')
        return temp


    def latest_state_data(self):
        """
        fetch latest robot state data from receiver

        :return: (list) robot state data
        """
        if not self.state_list:
            return None
        if not self.state_list[-1]:
            return None
        return self.state_list[-1]


def db2_movement_convert(evtype, kname):
    """
    convert keyboard event into double2 movement code and return
    if unrecognized key obtained, return None

    ======KEYBOARD MANUAL======
        W/up_arrow = forward
        S/down_arrow = backward
        A/left_arrow = turn left
        D/right_arrow = turn right
        P = parking
        V = stop ALL action
        I = pole up
        K = pole down
    ============================

    :param evtype: (string) "down" for pressed, "up" for released
    :param kname: (string) key name
    :return: cooresponding double2 movement code
    """
    if evtype == 'down':
        if kname == 'w' or kname == 'W' or kname == 'up':
            return 'f'
        elif kname == 's' or kname == 'S' or kname == 'down':
            return 'b'
        elif kname == 'a' or kname == 'A' or kname == 'left':
            return 'l'
        elif kname == 'd' or kname == 'D' or kname == 'right':
            return 'r'
        elif kname == 'i' or kname == 'I':
            return 'u'
        elif kname == 'k' or kname == 'K':
            return 'd'

        elif kname == 'p' or kname == 'P':
            return 'p'
        elif kname == 'v' or kname == 'V':
            return 'x'

        else:
            return None

    elif evtype == 'up':
        if kname == 'w' or kname == 'W' or kname == 'up':
            return 's'
        elif kname == 's' or kname == 'S' or kname == 'down':
            return 's'
        elif kname == 'a' or kname == 'A' or kname == 'left':
            return 't'
        elif kname == 'd' or kname == 'D' or kname == 'right':
            return 't'
        elif kname == 'i' or kname == 'I':
            return 'h'
        elif kname == 'k' or kname == 'K':
            return 'h'

        else:
            return None
    else:
        return None


class Db2RemoteController:
    def __init__(self):
        self.ip_addr = get_self_ip()
        self.port = get_free_port()
        self.poll_height = 0
        self.park_state = 0
        self.battery = 0
        self.left_encoder = 0
        self.right_encoder = 0
        self.conn_flag = 0

    def db2_remote_controller(self, update_rate=10, recv_buf_size=5):
        """
        Sample double 2 robot remote controller with terminal UI

        :param update_rate: (int) terminal UI refresh rate in fps
        :param recv_buf_size: (int) the maximum number of clauses will be saved
        :return: none
        """
        svrsock, clnsock, clnaddr = init_connection(self.ip_addr, self.port)
        self.conn_flag = 1
        #if input('PRESS ENTER TO START REMOTE...\nor input "e" to exit\n') is 'e':
        #    exit(0)
        kb_monitor = KeyboardListen(sock=clnsock)
        recv_maintainer = RecvMaintainer(sock=clnsock, buf_size=recv_buf_size, end_indicator='#')
        keyboard.hook(kb_monitor.kbaction_callback)
        threading.Thread(target=recv_maintainer.recv_maintain).start()
        while True:
            if recv_maintainer.latest_state_data() is None:
                continue
            self.poll_height = recv_maintainer.latest_state_data()[0]
            self.park_state = recv_maintainer.latest_state_data()[1]
            self.battery = recv_maintainer.latest_state_data()[2]
            self.left_encoder = recv_maintainer.latest_state_data()[3]
            self.right_encoder = recv_maintainer.latest_state_data()[4]
            print('STATE INFO:')
            print('  Poll Height:', self.poll_height)
            print('   Park State:', self.park_state)
            print('      Battary:', self.battery)
            print(' Left Encoder:', self.left_encoder)
            print('Right Encoder:', self.right_encoder)

            time.sleep(1 / update_rate)
            os.system('clear')



