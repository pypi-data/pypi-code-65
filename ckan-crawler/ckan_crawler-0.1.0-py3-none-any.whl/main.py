import toml

portal_data = toml.load("portal.toml")

def main():
    print("Portal name:", portal_data["info"]["name"])
    print("Portal url:", portal_data["info"]["url"])


if __name__=="__main__":
    main()