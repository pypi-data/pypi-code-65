def parse_json(resp_json: dict, keyword: str) -> list:
    final_list = []
    tweets = resp_json['globalObjects']['tweets']
    for tweet_id in tweets.keys():
        dict = {}
        dict["id"] = tweet_id
        dict['created_at'] = tweets[tweet_id]['created_at']
        dict['full_text'] = tweets[tweet_id]['text']
        dict['source'] = tweets[tweet_id]['source']
        dict['user_id'] = tweets[tweet_id]['user_id_str']
        dict['geo'] = tweets[tweet_id]['geo']
        dict['retweet_count'] = tweets[tweet_id]['retweet_count']
        dict['favorite_count'] = tweets[tweet_id]['favorite_count']
        dict["search_keyword"] = keyword
        final_list.append(dict)
    return final_list
