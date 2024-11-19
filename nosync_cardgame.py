import threading
import random
import time

# 초기 설정
turn_cards = []  # Reader와 Writer가 동시에 접근할 공유 데이터
players = [{"id": i, "score": 0} for i in range(1, 6)]
game_over = False


def player(player_id):
    """Player(Writer)가 카드를 제출"""
    global turn_cards, game_over
    while not game_over:
        letter = random.choice("abcdefghijklmnopqrstuvwxyz")
        number = random.randint(0, 9)
        turn_cards.append({"player_id": player_id, "card": (letter, number)})
        time.sleep(random.uniform(0.01, 0.1))  # 랜덤 지연 시간


def reader():
    """Reader가 카드를 읽고 점수를 계산"""
    global turn_cards, players, game_over
    while not game_over:
        if len(turn_cards) >= 5:  # 5개의 카드가 모였는지 확인
            cards = turn_cards[:5]
            turn_cards = turn_cards[5:]  # 처리한 카드를 제거

            # 점수 계산 (간단히 동일 알파벳이면 점수 추가)
            letters = [card["card"][0] for card in cards]
            for card in cards:
                player_id = card["player_id"]
                letter = card["card"][0]
                if letters.count(letter) > 1:  # 동일 알파벳 점수
                    players[player_id - 1]["score"] += letters.count(letter)

            print(f"Cards Processed: {cards}")
            print(f"Scores: {[p['score'] for p in players]}")

            # 게임 종료 조건
            if any(player["score"] >= 20 for player in players):
                game_over = True


# 스레드 생성 및 실행
player_threads = [threading.Thread(target=player, args=(i,)) for i in range(1, 6)]
reader_thread = threading.Thread(target=reader)

for t in player_threads:
    t.start()
reader_thread.start()

for t in player_threads:
    t.join()
reader_thread.join()
