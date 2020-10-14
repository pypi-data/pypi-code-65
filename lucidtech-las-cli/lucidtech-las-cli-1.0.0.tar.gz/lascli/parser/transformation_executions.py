from las import Client


def create_transformation_execution(las_client: Client, transformation_id):
    return las_client.create_transformation_execution(transformation_id)


def create_transformation_executions_parser(subparsers):
    parser = subparsers.add_parser('transformation-executions')
    subparsers = parser.add_subparsers()

    transformation_executions_parser = subparsers.add_parser('create')
    transformation_executions_parser.add_argument('transformation_id')
    transformation_executions_parser.set_defaults(cmd=create_transformation_execution)

    return parser
