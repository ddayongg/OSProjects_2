import random
import threading
from collections import defaultdict

# 게임 초기 설정
players = [{"id": i, "score": 0} for i in range(1, 6)]
turn_cards = []  # 각 턴 플레이어 제출 카드
scores_lock = threading.Lock()
game_over = threading.Event()
alphabet = "abcdefghijklmnopqrstuvwxyz"
numbers = list(range(10))


def is_prime(n):
    """소수 여부 확인"""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def player(player_id):
    """플레이어가 무작위로 카드를 선택하여 제출"""
    while not game_over.is_set():
        letter = random.choice(alphabet)
        number = random.choice(numbers)
        with scores_lock:
            turn_cards.append({"player_id": player_id, "card": (letter, number)})
        threading.Event().wait(0.1)  # 각 플레이어 간 약간의 지연


def reader():
    """심판이 점수를 계산"""
    global game_over
    while not game_over.is_set():
        if len(turn_cards) == 5:  # 모든 플레이어의 카드가 제출되었는지 확인
            with scores_lock:
                cards = [card["card"] for card in turn_cards]
                player_ids = [card["player_id"] for card in turn_cards]
                letters = [card[0] for card in cards]
                numbers = [card[1] for card in cards]

                letter_scores = defaultdict(int)
                sorted_letters = sorted(letters)
                for i in range(len(sorted_letters) - 1):
                    if ord(sorted_letters[i]) + 1 == ord(sorted_letters[i + 1]):
                        letter_scores[sorted_letters[i]] += 2
                        letter_scores[sorted_letters[i + 1]] += 2
                for letter in set(letters):
                    if letters.count(letter) > 1:
                        letter_scores[letter] += letters.count(letter)

                number_scores = defaultdict(int)
                sorted_numbers = sorted(numbers)
                for i in range(len(sorted_numbers) - 1):
                    if sorted_numbers[i] + 1 == sorted_numbers[i + 1]:
                        number_scores[sorted_numbers[i]] += 2
                        number_scores[sorted_numbers[i + 1]] += 2

                odd_even_prime = [
                    ("odd" if n % 2 else "even") if not is_prime(n) else "prime"
                    for n in numbers
                ]
                majority = max(set(odd_even_prime), key=odd_even_prime.count)
                for i, trait in enumerate(odd_even_prime):
                    if trait != majority:
                        number_scores[numbers[i]] += 10

                penalties = defaultdict(int)
                for letter in set(letters):
                    if letters.count(letter) >= 3 and (
                        not any(
                            ord(letter) + 1 == ord(next_letter)
                            for next_letter in letters
                        )
                    ):
                        for i, l in enumerate(letters):
                            if l == letter:
                                penalties[player_ids[i]] -= 5

                round_details = []
                for player_id, (letter, number) in zip(player_ids, cards):
                    letter_score = letter_scores[letter]
                    number_score = number_scores[number]
                    penalty = penalties[player_id]
                    total_score = letter_score + number_score + penalty
                    players[player_id - 1]["score"] += total_score
                    round_details.append(
                        {
                            "player_id": player_id,
                            "letter": letter,
                            "number": number,
                            "letter_score": letter_score,
                            "number_score": number_score,
                            "penalty": penalty,
                            "total_score": total_score,
                        }
                    )
                # 출력
                print(f"\n=== Turn Results ===")
                print(f"Cards: {cards}")
                for detail in round_details:
                    print(
                        f"Player {detail['player_id']} | "
                        f"Card: ({detail['letter']}, {detail['number']}) | "
                        f"Letter Score: {detail['letter_score']} | "
                        f"Number Score: {detail['number_score']} | "
                        f"Penalty: {detail['penalty']} | "
                        f"Total: {detail['total_score']}"
                    )
                print(f"Scores: {[p['score'] for p in players]}")

                # 게임 종료 조건 확인
                if any(player["score"] >= 100 for player in players):
                    game_over.set()
                    break

                # 턴 종료 후 초기화
                turn_cards.clear()


player_threads = [threading.Thread(target=player, args=(i,)) for i in range(1, 6)]
reader_thread = threading.Thread(target=reader)

for t in player_threads:
    t.start()
reader_thread.start()

for t in player_threads:
    t.join()
reader_thread.join()

print("\n=== Final Results ===")
players.sort(key=lambda x: x["score"], reverse=True)
for player in players:
    print(f"Player {player['id']}: {player['score']} points")
