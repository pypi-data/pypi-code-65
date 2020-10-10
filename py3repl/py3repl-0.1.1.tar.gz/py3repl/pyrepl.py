from colorama import Fore, init

init(autoreset=True)

success = lambda input: f"{Fore.GREEN}{input}"
failure = lambda input: f"{Fore.RED}{input}"


def info() -> None:
    print()
    print(f"{Fore.GREEN}Welcome to python nano-REPL")
    print(f"{Fore.BLUE}author: Amal Shaji")
    print(f"{Fore.BLUE}repo  : https://github.com/amalshaji/pyrepl")
    print(f"{Fore.YELLOW}crtl-c to quit")
    print()


def repl() -> None:
    info()
    try:
        while True:
            try:
                _in = input(">>> ")
                try:
                    print(success(eval(_in)))
                except:
                    out = exec(_in)
                    if out != None:
                        print(success(out))
            except Exception as e:
                print(failure(f"Error: {e}"))
    except KeyboardInterrupt as e:
        print("\nExiting...")


if __name__ == "__main__":
    repl()
