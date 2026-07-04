import random

def hello(name):
    """打印问候语"""
    print(f"Hello, {name}!")
    print("斗地主游戏开始！")
    return "游戏已初始化"

# 调用 hello
hello('11')

pokes = {}
pokeTypes = ['●', '●', '●', '●']
pokeNumbers = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']

index = 0
for number in pokeNumbers:
    for poke_type in pokeTypes:
        pokes[index] = poke_type + number
        index += 1

pokes[52] = '小王'
pokes[53] = '大王'
print(f"牌组创建完成，共 {len(pokes)} 张牌")

keys = list(pokes.keys())
random.shuffle(keys)
print("洗牌完成")

player1_keys = keys[0:17]
player2_keys = keys[17:34]
player3_keys = keys[34:51]
bottom_keys = keys[51:54]

player1 = [pokes[k] for k in player1_keys]
player2 = [pokes[k] for k in player2_keys]
player3 = [pokes[k] for k in player3_keys]
bottom = [pokes[k] for k in bottom_keys]
print("发牌完成")

ORDER = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4, '8': 5, '9': 6,
         '10': 7, 'J': 8, 'Q': 9, 'K': 10, 'A': 11, '2': 12,
         '小王': 13, '大王': 14}

def get_rank(card):
    if card in ['小王', '大王']:
        return ORDER[card]
    return ORDER[card[1:]]

def sort_cards(cards):
    return sorted(cards, key=get_rank)

def show_cards(cards, name):
    sorted_cards = sort_cards(cards)
    print(f"\n{name} (共{len(sorted_cards)}张):")
    print(' '.join(sorted_cards))

print("\n" + "=" * 50)
print("发牌结果")
print("=" * 50)

show_cards(player1, "👤 玩家1")
show_cards(player2, "👤 玩家2")
show_cards(player3, "👤 玩家3")
show_cards(bottom, "🃏 底牌")

def hh():
    print(22)

    def hh():
        print(22)

    # 对象 dict
    # {
    #     "age": 11,
    #     "arr": [],
    #     "dict": {},
    #     "list": [],
    #     "tuple": (),
    # }