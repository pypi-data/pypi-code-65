from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import util
import shortuuid

URI = "http://cap.dudaji.com"


app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("port")


class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}


class PortMap(Resource):
    def get(self):
        return util.list_portmap()

    def post(self):
        args = parser.parse_args()
        print(args)
        pod_name = args["name"]
        port = int(args["port"])
        # svc_name = "%s_%s" % (pod_name, shortuuid.uuid())
        svc_name = pod_name
        _, node_port = util.create_portmap(svc_name, pod_name, port)
        return {
            "url": f"{URI}:{node_port}",
            "serviceName": svc_name,
            "port": port,
            "nodePort": node_port
        }

    def delete(self):
        args = parser.parse_args()
        print(args)
        pod_name = args["name"]
        # svc_name = "%s_%s" % (pod_name, shortuuid.uuid())
        svc_name = pod_name
        success, _ = util.delete_portmap(svc_name)
        return {
            'success': success,
            'serviceName': svc_name,
        }


api.add_resource(HelloWorld, "/")
api.add_resource(PortMap, "/portmap")


if __name__ == "__main__":
    app.run(debug=True)
