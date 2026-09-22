# 示例 Makefile — 用于演示 MDFixer 修复 MISSING 依赖
# 目标 app 缺失 utils.o 和 config.o 依赖

CC = gcc
CFLAGS = -Wall -O2

all: app

app: main.o legacy.o
	$(CC) $(CFLAGS) -o app main.o legacy.o

main.o: main.c
	$(CC) $(CFLAGS) -c main.c

utils.o: utils.c utils.h
	$(CC) $(CFLAGS) -c utils.c

config.o: config.c config.h
	$(CC) $(CFLAGS) -c config.c

legacy.o: legacy.c
	$(CC) $(CFLAGS) -c legacy.c

clean:
	rm -f *.o app

.PHONY: all clean test

test:
	@echo "running tests..."
	@./app --self-test
