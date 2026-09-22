CC ?= cc
CFLAGS ?= -Wall -Wextra -O0

all: app

app: app.o
	$(CC) -o $@ $^

app.o: app.c legacy.h
	$(CC) $(CFLAGS) -c -o $@ app.c

test: app
	@test "$$(./app)" = "7"

clean:
	rm -f app app.o

.PHONY: all test clean
