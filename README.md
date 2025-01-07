# gRPC Project

## Overview

This project demonstrates the use of gRPC for building efficient and scalable APIs. It includes examples of defining protobuf messages, generating Go and Python code from `.proto` files, and implementing gRPC clients and servers.

## Features

- Define protobuf messages and services
- Generate Go and Python code from `.proto` files
- Implement gRPC clients and servers
- Handle different message types using `oneof`
- Custom JSON serialization for gRPC messages

## Installation

### Prerequisites

- Go (version 1.16 or higher)
- Python (version 3.6 or higher)
- Protocol Buffers compiler (`protoc`)
- gRPC plugins for Go and Python

### Steps

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/grpc-project.git
    cd grpc-project
    ```

2. Install Go dependencies:

    ```sh
    go mod tidy
    ```

3. Install Python dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Generate Go and Python code from `.proto` files:

    ```sh
    protoc --go_out=. --go-grpc_out=. proto/chat.proto
    protoc --python_out=. --grpc_python_out=. proto/chat.proto
    ```

## Usage

### Running the Server

To run the gRPC server, execute the following command:

```sh
go run server.go
```


### Running the Client

To run the gRPC client, execute the following command:

```sh
go run client.go
```

### Example Python Client

To run the Python client, execute the following command:

```sh
python client.py
```

## Project Structure

```
grpc-project/
├── proto/
│   └── chat.proto
├── go/
│   ├── chat/
│   │   ├── chat.pb.go
│   │   ├── chat_grpc.pb.go
│   ├── client.go
│   ├── server.go
├── python/
│   ├── chat_pb2.py
│   ├── chat_pb2_grpc.py
│   ├── client.py
├── README.md
├── requirements.txt
```

