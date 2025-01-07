from dotenv import load_dotenv
import os
import grpc
import chat_pb2, chat_pb2_grpc
from typing import List, Optional

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
channel = grpc.insecure_channel("localhost:9000")
stub = chat_pb2_grpc.ChatStub(channel)

DEFAULT_SYSTEM="You are a helpful friendly assistant. Please answer clearly and concisely. You are part of a home assitant system, only use tools calls after asking the user"



class llm:

    @staticmethod
    def function(
        model: Optional[str] = "llama-3.3-70b-versatile",
        stream: Optional[bool] = False,
        messages: Optional[List[chat_pb2.Message]] =[
            chat_pb2.Message(role="system", content=DEFAULT_SYSTEM),
        ],
        **options
        ):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if messages[0].role == "system" :
                    messages[0] = chat_pb2.Message(
                        role="system", 
                        content=func.__doc__)
                else:
                    ##append to beggining of list
                    messages.insert(0, chat_pb2.Message(
                        role="system", 
                        content=func.__doc__
                        ))
                original_result = func(*args, **kwargs)
                messages.append(
                    chat_pb2.Message(
                        role="user", 
                        content=original_result)
                )
                request = chat_pb2.ChatRequest(
                    messages=messages,
                    apiKey=GROQ_API_KEY,
                    model=model
                )
                
                try:
                    if stream == True:
                        # Calling the ChatStream RPC and reading the responses
                        responses = stub.ChatStream(request)
                        return responses
                    else:
                        response = stub.Chat(request)
                        return response.choices[0].message.content

                except grpc.RpcError as e:
                    print(f"RPC failed: {e}")
                
                return "New functionality!"
            return wrapper
        return decorator

@llm.function()
def language_spoken(country):
    """Only return the actualt language name nothing else"""
    return f"What language is spoken {country}"

@llm.function(stream=True)
def poem(topic):
    """Write a long poem about the topic"""
    return f"The topic is {topic}"


messages = [
     chat_pb2.Message(role="system", content=DEFAULT_SYSTEM)
]
@llm.function(stream=True, messages=messages)
def chat(message):
    """You are a helful assistant answer the user shortly and clearly. Do anything the user tells you to do"""
    return message



def main():
    while True:
        message = input("You: ")
        chunks = chat(message)
        print("Bot: ", end="")
        for chunk in chunks:
            print(chunk.choices[0].delta.content, end="")
        print("")


if __name__ == "__main__":
    main()



