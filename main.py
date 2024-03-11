#! import requirements
import json
from openai import OpenAI
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf


api_key = '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'

client = OpenAI(api_key=api_key)

def get_stock_price(ticker):
    return str(yf.Ticker(ticker).history(period="1m").iloc[-1].Close)


def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1m").Close
    return str(data.rolling(window=window).mean().iloc[-1])


def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1m").Close
    return str(data.ewm(span=window, adjust=False).mean().iloc[-1])


def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period="1m").Close
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=14 - 1, adjust=False).mean()
    ema_down = down.ewm(com=14 - 1, adjust=False).mean()
    rs = ema_up / ema_down
    return str(100 - (100 / (1 + rs)).iloc[-1])


def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period="1m").Close
    short_EMA = data.ewm(span=12, adjust=False).mean()
    long_EMA = data.ewm(span=26, adjust=False).mean()

    MACD = short_EMA - long_EMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    MACD_histogram = MACD - signal

    return f"{MACD[-1]} , {signal[-1]} , {MACD_histogram[-1]}"


def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period="1y")
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.Close)
    plt.title(f"{ticker} Stock Price Over Last Year")
    plt.xlabel("Date")
    plt.ylabel("Stock Price ($)")
    plt.grid(True)
    plt.savefig("stock.png")
    plt.close()


functions = [
    {
        "name": "get_stock_price",
        "description": "Gets the latest stock price given ticker symbol of a company.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol for a company(for example AAPL for Apple).",
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "calculate_SMA",
        "description": "Calculates the simple moving average for a given stock ticker and a window.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for a company(for example => APPL for Apple)",
                },
                "window": {
                    "type": "integer",
                    "description": "The timeframe to consider when calculating the SMA",
                },
            },
            "required": ["ticker", "window"],
        },
    },
    {
        "name": "calculate_EMA",
        "description": "Calculates the simple moving average for a given stock ticker and a window.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for a company(for example => APPL for Apple)",
                },
                "window": {
                    "type": "integer",
                    "description": "The timeframe to consider when calculating the SMA",
                },
            },
            "required": ["ticker", "window"],
        },
    },
    {
        "name": "calculate_RSI",
        "description": "Calculates the RSI  for a given stock ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for a company(for example => APPL for Apple)",
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "calculate_MACD",
        "description": "Calculates the MACD   for a given stock ticker and a long window.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for a company(for example => APPL for Apple)",
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "calculate_MACD",
        "description": "Calculates the MACD   for a given stock ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for a company(for example => APPL for Apple)",
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "plot_stock_price",
        "description": "Plot the stock price for the last month given the ticker symbol for a company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The ticker symbol for a company(for example => APPL for Apple)",
                },
            },
            "required": ["ticker"],
        },
    },
]
avaliable_functions = {
    "get_stock_price": get_stock_price,
    "calculate_SMA": calculate_SMA,
    "calculate_EMA": calculate_EMA,
    "calculate_RSI": calculate_RSI,
    "calculate_MACD": calculate_MACD,
    "plot_stock_price": plot_stock_price,
}
if "messages" not in st.session_state:
    st.session_state["messages"] = []

#! web application for st

st.title("Stock Analysis Chatbot Assistant")
user_input = st.text_input("Your Input : ")

if user_input:
    try:
        st.session_state["messages"].append(
            {"role": "user", "content": f"{user_input}"}
        )
        response = client.chat.completions.create(model="gpt-3.5-turbo-0613",
        messages=st.session_state["messages"],
        functions=functions,
        function_call="auto")
        response_message = response.choices[0].message
        if response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            if function_name in [
                "get_stock_price",
                "calculate_RSI",
                "calculate_MACD",
                "plot_stock_price",
            ]:
                args_dict = {"ticker": function_args.get("ticker")}
            elif function_name in ["calculate_SMA", "calculate_EMA"]:
                args_dict = {
                    "ticker": function_args.get("ticker"),
                    "window": function_args.get("window"),
                }

            function_to_call = avaliable_functions[function_name]
            function_response = function_to_call(**args_dict)

            if function_name == "plot_stock_price":
                st.image("stock.png")
            else:
                st.session_state["messages"].append(response_message)
                st.session_state["messages"].append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )
                second_response = client.chat.completions.create(model="gpt-3.5-turbo-0613",
                messages=st.session_state["messages"])
                st.text(second_response.choices[0].message.content)
                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": second_response.choices[0].message.content,
                    }
                )
        else:
            st.text(response_message.content)
            st.session_state["messages"].append(
                {"role": "assistant", "content": response_message.content}
            )
    except Exception as e:
        st.error(f"An error occurred: {e}")
