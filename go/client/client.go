package main

import (
	"context"
	groq "desarso/photoToHtml/chat"
	"fmt"
	"log"
	"os"

	"google.golang.org/grpc"
)

func main() {
	var conn *grpc.ClientConn
	conn, err := grpc.Dial(":9000", grpc.WithInsecure())
	if err != nil {
		log.Fatalf("Could not connect: %s", err)
	}
	defer conn.Close()

	// Create a new ChatClient
	c := groq.NewChatClient(conn)

	// Call the SayHello method
	message := groq.Message{
		Role:    "user",
		Content: "Hello",
	}

	messages := []*groq.Message{&message}

	apiKey := os.Getenv("GROQ_API_KEY")
	if apiKey == "" {
		fmt.Println("Error: GROQ_API_KEY is not set")
		return
	}

	model := "llama-3.3-70b-versatile"

	chatRequest := &groq.ChatRequest{
		ApiKey:   apiKey,
		Model:    model,
		Messages: messages,
	}

	response, err := c.ChatStream(context.Background(), chatRequest)
	if err != nil {
		log.Fatalf("Error when calling SayHello: %s", err)
	}

	for {
		message, err := response.Recv()
		if err != nil {
			// If the stream has ended just output empty string
			if err.Error() == "EOF" {
				fmt.Println("")
				break
			}
			log.Fatalf("Error when calling Function: %s", err)
		}
		fmt.Print(message.Choices[0].Delta.Content)
	}
}
