
import chat_pb2, chat_pb2_grpc
from helpers.llm_functions import llm, DEFAULT_SYSTEM

messages = [
   chat_pb2.Message(
         role= "system",
         content= DEFAULT_SYSTEM
         )
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
            #print(chunk)
            print(chunk.choices[0].delta.content, end="")
        print("")


if __name__ == "__main__":
    main()