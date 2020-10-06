import requests, time

MOTIF_BROKER_ENDPOINT = "http://localhost:3282"
BULK_LENGTH = 50000
NB_JOKER = 15
SESSION = requests.Session()
SESSION.trust_env = False

def _default_filter(mb_res, **kwargs):
    return mb_res

def _default_transform(mb_res):
    return mb_res

def configure(motif_broker_endpoint:str):
    global MOTIF_BROKER_ENDPOINT
    MOTIF_BROKER_ENDPOINT = motif_broker_endpoint

def set_bulk_length(bulk_length:int):
    global BULK_LENGTH
    BULK_LENGTH = bulk_length

def get(list_key, filter_predicate = _default_filter, transform_predicate = _default_transform, **kwargs):
    try:
        SESSION.get(MOTIF_BROKER_ENDPOINT + "/handshake")
    except:
        raise Exception(f"Can't ping motif-broker at {MOTIF_BROKER_ENDPOINT}")

    bulk_requests = [list_key[i:i + BULK_LENGTH] for i in range(0, len(list_key), BULK_LENGTH)]

    results = {}

    for bulk in bulk_requests:
        joker = 0
        request_sliced = {"keys" : bulk}
        while True:
            try:
                raw_res = SESSION.post(MOTIF_BROKER_ENDPOINT + "/bulk_request",json=request_sliced).json()["request"]
            except Exception:
                joker += 1
                if joker > NB_JOKER:
                    raise Exception(f"Can't interrogate motif-broker at {MOTIF_BROKER_ENDPOINT} after {NB_JOKER} tries")
                time.sleep(5)
                continue
            
            filtered = filter_predicate(raw_res, **kwargs)
            transformed = transform_predicate(filtered)
            results.update(transformed)
            break

    return results
