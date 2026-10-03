"""Homework 3 self-check. Run: python3 check_hw03.py"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _check import Checker

c = Checker("Homework 3 self-check", "hw03_starter.py")
m = c.load(__file__)
_EPV_HALF = sum((0.5 ** i) * 10 / 1.1 ** (i + 1) for i in range(3))
c.check("expected_present_value with 50% survival each year", lambda: m.expected_present_value([10, 10, 10], 0.10, 0.5), _EPV_HALF, tol=0.02)
c.check("expected_present_value with certain survival", lambda: m.expected_present_value([10, 15, 20], 0.10, 1.0), 36.51, tol=0.02)
c.check("expected_present_value with no survival past year 1", lambda: m.expected_present_value([10, 10, 10], 0.10, 0.0), 10 / 1.1, tol=0.02)
c.check("simulated P(4-sided | rolled a 1)", lambda: m.simulate_dice(200_000), 0.6, tol=0.02)
c.check("simulated three-coin expected payout", lambda: m.simulate_coins(200_000), 1.5, tol=0.02)
c.assert_true("simulate_dice is reproducible with a fixed seed", lambda: abs(m.simulate_dice(50_000, seed=1) - m.simulate_dice(50_000, seed=1)) < 1e-12)
c.assert_true("more trials gives a closer estimate", lambda: abs(m.simulate_coins(400_000, seed=3) - 1.5) <= abs(m.simulate_coins(400, seed=3) - 1.5) + 0.05)
UP, DOWN, SMALL, BIG = 0.01, -0.01, -0.005, -0.03
ALTERNATING = [UP, DOWN, UP, DOWN, UP, DOWN]
BLOCKS = [DOWN, DOWN, DOWN, DOWN, UP, UP, UP, UP]
ALL_DOWN = [DOWN, DOWN, DOWN, DOWN]
MIXED_AFTER = [BIG, UP, BIG, DOWN, UP, SMALL]
BIG_REBOUND = [BIG, UP, DOWN, DOWN, BIG, UP]
c.check("p_down on a series that alternates", lambda: m.p_down(ALTERNATING), 0.5, tol=1e-9)
c.check("p_down when every day is down", lambda: m.p_down(ALL_DOWN), 1.0, tol=1e-9)
c.check("p_down_given_down when a down day never follows a down day", lambda: m.p_down_given_down(ALTERNATING), 0.0, tol=1e-9)
c.check("p_down_given_down on four down days then four up", lambda: m.p_down_given_down(BLOCKS), 3 / 4, tol=1e-9)
c.check("p_down_given_big_drop ignores drops above the threshold", lambda: m.p_down_given_big_drop(MIXED_AFTER), 0.5, tol=1e-9)
c.check("p_down_given_big_drop is not p_down_given_down", lambda: m.p_down_given_big_drop(BIG_REBOUND), 0.0, tol=1e-9)
sys.exit(c.report())
