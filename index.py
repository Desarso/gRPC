import os

import chat_pb2, chat_pb2_grpc
import pyaudio
from openai import OpenAI

from faster_whisper import WhisperModel
from time import time
import queue
import sounddevice as sd
import numpy as np
import json




def greet_user_function(name):
    print(f"Hello there {name}")

def execute_tool_call(call):
    call = call.function
    function_name = getattr(call, 'name', None)
    arguments = getattr(call, 'arguments', None)  # Assuming arguments is a JSON string
    if function_name:
        # Resolve the function from a predefined mapping of available functions
        func = globals().get(function_name)
        if callable(func):
            try:
                # Parse arguments if they are a JSON string
                parsed_args = json.loads(arguments) if arguments else {}
                if isinstance(parsed_args, dict):
                    func(**parsed_args)  # Call the function with unpacked arguments
                else:
                    print(f"Invalid arguments format for function '{function_name}': {parsed_args}")
            except Exception as e:
                print(f"Error calling function '{function_name}': {e}")
        else:
            print(f"Function '{function_name}' is not callable or not defined.")
    else:
        print("Call is missing a function name.")





def main():

    channel = grpc.insecure_channel("localhost:9000")
    stub = chat_pb2_grpc.ChatStub(channel)

    messages = []
    messages = [
        chat_pb2.Message(role="system", content="You are a helpful friendly assistant. Please answer clearly and concisely. You are part of a home assitant system, only use tools calls after asking the user"),
]


    while True:
        input_message = input("User: ")
        if input_message == "exit":
            break
        messages.append(chat_pb2.Message(role="user", content=input_message))
        request = chat_pb2.ChatRequest(
            messages=messages,
            apiKey=GROQ_API_KEY,
            model="llama-3.3-70b-versatile"
        )
        try:
            # Calling the ChatStream RPC and reading the responses
            responses = stub.ChatStream(request)
            assitantMessage = chat_pb2.Message(role="assistant", content="")
            print("Assistant: ", end="")

            for response in responses:
                delta = response.choices[0].delta
                ##check if delta contains content
                if hasattr(delta, 'content') and delta.content is not None:
                    # Print in the same line
                    print(response.choices[0].delta.content, end="")
                    assitantMessage.content += response.choices[0].delta.content

                for call in delta.tool_calls: 
                    execute_tool_call(call)
                    


            
            print("")

            messages.append(assitantMessage)

        except grpc.RpcError as e:
            print(f"RPC failed: {e}")


if __name__ == "__main__":
    main()


