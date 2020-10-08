from aiohttp import web
from aiohttp_cors import CorsViewMixin
import asyncpg

from .schemas import prox_schema
from .views import paginate_query
from ..config import CONFIG

THE_QUERY = \
"""
SELECT DISTINCT ON (upper.tag_id) coalesce(anchor_dist, distance_cm) as distance,
                                zones.name as zone_name,
                                tags.name as tag_name,
                                tags.type as tag_type,
                                tags.last_seen as last_seen,
                                upper.anchor_id, upper.tag_id, upper.zone_id from log upper
LEFT JOIN zones on zones.id = upper.zone_id
LEFT JOIN (SELECT * FROM tags t) tags on tags.id = upper.tag_id
WHERE ts > tags.last_seen - interval '1min'
ORDER BY upper.tag_id, distance, upper.ts DESC
"""

THE_TYPE_QUERY = \
"""
SELECT DISTINCT ON (upper.tag_id) coalesce(anchor_dist, distance_cm) as distance,
                                zones.name as zone_name,
                                tags.name as tag_name,
                                tags.type as tag_type,
                                tags.last_seen as last_seen,
                                upper.anchor_id, upper.tag_id, upper.zone_id from log upper
LEFT JOIN zones on zones.id = upper.zone_id
LEFT JOIN (SELECT * FROM tags t) tags on tags.id = upper.tag_id
WHERE ts > tags.last_seen - interval '1min' AND tags.type = $1
ORDER BY upper.tag_id, distance, upper.ts DESC
"""

THE_GROUP_QUERY = \
"""
SELECT DISTINCT ON (upper.tag_id) coalesce(anchor_dist, distance_cm) as distance,
                                zones.name as zone_name,
                                tags.name as tag_name,
                                tags.type as tag_type,
                                tags.last_seen as last_seen,
                                upper.anchor_id, upper.tag_id, upper.zone_id from log upper
LEFT JOIN zones on zones.id = upper.zone_id
LEFT JOIN (SELECT * FROM tags t) tags on tags.id = upper.tag_id
WHERE ts > tags.last_seen - interval '1min' AND tags.group_id = $1
ORDER BY upper.tag_id, distance, upper.ts DESC
"""
# """SELECT zones.name as zone_name, tags.name as tag_name, a.*
# FROM (SELECT log.tag_id, zone_id, anchor_dist as distance, log.ts, anchor_id from log
#     JOIN (SELECT tag_id, max(ts) max_ts from log WHERE anchor_id IS NOT NULL GROUP BY tag_id) temp
#         ON log.tag_id = temp.tag_id AND log.ts = temp.max_ts
# UNION SELECT DISTINCT ON (log.tag_id) log.tag_id, zone_id, distance_cm as distance, log.ts, anchor_id from log
#     JOIN (SELECT tag_id, min(distance_cm), ts from log
#           WHERE anchor_id IS NULL and ts > ((now() at time zone 'utc') - interval '1 min') GROUP BY tag_id, ts ORDER BY ts DESC) temp
#     ON log.tag_id = temp.tag_id AND log.ts = temp.ts) a
# LEFT JOIN zones on zone_id = zones.id
# LEFT JOIN tags on tag_id = tags.id"""


def process_prox_results(results):
    output = []
    for r in results:
        anchor_id = r['anchor_id']
        zone_id = r['zone_id']
        d_r = dict(r)
        d_r['links'] = {
            "anchor": f"/api/tags/{anchor_id}" if anchor_id else None,
            "zone": f"/api/zones/{zone_id}" if zone_id else None,
            "tag": f"/api/tags/{r['tag_id']}"
        }
        output.append(d_r)
    return output


class ProximityView(web.View, CorsViewMixin):
    async def get(self):
        if 'type' in self.request.query:
            t = self.request.query['type']
            query = (THE_TYPE_QUERY, t)
        elif 'group_id' in self.request.query:
            g = self.request.query['group_id']
            try:
                query = (THE_GROUP_QUERY, int(g))
            except ValueError:
                raise web.HTTPBadRequest(text='Invalid group id')
        else:
            query = (THE_QUERY,)
        query = paginate_query(self.request, query)
        async with self.request.app['db_pool'].acquire() as conn:
            try:
                results = await conn.fetch(*query)
                print(process_prox_results(results))
            except asyncpg.exceptions.InvalidTextRepresentationError:
                raise web.HTTPBadRequest(text='Bad tag type in query')
            return web.json_response(prox_schema.dump(process_prox_results(results)))
