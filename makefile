run:
	cd ./go && go run ./main.go



compile:
	protoc --go_out=./go/chat --go_opt=paths=source_relative chat.proto
	protoc --go-grpc_out=./go/chat --go-grpc_opt=paths=source_relative chat.proto
	python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. chat.proto

