import argparse
import sys, os
import requests


def line_notify(line_notify_token, msg, image):

    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + line_notify_token}
    payload = {'message': msg}
    if image:
        files = {"imageFile": open(image, "rb")}
    else:
        files = None
    return requests.post(line_notify_api, data=payload, headers=headers, files=files)


def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    parser = argparse.ArgumentParser(description='build ppt ')  # (1)
    parser.add_argument('-t', '--token', type=str, help='token', required=True)
    parser.add_argument('-m', '--msg', type=str, help='message', required=True)
    parser.add_argument('-f',
                        '--file',
                        type=str,
                        help='image file',
                        required=False)
    args = parser.parse_args()
    line_notify(args.token, args.msg, args.file)


if __name__ == "__main__":
    main()
