def main():
    import sys
    from .nhl_player import Player

    args = sys.argv
    print(args)
    if (len(args) == 1):
        print("""
          Usage: nhlapip endpoint [args]
          Example: nhlapip player 8451101 
        """)
        return(True)
    endpoint = args[1]
    ids = args[2:]

   
    if (endpoint == "player"):
        instancelist = [Player(i) for i in ids]
        instancelist = [x.get_data() for x in instancelist]
        instancelist = [print(x.data) for x in instancelist]
        return(True)
       

    

if __name__ == "__main__":
    main()
