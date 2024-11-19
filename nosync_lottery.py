import threading
import time
import random

# 공유 버퍼 설정
buffer = []
BUFFER_SIZE = 10
game_running = True

# 로또 당첨 번호와 보너스 번호
winning_numbers = random.sample(range(1, 10), 5)
bonus_number = random.choice([num for num in range(1, 10) if num not in winning_numbers])

# Producer 역할
def producer():
    global buffer
    while game_running:
        if len(buffer) < BUFFER_SIZE:
            lotto_numbers = random.sample(range(1, 10), 5)
            print(f"[Producer] Before Append: {buffer}")
            time.sleep(0.2)  # 의도적으로 지연
            buffer.append(lotto_numbers)  # Lock 없이 버퍼에 추가
            print(f"[Producer] Produced: {lotto_numbers}")
        time.sleep(random.uniform(0.1, 0.5))

def consumer():
    global buffer
    while game_running:
        if buffer:
            print(f"[Consumer] Before Pop: {buffer}")
            time.sleep(0.2)  # 의도적으로 지연
            lotto_numbers = buffer.pop(0)  # Lock 없이 버퍼에서 제거
            print(f"[Consumer] Consumed: {lotto_numbers}")
        time.sleep(random.uniform(0.1, 0.5))


# 실행 제어
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

try:
    producer_thread.start()
    consumer_thread.start()
    producer_thread.join()
    consumer_thread.join()
except KeyboardInterrupt:
    game_running = False
    producer_thread.join()
    consumer_thread.join()
