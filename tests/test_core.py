"""Tests for Livelingua."""
from src.core import Livelingua
def test_init(): assert Livelingua().get_stats()["ops"] == 0
def test_op(): c = Livelingua(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Livelingua(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Livelingua(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Livelingua(); r = c.process(); assert r["service"] == "livelingua"
