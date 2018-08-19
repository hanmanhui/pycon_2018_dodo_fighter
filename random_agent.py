#!/usr/bin/env python3.6

import json
import sys
import random

# 도도 파이터에 참가하기 위해서는 에이전트를 만들어서 제출해 주셔야 합니다.
# 에이전트는 사용자가 작성하는 인공지능 코드로서, 주어지는 현재 게임 상태를 바탕으로
# 어떤 액션을 취할지를 결정하는 역할을 합니다.
#
# 액션 설명
#  - idle - 아무것도 하지 않습니다.
#  - forward - 앞으로 움직입니다. 상대가 바로 앞에 있을 경우 더 움직이지 않습니다.
#  - backward - 뒤로 움직입니다. 처음 시작지점에서 세칸 이상 뒤로 갈 수 없습니다.
#  - punch - 상단을 공격합니다.
#  - kick - 하단을 공격합니다.
#  - crouch - 상단 공격을 피합니다.
#  - jump - 하단 공격을 피합니다.
#  - guard - 공격을 방어합니다. 상하단 모두 방어할 수 있지만 약간의 데미지를 입습니다.
#
# 상태 설명
#  - distance - 상대방과 나와의 거리. 0일 경우에만 공격이 가능합니다.
#  - time_left - 남은 시간
#  - health - 나의 체력
#  - opponent_health - 상대의 체력
#  - opponent_action - 지난 턴에서 상대의 액션
#  - given_damage - 직전 액션에서 내가 상대방에게 가한 데미지
#  - taken_damage - 직전 액션에서 상대방이 나에게 가한 데미지
#  - match_records - 지금까지의 경기 기록. 리스트 형식입니다.
#                    예를 들어 [None, True, False]인 경우, 첫번째 경기는 무승부,
#                    두번째 경기는 당신이, 세번째 경기는 상대방이 이겼다는 뜻입니다.
#
# 주의사항
#  - 같은 액션을 계속 반복하지 마세요. 공격력이 하락되는 페널티가 있습니다.
#  - 상대의 공격을 회피하거나 막는데 성공하면 다음 공격에서 공격력 보너스가 있습니다.
#  - 한 턴 내에서는 이동과 방어 동작이 공격 동작보다 우선합니다.
#    즉, P1이 공격을 하고 P2가 이동한다면 P2가 이동하는 액션을 우선 평가합니다.
#  - 사용할 수 있는 모듈은 random, json, sys, math로 한정되어 있습니다.
#  - 스크립트 실행 시간이 3초를 넘어가면 탈락 처리됩니다.


def action(what):
    if what not in ('idle', 'forward', 'backward', 'punch', 'kick',
                    'crouch', 'jump', 'guard'):
        raise ValueError(f'Unknown action type: {what}')
    sys.stdout.write(what + '\n')
    sys.stdout.flush()


def read_status():
    data = sys.stdin.readline()
    while data:
        yield json.loads(data)
        data = sys.stdin.readline()

actions = ['forward', 'backward', 'punch', 'kick', 'crouch', 'jump', 'guard']

for status in read_status():
    distance = status['distance']
    time_left = status['time_left']
    health = status['health']
    opponent_health = status['opponent_health']
    opponent_action = status['opponent_action']
    given_damage = status['given_damage']
    taken_damage = status['taken_damage']
    match_records = status['match_records']

    # 아래 코드를 수정해 주세요!
    # 주의할 점은, 한 루프 내에는 반드시 한 번의 action()만 호출되어야 합니다.
    # 호출되지 않으면 스크립트가 강제종료되며, 여러번 호출되면 큐가 쌓여서
    # 의도하지 않은 결과가 나옵니다.
    action(random.choice(actions))
