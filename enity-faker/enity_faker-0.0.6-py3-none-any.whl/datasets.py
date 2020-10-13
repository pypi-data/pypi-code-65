import os
import shutil
import random
import json
import re
import spacy
from .entitykeywordgenerator import generate_entites, get_entities_json
from .keywords import KeywordsType
from .insertlocations import InsertLocation
import en_core_web_sm

def insertkeywordandentity(words, location, config, ge):
    index = random.randint(0,len(words)-1)
    if(location == InsertLocation.KeyValue):
        word = words[index]
        separator = random.choice(config['separator'])
        entry = ge[0]+separator+ge[1]
        word = entry + " " + word
        words[index] = word
        return words
    elif (location == InsertLocation.SameLineBeforeEntity):
        word = words[index]
        word = ge[1] + " " + word + " " + ge[0]
        words[index] = word
        return words
    elif (location == InsertLocation.SameLineAfterEntity):
        word = words[index]
        word = ge[0] + " " + word + " " + ge[1]
        words[index] = word
        return words
    elif (location == InsertLocation.DiffLineBeforeEntity):
        diff = random.randint(index,len(words)-1)
        first = words[index]
        first = ge[1]+" "+first
        words[index] = first
        last = words[diff]
        last = ge[0]+" "+last
        words[diff] = last
        return words
    elif (location == InsertLocation.DiffLineAfterEntity):
        diff = random.randint(index,len(words)-1)
        first = words[index]
        first = ge[0]+" "+first
        words[index] = first
        last = words[diff]
        last = ge[1]+" "+last
        words[diff] = last
        return words

def insert_entities(config, entities_changed = []):
    sp = spacy.load('en_core_web_sm')
    # with open('/entityfaker/config.json',encoding="utf8") as f:
    #     config = json.load(f)
    #     print(config)

    # with open('/entityfaker/entities.json',encoding="utf8") as f:
    # entity_config = get_entities_json()

    file_loc = config["filepath"]
    file_dest = config["filedestpath"]
    if os.path.exists(file_dest):
        shutil.rmtree(file_dest)
    os.makedirs(file_dest)
    files = os.listdir(file_loc)
    files_count = len(files)

    entities = config["entities"]

    files_dist = []
    for d in config["file_distribution"]["distribution_percent"]:
        files_dist.append(int(d * files_count/100))

    labels = []
    dist=0
    counter = 1
    os.makedirs(file_dest + "/dataset" + str(dist+1))
    for f in files:
        entity_count = config["file_distribution"]["entity_count"][dist]
        shutil.copy(file_loc + "//" + f, file_dest + "/dataset" + str(dist+1)+"/"+f)
        with open(file_dest + "/dataset" + str(dist+1)+"/"+f, 'r',encoding="utf-8") as fl:
            text = fl.read()
            spc = sp(text)
            words = []
            for t in spc.sents:
                words.append(t.text)
        filenamekeywords = []
        with open(file_dest + "/dataset" + str(dist+1)+"/"+f, 'w',encoding="utf-8") as fl:
            enties_to_insert = random.choices(config["entities"], k=entity_count)
            count = 0
            for t in enties_to_insert:
                if(config["entity_keywords"][count] == "specific"):
                    keyword = KeywordsType.Specific
                elif (config["entity_keywords"][count] == "generic"):
                    keyword = KeywordsType.Generic
                elif (config["entity_keywords"][count] == "empty"):
                    keyword = KeywordsType.Empty
                elif (config["entity_keywords"][count] == "conflict"):
                    keyword = KeywordsType.Conflict
                # keyword = random.choice([KeywordsType.Specific, KeywordsType.Generic, KeywordsType.Empty])
                # keyword = random.choice([KeywordsType.Specific,KeywordsType.Generic,KeywordsType.Empty])
                instances = config["entities"].index(t)
                generated_entities = generate_entites(t, keyword, config["entities_instances"][instances], entities_changed)
                for ge in generated_entities:
                    location = random.choice([InsertLocation.KeyValue,InsertLocation.SameLineBeforeEntity,InsertLocation.SameLineAfterEntity,InsertLocation.DiffLineBeforeEntity,InsertLocation.DiffLineAfterEntity,InsertLocation.InFileName])
                    if(location == InsertLocation.InFileName):
                        index = random.randint(0,len(words)-1)
                        word = words[index]
                        entry = ge[0]
                        word = entry + " " + word
                        words[index] = word
                        filenamekeywords.append(ge[1])
                    else:
                        insertkeywordandentity(words, location, config, ge)
                    temp_text = "".join(words)
                    inserted = ge[0]
                    pos = re.search(inserted, temp_text)
                    if(pos is not None):
                        end = pos.end()
                        begin = pos.start()
                    else:
                        begin = 0
                        end = 0
                    labels.append({
                        "filename": f,
                        "entityname": t,
                        "entityvalue": ge[0],
                        "keywordtype": keyword.name,
                        "entitykeyword": ge[1],
                        "begin": begin,
                        "end": end,
                        "labeltype": "true positive"
                    }) 
                count += 1
            if(len(config["confilict_entities"])>0):
                conflict_enties_to_insert = random.choices(config["confilict_entities"], k=entity_count)
                for c in conflict_enties_to_insert:
                    conflict_instances = config["confilict_entities"].index(c)
                    generated_conflict_entities = generate_entites(c, KeywordsType.Conflict,config["confilict_entities_instances"][conflict_instances],entities_changed)
                    for ge in generated_conflict_entities:
                        location = random.choice([InsertLocation.KeyValue,InsertLocation.SameLineBeforeEntity,InsertLocation.SameLineAfterEntity,InsertLocation.DiffLineBeforeEntity,InsertLocation.DiffLineAfterEntity,InsertLocation.InFileName])
                        # if(location == InsertLocation.InFileName):
                        if(location == InsertLocation.InFileName):
                            index = random.randint(0,len(words)-1)
                            word = words[index]
                            entry = ge[0]
                            word = entry + " " + word
                            words[index] = word
                            filenamekeywords.append(ge[1])
                        else:
                            insertkeywordandentity(words, location, config, ge)
                        temp_text = "".join(words)
                        inserted = ge[0]
                        pos = re.search(inserted, temp_text)
                        if(pos is not None):
                            end = pos.end()
                            begin = pos.start()
                        else:
                            begin = 0
                            end = 0
                        labels.append({
                            "filename": f,
                            "entityname": t,
                            "entityvalue": ge[0],
                            "keywordtype": keyword.name,
                            "entitykeyword": ge[1],
                            "begin": begin,
                            "end": end,
                            "labeltype": "true positive"
                        }) 
            text = "".join(words)
            fl.write(text)     
            if(counter == files_dist[dist]):
                counter = 1
                dist += 1
                if(dist >= len(files_dist)):
                    break
                os.makedirs(file_dest + "/dataset" + str(dist+1))
        if(len(filenamekeywords)>0):
            keywordtoadd = random.choice(filenamekeywords)
            f_splt = f.split('.')
            if(keywordtoadd != ""):
                newname = f_splt[0]+"-"+keywordtoadd+'.'+f_splt[1]
                if(os.path.exists(file_dest + "/dataset" + str(dist+1)+"/"+f)):
                    os.rename(file_dest + "/dataset" + str(dist+1)+"/"+f,file_dest + "/dataset" + str(dist+1)+"/"+newname)
        counter += 1
    with open(file_dest+'\labels.json', 'w',encoding="utf-8") as f:
        json.dump(labels, f,indent=4)
