from redvox.cloud.api import ApiConfig

import redvox.cloud.client as cloud_client


def main():
    client: cloud_client.CloudClient
    with cloud_client.cloud_client("redvoxcore@gmail.com",
                                   "red1Core18",
                                   ApiConfig(
                                       "http",
                                       "localhost",
                                       8080
                                   ),
                                   "The_Early_Bird_Gets_The_Worm") as client:
        print(client.request_metadata_m(
            1601424000,
            1601424000 + 300,
            ["1637610001"],
            ["metadata"]
        ).db_packets[0].metadata)


if __name__ == "__main__":
    main()
