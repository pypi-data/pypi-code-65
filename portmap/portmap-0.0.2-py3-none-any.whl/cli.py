import fire
import logging
import shortuuid
from portmap import util
from terminaltables import AsciiTable


logging.basicConfig(level=logging.INFO)


URL = "http://cap.dudaji.com"


class Command(object):
    def show(self):
        raw = util.list_portmap_raw()
        l1 = [(x.metadata.name,
              x.spec.ports[0].port,
              x.spec.selector)
             for x in raw.items]
        pod_name = util.get_hostname()
        ns = util.get_my_ns()
        key = "statefulset.kubernetes.io/pod-name"
        l2 = [[f"{URL}/app/{ns}/{x[0]}", x[0], x[1], "mine"] for x in l1 
                if key in x[2] and pod_name == x[2][key]]
        l3 = [[f"{URL}/app/{ns}/{x[0]}", x[0], x[1], "others"] for x in l1 
                if key in x[2] and pod_name != x[2][key]]
        table = AsciiTable([["URI", "prefix", "port", "owner"]] + l2 + l3)
        print(table.table)

    def create(self, relative_prefix, port):
        success, prefix = util.create_portmap(relative_prefix, port)
        logging.info(f"Try: {URL}{prefix}")

    def delete(self, prefix):
        util.delete_portmap_by_prefix(prefix)


def main():
    fire.Fire(Command)


if __name__ == "__main__":
    main()