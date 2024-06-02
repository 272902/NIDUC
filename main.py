from queue import PriorityQueue
import random

from Decoder import Decoder
from Event import Event
from Generator import Generator
from TransmissionCanal import TransmissionCanal
from TransmissionGUI import TransmissionGUI


def compare_signals(signal_in, signal_out):
    """ Porównuje sygnały
        signal_in - sygnał wejściowy
        signal_out - sygnał wyjściowy """

    lost = 0
    for i in range(len(signal_in)):
        if signal_in[i] != signal_out[i]:
            lost += 1

    global stat
    # print("Sygnał wejściowy: ", signal_in)
    # print("Sygnał wyjściowy: ", signal_out)
    stat = lost / len(signal_in)
    stat = round(stat * 100, 2)
    return stat

def simulation (coding, packet_length, num_of_retransmission, signal_length, noise, bandwith):
    generator = Generator(packet_length)
    decoder = Decoder()
    signal = generator.generate_signal(signal_length)
    received_signal = []
    packets = generator.generate_package(signal, coding, 2)

    gui = TransmissionGUI(bandwith, packet_length, num_of_retransmission, noise)
    gui.start_simulation(packets)

if __name__ == '__main__':
    # Typ kodowania 0 - bit parzystości, 1 - CRC-8, 2 - CRC-16, 3 - CRC-32
    coding = 1
    # Długość pakietu
    packet_length = 50
    # Liczba możliwych retransmisji
    num_of_retransmission = 5
    # Długość sygnału
    signal_lenth = 1000
    # Szum w kanale - % na zakłócenie pojedynczej paczki np 0.2 = 20%
    noise = 0.01
    # Szerokość pasma w Mb
    bandwith = 2.4
    # Liczba powtórzeń symulacji
    num_of_repetition = 10

    # Symulacja
    wynik = 0

    # Srednia z wynikow
    for i in range(num_of_repetition):
        wynik += simulation(coding, packet_length, num_of_retransmission, signal_lenth, noise, bandwith)
    print("Wynik: ", wynik / num_of_repetition, "%")