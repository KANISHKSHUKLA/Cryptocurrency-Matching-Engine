import pytest
from decimal import Decimal
from matching_engine.engine import MatchingEngine, Order

def test_limit_order_matching():
    engine = MatchingEngine()
    symbol = "BTC-USDT"
    
    # we can Add a limit buy order
    executions = engine.submit_order(
        symbol=symbol,
        side="buy",
        order_type="limit",
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    assert len(executions) == 0  # No matches yet
    
    # we can Add a limit sell order at the same price
    executions = engine.submit_order(
        symbol=symbol,
        side="sell",
        order_type="limit",
        quantity=Decimal("0.5"),
        price=Decimal("50000.0")
    )
    assert len(executions) == 1  # Should match
    maker, taker, price, quantity = executions[0]
    assert price == Decimal("50000.0")
    assert quantity == Decimal("0.5")
    
    # we can Check remaining quantity
    best_bid, best_ask = engine.get_bbo(symbol)
    assert best_bid == Decimal("50000.0")
    assert best_ask is None

def test_market_order_matching():
    engine = MatchingEngine()
    symbol = "BTC-USDT"
    
    # we can Add a limit sell order
    engine.submit_order(
        symbol=symbol,
        side="sell",
        order_type="limit",
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    # we can Add a market buy order
    executions = engine.submit_order(
        symbol=symbol,
        side="buy",
        order_type="market",
        quantity=Decimal("0.5")
    )
    assert len(executions) == 1
    maker, taker, price, quantity = executions[0]
    assert price == Decimal("50000.0")
    assert quantity == Decimal("0.5")

def test_ioc_order():
    engine = MatchingEngine()
    symbol = "BTC-USDT"
    
    # we can Add a limit sell order
    engine.submit_order(
        symbol=symbol,
        side="sell",
        order_type="limit",
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    # we can Add an IOC buy order for more than available
    executions = engine.submit_order(
        symbol=symbol,
        side="buy",
        order_type="ioc",
        quantity=Decimal("2.0"),
        price=Decimal("50000.0")
    )
    assert len(executions) == 1
    maker, taker, price, quantity = executions[0]
    assert price == Decimal("50000.0")
    assert quantity == Decimal("1.0")  # Only matched available quantity

def test_fok_order():
    engine = MatchingEngine()
    symbol = "BTC-USDT"
    
    # Add a limit sell order
    engine.submit_order(
        symbol=symbol,
        side="sell",
        order_type="limit",
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    # we can Add a FOK buy order for more than available
    executions = engine.submit_order(
        symbol=symbol,
        side="buy",
        order_type="fok",
        quantity=Decimal("2.0"),
        price=Decimal("50000.0")
    )
    assert len(executions) == 0  # No execution as full quantity not available

def test_price_time_priority():
    engine = MatchingEngine()
    symbol = "BTC-USDT"
    
    # we can Add multiple limit sell orders at the same price
    engine.submit_order(
        symbol=symbol,
        side="sell",
        order_type="limit",
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    engine.submit_order(
        symbol=symbol,
        side="sell",
        order_type="limit",
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    # we can Add a market buy order
    executions = engine.submit_order(
        symbol=symbol,
        side="buy",
        order_type="market",
        quantity=Decimal("1.5")
    )
    assert len(executions) == 2  # Should match with both sell orders
    assert executions[0][3] == Decimal("1.0")  # First order fully filled
    assert executions[1][3] == Decimal("0.5")  # Second order partially filled

def test_cancel_order():
    engine = MatchingEngine()
    symbol = "BTC-USDT"
    
    # we can Add a limit order
    executions = engine.submit_order(
        symbol=symbol,
        side="buy",
        order_type="limit",
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    order_id = executions[0][1].order_id if executions else None
    
    # we can Cancel the order
    success = engine.cancel_order(symbol, order_id)
    assert success
    
    # we can Verify order is gone
    best_bid, best_ask = engine.get_bbo(symbol)
    assert best_bid is None
    assert best_ask is None 