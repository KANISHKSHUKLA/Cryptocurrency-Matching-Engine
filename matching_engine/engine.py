from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # "buy" or "sell"
    order_type: str  # "market", "limit", "ioc", "fok"
    quantity: Decimal
    price: Optional[Decimal]
    timestamp: datetime

class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: Dict[Decimal, List[Order]] = {}  # price -> list of orders
        self.asks: Dict[Decimal, List[Order]] = {}  # price -> list of orders
        self.order_map: Dict[str, Order] = {}  # order_id -> order

    def get_bbo(self) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Get Best Bid and Offer"""
        best_bid = max(self.bids.keys()) if self.bids else None
        best_ask = min(self.asks.keys()) if self.asks else None
        return best_bid, best_ask

    def add_order(self, order: Order) -> List[Tuple[Order, Order, Decimal, Decimal]]:
        """
        Add an order to the book and return list of executions
        Returns: List of (maker_order, taker_order, price, quantity) tuples
        """
        executions = []
        
        if order.side == "buy":
            # Try to match against asks
            while order.quantity > 0 and self.asks:
                best_ask = min(self.asks.keys())
                if order.order_type == "limit" and order.price < best_ask:
                    break
                
                matching_orders = self.asks[best_ask]
                for maker_order in matching_orders:
                    if order.quantity <= 0:
                        break
                    
                    execution_qty = min(order.quantity, maker_order.quantity)
                    executions.append((maker_order, order, best_ask, execution_qty))
                    
                    maker_order.quantity -= execution_qty
                    order.quantity -= execution_qty
                    
                    if maker_order.quantity <= 0:
                        self.order_map.pop(maker_order.order_id)
                
                # we can Clean up empty price levels
                self.asks[best_ask] = [o for o in matching_orders if o.quantity > 0]
                if not self.asks[best_ask]:
                    del self.asks[best_ask]
                
                if order.order_type in ["ioc", "fok"] and order.quantity > 0:
                    return executions
                
        else:  # sell
            # we can Try to match against bids
            while order.quantity > 0 and self.bids:
                best_bid = max(self.bids.keys())
                if order.order_type == "limit" and order.price > best_bid:
                    break
                
                matching_orders = self.bids[best_bid]
                for maker_order in matching_orders:
                    if order.quantity <= 0:
                        break
                    
                    execution_qty = min(order.quantity, maker_order.quantity)
                    executions.append((maker_order, order, best_bid, execution_qty))
                    
                    maker_order.quantity -= execution_qty
                    order.quantity -= execution_qty
                    
                    if maker_order.quantity <= 0:
                        self.order_map.pop(maker_order.order_id)
                
                # we can Clean up empty price levels
                self.bids[best_bid] = [o for o in matching_orders if o.quantity > 0]
                if not self.bids[best_bid]:
                    del self.bids[best_bid]
                
                if order.order_type in ["ioc", "fok"] and order.quantity > 0:
                    return executions
        
        # we can If order still has quantity and is a limit order, add to book
        if order.quantity > 0 and order.order_type == "limit":
            if order.side == "buy":
                if order.price not in self.bids:
                    self.bids[order.price] = []
                self.bids[order.price].append(order)
            else:
                if order.price not in self.asks:
                    self.asks[order.price] = []
                self.asks[order.price].append(order)
            self.order_map[order.order_id] = order
        
        return executions

    def cancel_order(self, order_id: str) -> bool:
        """we can Cancel an order from the book"""
        if order_id not in self.order_map:
            return False
        
        order = self.order_map[order_id]
        if order.side == "buy":
            orders = self.bids.get(order.price, [])
            orders = [o for o in orders if o.order_id != order_id]
            if orders:
                self.bids[order.price] = orders
            else:
                del self.bids[order.price]
        else:
            orders = self.asks.get(order.price, [])
            orders = [o for o in orders if o.order_id != order_id]
            if orders:
                self.asks[order.price] = orders
            else:
                del self.asks[order.price]
        
        del self.order_map[order_id]
        return True

class MatchingEngine:
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
    
    def get_order_book(self, symbol: str) -> OrderBook:
        if symbol not in self.order_books:
            self.order_books[symbol] = OrderBook(symbol)
        return self.order_books[symbol]
    
    def submit_order(self, symbol: str, side: str, order_type: str, 
                    quantity: Decimal, price: Optional[Decimal] = None) -> List[Tuple[Order, Order, Decimal, Decimal]]:
        """we can Submit a new order to the matching engine"""
        order = Order(
            order_id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            timestamp=datetime.utcnow()
        )
        
        order_book = self.get_order_book(symbol)
        return order_book.add_order(order)
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """we can Cancel an existing order"""
        order_book = self.get_order_book(symbol)
        return order_book.cancel_order(order_id)
    
    def get_bbo(self, symbol: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """we can Get Best Bid and Offer for a symbol"""
        order_book = self.get_order_book(symbol)
        return order_book.get_bbo() 