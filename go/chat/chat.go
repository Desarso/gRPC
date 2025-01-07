package groq

import (
	context "context"
	"encoding/json"
	"fmt"
	"strings"

	"google.golang.org/grpc"
)

// implement the ChatServer interface
// Define the ChatServer struct and embed UnimplementedChatServer
type ChatServerImpl struct {
	UnimplementedChatServer // Embedding the unimplemented server for forward compatibility
}

func NewChatServer() *ChatServerImpl {
	return &ChatServerImpl{}
}

// mustEmbedUnimplementedChatServer satisfies the interface requirement
func (s *ChatServerImpl) mustEmbedUnimplementedChatServer() {
	// This method is intentionally empty as the embedding of UnimplementedChatServer
	// satisfies the requirement
}

func (s *ChatServerImpl) ChatStream(chatRequest *ChatRequest, stream grpc.ServerStreamingServer[ResponseData]) error {
	messages := make([]Message, len(chatRequest.Messages))
	for i, msg := range chatRequest.Messages {
		messages[i] = *msg
	}
	chunks, errs := chatStream(chatRequest.ApiKey, chatRequest.Model, messages)

	for {
		select {
		case chunk, ok := <-chunks:
			if !ok {
				chunks = nil // Close the chunks channel when done
				return nil
			} else if strings.HasPrefix(chunk, "data:") {
				//if message is data: [DONE] then break the loop
				if strings.Contains(chunk, "data: [DONE]") {
					fmt.Println("")
					break
				} else {
					var response ResponseData
					response.Choices = []*Choice{}
					chunk = strings.TrimPrefix(chunk, "data:")
					err := json.Unmarshal([]byte(chunk), &response)
					if err != nil {
						fmt.Println("Error unmarshaling data:", err)
						return err
					}
					fmt.Println("Response:", response.Choices[0].Delta)

					if err := stream.Send(&response); err != nil {
						return err
					}
				}

			}
		case err := <-errs:
			if err != nil {
				fmt.Println("Error:", err)
			}
			return err
		}
	}

}

func (s *ChatServerImpl) Chat(ctx context.Context, chatRequest *ChatRequest) (*ResponseData, error) {
	messages := make([]Message, len(chatRequest.Messages))
	for i, msg := range chatRequest.Messages {
		messages[i] = *msg
	}
	response, err := chat(chatRequest.ApiKey, chatRequest.Model, messages)
	if err != nil {
		return nil, err
	}
	return response, nil
}
