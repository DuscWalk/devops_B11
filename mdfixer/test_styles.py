"""验证四种声明风格的补丁生成与 E3 参考补丁一致。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mdfixer_core import Finding
from mdfixer_engine import parse_makefile
from mdfixer_patch import generate_patch_for_missing, make_unified_diff

FIXTURES = {
    "target": (
            "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\nmain.o: main.c unused.h\n\t$(CC) $(CFLAGS) -c $< -o $@\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                    "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\nmain.o: main.c unused.h config.h\n\t$(CC) $(CFLAGS) -c $< -o $@\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                        ),
                            "macro": (
                                    "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\nDEPS = main.c unused.h\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\nmain.o: $(DEPS)\n\t$(CC) $(CFLAGS) -c $< -o $@\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                                            "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\nDEPS = main.c unused.h config.h\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\nmain.o: $(DEPS)\n\t$(CC) $(CFLAGS) -c $< -o $@\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                                                ),
                                                    "hybrid": (
                                                            "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\nHEADERS = unused.h\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\nmain.o: main.c $(HEADERS)\n\t$(CC) $(CFLAGS) -c $< -o $@\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                                                                    "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\nHEADERS = unused.h config.h\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\nmain.o: main.c $(HEADERS)\n\t$(CC) $(CFLAGS) -c $< -o $@\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                                                                        ),
                                                                            "implicit": (
                                                                                    "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\n%.o: %.c\n\t$(CC) $(CFLAGS) -c $< -o $@\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                                                                                            "CC ?= cc\nCFLAGS = -O0 -Wall -Wextra\n\nall: app\n\napp: main.o\n\t$(CC) main.o -o app\n\n%.o: %.c\n\t$(CC) $(CFLAGS) -MMD -MP -c $< -o $@\n\n-include main.d\n\nclean:\n\trm -f app main.o main.d\n\n.PHONY: all clean\n",
                                                                                                ),
                                                                                                }


                                                                                                def main():
                                                                                                    finding = Finding(
                                                                                                            type="MISSING",
                                                                                                                    target="main.o",
                                                                                                                            dependency="config.h",
                                                                                                                                    commit="",
                                                                                                                                            detector="",
                                                                                                                                                    location={},
                                                                                                                                                            evidence={},
                                                                                                                                                                )
                                                                                                                                                                    all_ok = True
                                                                                                                                                                        for style, (before, expected_after) in FIXTURES.items():
                                                                                                                                                                                rules, variables = parse_makefile(before)
                                                                                                                                                                                        gen = generate_patch_for_missing(before, rules, variables, finding)
                                                                                                                                                                                                if gen is None:
                                                                                                                                                                                                            print(f"[FAIL] ${style}: no patch generated")
                                                                                                                                                                                                                        all_ok = False
                                                                                                                                                                                                                                    continue
                                                                                                                                                                                                                                            patched, desc = gen
                                                                                                                                                                                                                                                    if patched == expected_after:
                                                                                                                                                                                                                                                                print(f"[ OK ] ${style}: ${desc}")
                                                                                                                                                                                                                                                                        else:
                                                                                                                                                                                                                                                                                    print(f"[FAIL] ${style}: ${desc}")
                                                                                                                                                                                                                                                                                                print("--- expected ---")
                                                                                                                                                                                                                                                                                                            print(expected_after)
                                                                                                                                                                                                                                                                                                                        print("--- actual ---")
                                                                                                                                                                                                                                                                                                                                    print(patched)
                                                                                                                                                                                                                                                                                                                                                all_ok = False
                                                                                                                                                                                                                                                                                                                                                    print()
                                                                                                                                                                                                                                                                                                                                                        print("ALL PASS" if all_ok else "SOME FAILED")
                                                                                                                                                                                                                                                                                                                                                            return 0 if all_ok else 1


                                                                                                                                                                                                                                                                                                                                                            if __name__ == "__main__":
                                                                                                                                                                                                                                                                                                                                                                sys.exit(main())
                                                                                                                                                                                                                                                                                                                                                                