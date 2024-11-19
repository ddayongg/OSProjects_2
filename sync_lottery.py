import threading
import time
import random

buffer = []
BUFFER_SIZE = 10
buffer_lock = threading.Lock()
game_running = True

winning_numbers = random.sample(range(1, 10), 5)
bonus_number = random.choice([num for num in range(1, 10) if num not in winning_numbers])

total_guess = 0  # 추리 횟수
total_money = 0  # 누적 금액
prize_pool = {"1등": 0, "2등": 0}
winners = {"1등": 0, "2등": 0}

def producer():
    global total_guess
    while game_running:
        with buffer_lock:
            if len(buffer) < BUFFER_SIZE:
                lotto_numbers = random.sample(range(1, 10), 5)
                total_guess += 1
                buffer.append((total_guess, lotto_numbers))  # 추리 번호와 함께 추가
                print(f"[Producer] Guess #{total_guess}: Produced Lotto Numbers: {lotto_numbers}")
            else:
                print("[Producer] Buffer is full. Waiting...")
        time.sleep(random.uniform(0.1, 0.5))  # 번호 생성 속도

def consumer():
    global total_money, winning_numbers, bonus_number
    while game_running:
        with buffer_lock:
            if buffer:
                guess_number, lotto_numbers = buffer.pop(0)
                total_money += 10000  # 한 Guess 당 10,000원 누적
                match_count = len(set(lotto_numbers) & set(winning_numbers))
                bonus_match = bonus_number in lotto_numbers

                if match_count == 5:
                    winners["1등"] += 1
                    prize_pool["1등"] += int(total_money * 0.7)  # 1등: 상금의 70%
                    print(f"[Consumer] 🎉 Guess #{guess_number}: 1등 당첨! Numbers: {lotto_numbers}")
                    display_results()
                    wait_for_user_input()
                    reset_game()
                elif match_count == 4 and bonus_match:
                    winners["2등"] += 1
                    prize_pool["2등"] += int(total_money * 0.3)  # 2등: 상금의 30%
                    print(f"[Consumer] 🥈 Guess #{guess_number}: 2등 당첨! Numbers: {lotto_numbers}")
                else:
                    print(f"[Consumer] 😞 Guess #{guess_number}: 꽝. Numbers: {lotto_numbers} | Matches: {match_count}")
            else:
                print("[Consumer] Buffer is empty. Waiting...")
        time.sleep(random.uniform(0.1, 0.5))  # 결과 처리 속도

def display_results():
    print("====================================")
    print(f"총 Guess: {total_guess}, 누적 금액: {total_money}")
    print(f"1등 당첨자: {winners['1등']}명, 총 상금: {prize_pool['1등']}원")
    print(f"2등 당첨자: {winners['2등']}명, 총 상금: {prize_pool['2등']}원")
    print("====================================")

def wait_for_user_input():
    print("1등 당첨! 새로운 시도를 재개하려면 Enter를. 종료하려면 다른 키를 입력.")
    user_input = input()
    if user_input.strip() != "":
        global game_running
        game_running = False

def reset_game():
    global winning_numbers, bonus_number, total_money
    winning_numbers = random.sample(range(1, 10), 5)
    bonus_number = random.choice([num for num in range(1, 10) if num not in winning_numbers])
    print(f"[Consumer] 새로운 당첨 번호: {winning_numbers}, 보너스 번호: {bonus_number}")
    total_money = 0  # 게임 초기화 후 금액 리셋

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
    print("Simulation stopped.")
