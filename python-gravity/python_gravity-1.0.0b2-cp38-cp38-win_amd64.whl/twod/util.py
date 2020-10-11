from typing import List, Optional, Tuple, Union
from pygravity import twod


__all__ = ['Body', 'BodyWithMetadata', 'capture_simulation']


class Body:
    def __init__(self, container, position, mass, has_caster=True, has_acceptor=True):
        self.position = position
        self.mass = mass
        self.physics = twod.PhysicsManager(position)
        if has_caster:
            self.caster = twod.GravityCaster(position, mass)
            container.add_caster(self.caster)
        else: self.caster = None
        if has_acceptor:
            self.acceptor = twod.GravityAcceptor(position, container, self.physics)
        else: self.acceptor = None

    def step(self, time_passed):
        res = None
        if self.acceptor is not None:
            res = self.acceptor.calculate(time_passed)
        return res, self.physics.calculate(time_passed)


class BodyWithMetadata:
    body: Body
    name: str = 'body'
    radius: float = 0
    color: Tuple[float, float, float] = (0, 0, 0)

    def __init__(self, body: Body, name: str = 'body', radius: float = 0, color: Tuple[float, float, float] = (0, 0, 0)):
        self.body = body
        self.name = name
        self.radius = radius
        self.color = color

    @staticmethod
    def ensure_metadata(body, *defaults):
        if isinstance(body, BodyWithMetadata):
            return body
        return BodyWithMetadata(body, *defaults)

    @staticmethod
    def iter_ensure_metadata(it, name_format='body%03i', *defaults):
        yield from (
            BodyWithMetadata.ensure_metadata(body, name_format % i, *defaults)
            for (i, body)
            in enumerate(it)
        )

    @staticmethod
    def strip_metadata(body):
        return BodyWithMetadata.ensure_metadata(body).body

    @staticmethod
    def iter_strip_metadata(it):
        yield from (
            BodyWithMetadata.strip_metadata(body)
            for body
            in it
        )


def capture_simulation(
        bodies: List[Union[Body, BodyWithMetadata]],
        focus: Optional[Union[Body, BodyWithMetadata]] = None,
        step_distance=36800,
        step_count=5000) -> dict:
    result = {}
    focus = BodyWithMetadata.strip_metadata(focus)

    bodies = list(BodyWithMetadata.iter_ensure_metadata(bodies))
    metadata = {}
    result['meta'] = metadata
    for body in bodies:
        body_meta_dict = {}
        result['meta'][body.name] = body_meta_dict
        body_meta_dict['mass'] = body.body.mass
        body_meta_dict['radius'] = body.radius
        body_meta_dict['color'] = body.color

    bodies.reverse()
    data = []
    result['data'] = data
    def report():
        frame = {}
        for body in bodies:
            body_frame = {}
            if focus is None:
                use_position = body.body.position
            else:
                use_position = body.body.position - focus.position
            body_frame['position'] = tuple(use_position)
            body_frame['velocity'] = tuple(body.body.physics.velocity)
            frame[body.name] = body_frame
        data.append(frame)
    report()
    for i in range(step_count):
        for body in bodies:
            body.body.step(step_distance)
        report()

    return result
