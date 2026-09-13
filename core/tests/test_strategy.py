import pytest
from core.strategy import RateLimiterStrategy

def test_cannot_instantiate_abstract_strategy():
    with pytest.raises(TypeError):
        RateLimiterStrategy()