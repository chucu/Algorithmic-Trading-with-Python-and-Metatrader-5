


#Author:  @dreso_fx (telegram)
#github repo: https://github.com/dreso/Algorithmic-Trading-with-Python-and-Metatrader-5
#donate BTC bc1qg2jkt802d2q3e66h760t2krsz7k6lx6ka6qz9j  xD


from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import MetaTrader5 as mt5
import time
import random


#           CONEXIÓN A LA TERMINAL MT5

# conectamos con MetaTrader 5 -> Introduce tu path(str), login (int), password (str) y server (str). Son los mismos que en la terminal de Metatrader 5
if not mt5.initialize(path="C:/Program Files/Darwinex MetaTrader 5/terminal64.exe",login=*********,password="********",server="demoUK-mt5.darwinex.com"):
    print("initialize() failed")

# solicitamos el estado y los parámetros de conexión
print(mt5.terminal_info())

# obtenemos la información sobre la versión de MetaTrader 5
print(mt5.version())


#           PARÁMETROS INICIALES
symbol = "EURUSD"
lot = 0.01
point = mt5.symbol_info(symbol).point
sl_buy = 100
tp_buy = 100
sl_sell = 100
tp_sell = 100
deviation = 5


#           FUNCIONES AUXILIARES

# Declaraciones globales
result_order_buy = None
result_order_sell = None

# Abrir una posición en largo (compra)
def open_buy():
    global result_order_buy
    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()

    # prepare the buy request structure
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        quit()

    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, exit",symbol)
            mt5.shutdown()
            quit()
    price = mt5.symbol_info_tick(symbol).ask
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - sl_buy * point,
        "tp": price + tp_buy * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # send a trading request
    result = mt5.order_send(request)

    # check the execution result
    print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation))
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field,result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
        print("shutdown() and quit")
        mt5.shutdown()
        quit()
    print("2. order_send done, ", result)
    print("   buy opened position with POSITION_TICKET={}".format(result.order))
    result_order_buy=result.order
    return(result_order_buy)

# Abrir una posición en corto (vende)
def open_sell():
    global result_order_sell
    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()

    # prepare the buy request structure
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
        quit()

    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, exit",symbol)
            mt5.shutdown()
            quit()

    lot = 0.01
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).bid
    deviation = 5
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price + sl_sell * point,
        "tp": price - tp_sell * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # send a trading request
    result = mt5.order_send(request)

    # check the execution result
    print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation))
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field,result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
        print("shutdown() and quit")
        mt5.shutdown()
        quit()

    print("2. order_send done, ", result)
    print("   sell opened position with POSITION_TICKET={}".format(result.order))
    result_order_sell=result.order
    return(result_order_sell)

# Cierra una posición de largo (vende)
def close_buy(res_order_buy):
    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()
    
    # create a close request
    position_id=res_order_buy
    price=mt5.symbol_info_tick(symbol).bid
    deviation=5
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    # send a trading request
    result=mt5.order_send(request)
    # check the execution result
    print("3. close buy position #{}: sell {} {} lots at {} with deviation={} points".format(position_id,symbol,lot,price,deviation))
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("4. order_send failed, retcode={}".format(result.retcode))
        print("   result",result)
    else:
        print("4. position #{} closed, {}".format(position_id,result))
        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field,result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
    # shut down connection to the MetaTrader 5 terminal
    #mt5.shutdown()
    positions = 0
    result_order_buy=None

# Cierra una posición de corto (compra)
def close_sell(res_order_sell):
    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
        quit()
    # create a close request
    position_id=res_order_sell
    price=mt5.symbol_info_tick(symbol).ask
    deviation=5
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    # send a trading request
    result=mt5.order_send(request)
    # check the execution result
    print("3. close sell position #{}: buy {} {} lots at {} with deviation={} points".format(position_id,symbol,lot,price,deviation))
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("4. order_send failed, retcode={}".format(result.retcode))
        print("   result",result)
    else:
        print("4. position #{} closed, {}".format(position_id,result))
        # request the result as a dictionary and display it element by element
        result_dict=result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field,result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field=="request":
                traderequest_dict=result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
    # shut down connection to the MetaTrader 5 terminal
    #mt5.shutdown()
    positions = 0
    result_order_buy=None

# Averigua si la última posición es de compra o de venta
#def classify_positions():


#          LÓGICA ESTRATEGIA

#Esto se ejecuta hasta el infinito o hasta que el usuario cancela el programa, lo suyo sería mejorarlo con una función tipo OnTick()
#last_tick=mt5.symbol_info_tick(symbol).time
while 1>0:
    #declaraciones locales
    positions=mt5.positions_total()
    random_number=random.uniform(0,1)

    #abrimos largo
    if positions == 0:
        if random_number >0.5:   #aquí tu estrategia
            open_buy()

    #abrimos corto
    if positions == 0:
        if random_number <0.5:    #aquí tu estrategia
            open_sell()

    #cerramos posiciones
    if positions != 0:
        #cerramos largo
        if result_order_buy != None:
            time.sleep(10)   #aquí tu estrategia
            close_buy(result_order_buy)

        #cerramos corto
        if result_order_sell != None:  
            time.sleep(10) #aquí tu estrategia
            close_sell(result_order_sell)

