from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional, List, Dict
import json
from datetime import datetime
import asyncio
from .engine import MatchingEngine
import uuid

app = FastAPI(title="Cryptocurrency Matching Engine")

# Initializing
engine = MatchingEngine()

# storeage
market_data_connections: List[WebSocket] = []
trade_connections: List[WebSocket] = []

class OrderRequest(BaseModel):
    symbol: str
    order_type: str
    side: str
    quantity: Decimal
    price: Optional[Decimal] = None

class OrderResponse(BaseModel):
    order_id: str
    status: str
    executions: List[Dict]

@app.post("/order", response_model=OrderResponse)
async def submit_order(order: OrderRequest):
    executions = engine.submit_order(
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price
    )
    
    # we can Broadcast market data updates
    await broadcast_market_data(order.symbol)
    
    # we can Broadcast trade executions
    for maker, taker, price, quantity in executions:
        trade_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": order.symbol,
            "trade_id": f"{maker.order_id}-{taker.order_id}",
            "price": str(price),
            "quantity": str(quantity),
            "aggressor_side": taker.side,
            "maker_order_id": maker.order_id,
            "taker_order_id": taker.order_id
        }
        await broadcast_trade(trade_data)
    
    # we can Get the order ID from the taker order if there are executions, otherwise from the maker order
    order_id = executions[0][1].order_id if executions else None
    
    return OrderResponse(
        order_id=order_id or str(uuid.uuid4()),  # Generate new ID if no executions
        status="filled" if executions else "accepted",
        executions=[{
            "price": str(price),
            "quantity": str(qty),
            "maker_order_id": maker.order_id,
            "taker_order_id": taker.order_id
        } for maker, taker, price, qty in executions]
    )

@app.delete("/order/{symbol}/{order_id}")
async def cancel_order(symbol: str, order_id: str):
    success = engine.cancel_order(symbol, order_id)
    if success:
        await broadcast_market_data(symbol)
    return {"success": success}

@app.get("/bbo/{symbol}")
async def get_bbo(symbol: str):
    best_bid, best_ask = engine.get_bbo(symbol)
    return {
        "symbol": symbol,
        "best_bid": str(best_bid) if best_bid else None,
        "best_ask": str(best_ask) if best_ask else None
    }

async def broadcast_market_data(symbol: str):
    order_book = engine.get_order_book(symbol)
    best_bid, best_ask = order_book.get_bbo()
    
    market_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "asks": [[str(price), str(sum(o.quantity for o in orders))] 
                for price, orders in sorted(order_book.asks.items())[:10]],
        "bids": [[str(price), str(sum(o.quantity for o in orders))] 
                for price, orders in sorted(order_book.bids.items(), reverse=True)[:10]]
    }
    
    for connection in market_data_connections:
        try:
            await connection.send_json(market_data)
        except WebSocketDisconnect:
            market_data_connections.remove(connection)

async def broadcast_trade(trade_data: dict):
    for connection in trade_connections:
        try:
            await connection.send_json(trade_data)
        except WebSocketDisconnect:
            trade_connections.remove(connection)

@app.websocket("/ws/market-data")
async def market_data_websocket(websocket: WebSocket):
    await websocket.accept()
    market_data_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        market_data_connections.remove(websocket)

@app.websocket("/ws/trades")
async def trades_websocket(websocket: WebSocket):
    await websocket.accept()
    trade_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        trade_connections.remove(websocket) 