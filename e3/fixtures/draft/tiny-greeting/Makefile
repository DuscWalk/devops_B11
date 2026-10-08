CC ?= cc
CFLAGS = -O0 -Wall -Wextra

all: hello

hello: main.c
	$(CC) $(CFLAGS) main.c -o hello

clean:
	rm -f hello

.PHONY: all clean
