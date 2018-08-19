# -*- coding: utf-8 -*-

import argparse
import enum
import json
import random
import subprocess
import sys
import time
import typing


# 이 코드는 도도 파이터의 에이전트 코드를 로컬에서 평가하기 위한 스크립트입니다.
# 실제 도도 파이터의 데미지 계산 공식과는 차이가 있는 점을 유념해 주십시오.
#
# 사용 방법: python judge.py [1P] [2P]
# 이 때, 에이전트 스크립트는 쉘에서 직접 실행 가능한 상태여야 합니다.
#  * 스크립트의 첫 줄에 `#!/usr/bin/env python3` 가 있어야 합니다.
#  * 스크립트는 실행 권한이 있어야 합니다.


ROUND_TIME = 30
HIT_POINT_RANGE = (8, 16)
HIT_POINT_GUARD_RANGE = (4, 8)


class Action(enum.Enum):
    idle = 'idle'
    forward = 'forward'
    backward = 'backward'
    punch = 'punch'
    kick = 'kick'
    crouch = 'crouch'
    jump = 'jump'
    guard = 'guard'


class Player:
    def __init__(self, prochandle: subprocess.Popen, p_file: str, position: int):
        self.prochandle = prochandle
        self.health = 100
        self.last_action = None
        self.last_inflicted_damage = 0
        self.position = position
        self.p_file = p_file

    def distance(self, opponent):
        return abs(opponent.position - self.position)

    def communicate(self, opponent, time_left: int) -> Action:
        payload = {
            'distance': self.distance(opponent),
            'time_left': time_left,
            'health': self.health,
            'opponent_health': opponent.health,
            'opponent_action': str(opponent.last_action),
            'given_damage': self.last_inflicted_damage,
            'taken_damage': opponent.last_inflicted_damage,
            'match_records': [],
        }
        self.prochandle.stdin.write(json.dumps(payload).encode('utf-8'))
        self.prochandle.stdin.write(b'\n')
        self.prochandle.stdin.flush()
        act = self.prochandle.stdout.readline().decode('utf-8').strip()
        self.last_action = Action(act)
        return self.last_action

    def inflict_damage(self, opponent, damage: int):
        opponent.health = max(0, opponent.health - damage)
        self.last_inflicted_damage = damage

    def __repr__(self) -> str:
        return f'<Player position={self.position} health={self.health} action={self.last_action} damage={self.last_inflicted_damage}>'  # noqa


def log(time: int, player: Player, action: Action, message: str):
    # print(f'{time} [{player.health}] [{action}] {message}')
    pass


def fight_loop(p1, p2):
    time_left = ROUND_TIME
    while time_left >= 0:
        try:
            p1a = p1.communicate(p2, time_left)
        except:
            print('Invalid communication from p1. Assuming that p2 has won.')
            raise
            return p2
        try:
            p2a = p2.communicate(p1, time_left)
        except:
            print('Invalid communication from p2. Assuming that p1 has won.')
            raise
            return p1
        p1.last_inflicted_damage = 0
        p2.last_inflicted_damage = 0
        p1_idle = True
        p2_idle = True
        if p1a is Action.forward:
            if p2.position > p1.position:
                p1.position += 1
                log(time_left, p1, p1a, 'P1은 앞으로 움직였다!')
            else:
                log(time_left, p1, p1a, 'P1은 앞으로 움직이려 했지만 더 갈 수 없다!')
            p1_idle = False
        elif p1a is Action.backward:
            if p1.position >= -2:
                p1.position -= 1
            log(time_left, p1, p1a, 'P1은 뒤로 움직였다!')
            p1_idle = False
        if p2a is Action.forward:
            if p2.position > p1.position:
                p2.position -= 1
                log(time_left, p2, p2a, 'P2는 앞으로 움직였다!')
            else:
                log(time_left, p2, p2a, 'P2는 앞으로 움직이려 했지만 더 갈 수 없다!')
            p2_idle = False
        elif p2a is Action.backward:
            if p2.position <= 5:
                p2.position += 1
            log(time_left, p2, p2a, 'P2는 뒤로 움직였다!')
            p2_idle = False
        if p1a is Action.punch:
            if p1.distance(p2) > 0:
                log(time_left, p1, p1a, 'P1의 펀치! 하지만 닿지 않는다!')
            elif p2a is Action.crouch:
                log(time_left, p2, p2a, 'P2는 숙였다!')
                log(time_left, p1, p1a, 'P1의 펀치! 하지만 P2는 숙여서 피했다!')
            elif p2a is Action.guard:
                log(time_left, p2, p2a, 'P2는 가드를 올렸다!')
                log(time_left, p1, p1a, 'P1의 펀치! 약간의 데미지를 주었다!')
                p1.inflict_damage(p2, random.randrange(*HIT_POINT_GUARD_RANGE))
            else:
                log(time_left, p1, p1a, 'P1의 펀치! 아프다!')
                p1.inflict_damage(p2, random.randrange(*HIT_POINT_RANGE))
            p1_idle = False
        elif p1a is Action.kick:
            if p1.distance(p2) > 0:
                log(time_left, p1, p1a, 'P1의 발차기! 하지만 닿지 않는다!')
            elif p2a is Action.jump:
                log(time_left, p2, p2a, 'P2의 점프!')
                log(time_left, p1, p1a, 'P1의 발차기! 하지만 P2는 점프해서 피했다!')
            elif p2a is Action.guard:
                log(time_left, p2, p2a, 'P2는 가드를 올렸다!')
                log(time_left, p1, p1a, 'P1의 발차기! 약간의 데미지를 주었다!')
                p1.inflict_damage(p2, random.randrange(*HIT_POINT_GUARD_RANGE))
            else:
                log(time_left, p1, p1a, 'P1의 발차기! 아프다!')
                p1.inflict_damage(p2, random.randrange(*HIT_POINT_RANGE))
            p1_idle = False
        if p2.health <= 0:
            # print('KO. P1 승리!')
            return p1
        if p2a is Action.punch:
            if p2.distance(p1) > 0:
                log(time_left, p2, p2a, 'P2의 펀치! 하지만 닿지 않는다!')
            elif p1a is Action.crouch:
                log(time_left, p1, p1a, 'P1은 숙였다!')
                log(time_left, p2, p2a, 'P2의 펀치! 하지만 P1은 숙여서 피했다!')
            elif p1a is Action.guard:
                log(time_left, p2, p2a, 'P1은 가드를 올렸다!')
                log(time_left, p1, p1a, 'P2의 펀치! 약간의 데미지를 주었다!')
                p2.inflict_damage(p1, random.randrange(*HIT_POINT_GUARD_RANGE))
            else:
                log(time_left, p2, p2a, 'P1의 펀치! 아프다!')
                p2.inflict_damage(p1, random.randrange(*HIT_POINT_RANGE))
            p2_idle = False
        elif p2a is Action.kick:
            if p2.distance(p1) > 0:
                log(time_left, p2, p2a, 'P2의 발차기! 하지만 닿지 않는다!')
            elif p1a is Action.jump:
                log(time_left, p1, p1a, 'P1의 점프!')
                log(time_left, p2, p2a, 'P2의 발차기! 하지만 P1은 점프해서 피했다!')
            elif p1a is Action.guard:
                log(time_left, p1, p1a, 'P1는 가드를 올렸다!')
                log(time_left, p2, p2a, 'P2의 발차기! 약간의 데미지를 주었다!')
                p2.inflict_damage(p1, random.randrange(*HIT_POINT_GUARD_RANGE))
            else:
                log(time_left, p2, p2a, 'P2의 발차기! 아프다!')
                p2.inflict_damage(p1, random.randrange(*HIT_POINT_RANGE))
            p2_idle = False
        if p1.health <= 0:
            # print('KO. P2 승리!')
            return p2
        if p1_idle:
            log(time_left, p1, p1a, '아무 일도 없었다.')
        if p2_idle:
            log(time_left, p2, p2a, '아무 일도 없었다.')
        time_left -= 1
    if p1.health == p2.health:
        # print('무승부!')
        return None
    elif p1.health > p2.health:
        # print('타임 오버. P1 승리!')
        return p1
    else:
        # print('타임 오버. P2 승리!')
        return p2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('p1', type=str)
    parser.add_argument('p2', type=str)
    args = parser.parse_args()
    p1 = subprocess.Popen([args.p1],
                          stdout=subprocess.PIPE,
                          stdin=subprocess.PIPE)
    p2 = subprocess.Popen([args.p2],
                          stdout=subprocess.PIPE,
                          stdin=subprocess.PIPE)
    try:
        winner = fight_loop(Player(p1, args.p1, 0), Player(p2, args.p2, 3))
    except KeyboardInterrupt:
        p1.terminate()
        p2.terminate()


def try_mult(N=100):
    parser = argparse.ArgumentParser()
    parser.add_argument('p1', type=str)
    parser.add_argument('p2', type=str)
    args = parser.parse_args()
    winners = {}
    winners[args.p1] = 0
    winners[args.p2] = 0
    winners[None] = 0
    for k in range(N):
        p1 = subprocess.Popen([args.p1],
                              stdout=subprocess.PIPE,
                              stdin=subprocess.PIPE)
        p2 = subprocess.Popen([args.p2],
                              stdout=subprocess.PIPE,
                              stdin=subprocess.PIPE)
        try:
            winner = fight_loop(Player(p1, args.p1, 0), Player(p2, args.p2, 3))
            if winner:
                winners[winner.p_file] += 1
            else:
                winners[None] += 1
        except KeyboardInterrupt:
            p1.terminate()
            p2.terminate()
    print(winners)


if __name__ == '__main__':
    # main()
    try_mult(500)
