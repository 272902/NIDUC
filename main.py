from queue import PriorityQueue
import random
import tkinter as tk

from Decoder import Decoder
from Event import Event
from Generator import Generator
from TransmissionCanal import TransmissionCanal

def compare_signals(signal_in, signal_out):
    """ Porównuje sygnały
        signal_in - sygnał wejściowy
        signal_out - sygnał wyjściowy """
    lost = 0
    for i in range(len(signal_in)):
        if signal_in[i] != signal_out[i]:
            lost += 1
    global stat
    print("Sygnał wejściowy: ", signal_in)
    print("Sygnał wyjściowy: ", signal_out)
    stat = lost / len(signal_in)
    stat = round(stat * 100, 2)
    return stat

def simulation (coding, packet_length, num_of_retransmission, signal_length, noise, bandwith, type = 0, bits_repetition_numb = 0):
    root=tk.Tk()
    root.title("Packet Transmission Simulation")
    canvas = tk.Canvas(root, width=1400, height=600)
    canvas.pack()
    result_queue = PriorityQueue()
    generator = Generator(packet_length)
    decoder = Decoder()
    #encoder = CorrectionCoding()
    time = []
    events_queue = PriorityQueue()
    current_time = 0.5
    delta_time = 0.5

    signal = generator.generate_signal(signal_length)
    received_signal = []

    packets, rem_packets = generator.generate_package(signal, coding, type)
    transmission_canal = TransmissionCanal(bandwith)
    iter = 0

    for packet in packets:
        r1 = (random.randint(1, 5) / 34)
        r2 = (random.randint(1, 3) / 345)
        duration = r1 * r2 * len(packet) / bandwith
        event = Event(packet, rem_packets[iter], current_time, duration)
        iter += 1

        event_id = iter
        events_queue.put(event)
        current_time += delta_time + (random.randint(1, 3) / 345) * (random.randint(1, 3) / 345)

    while not events_queue.empty():
        event = events_queue.get()
        if transmission_canal.is_free(event.start_time):
            transmission_canal.not_free_to += event.duration
            packet2 = transmission_canal.transmission(event.packet, noise)
            time.append([packet2, transmission_canal.not_free_to])
           #Zdekodowanie kodów korekcyjnych - proba naprawy błedów
            if type == 0:
                packet2 = decoder.hamming_decode(packet2)
            elif type == 1:
                packet2 = decoder.bch_decode(packet2)
            elif type == 2:
                packet2 = decoder.repeat_decode(packet2, bits_repetition_numb)

            # VVVVV -- printowanie packetow -- VVVVV [dlugosc packetow, jak dostac sie do packetu z sygnalu wejsciowego]
            #print(packet,packet2)

            def draw_packet(x, y, status):
                color = "green" if status == "accepted" else "red" if status == "corrupted" else "blue"
                canvas.create_rectangle(x, y, x + 20, y + 10, fill=color)

            x = int(event.start_time * 100)
            y = event.retranmission * 20 + 50
            #VVVVV -- jesli paczka w sygnale wejsciowym jest taka sama jak w sygnale wyjsciowym to "accepted" -- VVVVV
            status = "accepted" if event.packet_before[0:packet_length] == decoder.remove_coding_bits(packet2, coding) else "corrupted"
            draw_packet(x, y, status)

            #print(event.packet_before[0:packet_length],decoder.remove_coding_bits(packet2, coding))

            #Dekodowanie kodów detekcyjnych
            if decoder.receive_package(packet2, coding):
                packet_out = decoder.remove_coding_bits(packet2, coding)
                received_signal += packet_out
                result_queue.put(event)
                continue
            else:
                if event.retranmission <= num_of_retransmission:
                    event.retranmission += 1
                else:
                    print("Packet Rejected")
                    result_queue.put(event)
                    received_signal += decoder.remove_coding_bits(packet2, coding)
                    time.append([packet2, transmission_canal.not_free_to])
                    continue


        event.start_time += delta_time
        events_queue.put(event)
    root.mainloop()
    return compare_signals(signal, received_signal)


if __name__ == '__main__':
    # Typ kodowania 0 - bit parzystości, 1 - CRC-8, 2 - CRC-16, 3 - CRC-32
    coding = 1
    # Typ kodowania korekcyjnego 0 - Hamming, 1 - BCH, 2 - repeat
    type = 0
    # Powtorzenia bitów
    bits_repetition_numb = 3
    # Długość pakietu
    packet_length = 5
    # Liczba możliwych retransmisji
    num_of_retransmission = 4
    # Długość sygnału
    signal_lenth = 20
    # Szum w kanale - % na zakłócenie pojedynczej paczki np 0.2 = 20%
    noise = 0.01
    # Szerokość pasma w Mb
    bandwith = 1000
    # Liczba powtórzeń symulacji
    num_of_repetition = 1

    # Symulacja
    wynik = 0

    # Srednia z wynikow
    for i in range(num_of_repetition):
        wynik += simulation(coding, packet_length, num_of_retransmission, signal_lenth, noise, bandwith, type, bits_repetition_numb)
    print("Wynik: ", wynik / num_of_repetition, "%")