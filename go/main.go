package main

import (
	groq "desarso/photoToHtml/chat"
	"log"
	"net"

	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", ":9000")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	s := groq.NewChatServer()

	grpcServer := grpc.NewServer()

	groq.RegisterChatServer(grpcServer, s)

	log.Println("Starting gRCP Server....")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to create server: %v", err)
	}

}
