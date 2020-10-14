from las import Client


def create_transformation(las_client: Client, transformation_type):
    return las_client.create_transformation(transformation_type)


def create_transformations_parser(subparsers):
    parser = subparsers.add_parser('transformations')
    subparsers = parser.add_subparsers()

    transformations_parser = subparsers.add_parser('create')
    transformations_parser.add_argument('transformation_type', choices={'manual', 'docker'})
    transformations_parser.set_defaults(cmd=create_transformation)

    return parser
