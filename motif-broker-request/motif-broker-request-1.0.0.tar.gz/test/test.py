import motif_broker_request.request as mb_request

def filter_genomes(mb_res, **kwargs):
    if not "genomes" in kwargs:
        raise Exception("you must provide 'genomes' argument to get function for filter_genomes function")
    genomes = kwargs["genomes"]

    filtered_results = {}
    for sgrna in mb_res: 
        added = False 
        for org in mb_res[sgrna]:
            if org in genomes:
                if added:
                    filtered_results[sgrna][org] = mb_res[sgrna][org]
                else:
                    filtered_results[sgrna] = {org : mb_res[sgrna][org]}
    
    return filtered_results

def transform(mb_res):
    return mb_res

sgrnas = ["AAAAAAAAAAAAAAAAAAATGGG", "TCCAAAAAAAAACAGTGGATTGG", "CACTAAAAAAGAAGACCAAGCGG"] 

res = mb_request.get(sgrnas, filter_predicate=filter_genomes, transform_predicate = transform, genomes=["dd6cfb980c8a3659acffa4f002ea7404", "dd6cfb980c8a3659acffa4f0029ff84a"])
print(res)