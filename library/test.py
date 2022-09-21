

# from library.file_read_lib import get_content_from_file
import score_lib
import process_data_lib
import file_read_lib
import score_product_lib
import json
import constants
import oss2

auth=oss2.Auth(constants.ACCESS_KEY_ID, constants.ACCESS_KEY_SECRET)
bucket=oss2.Bucket(auth, constants.ENDPOINT, constants.BUCKET)
test_url='https://shopee.sg/Vention-Ethernet-Cable-Cat7-Lan-High-Speed-10Gbps-SFTP-RJ-45-Network-Cable-Patch-Cable-8m-10m-for-Laptop-PC-i.95236751.1578425947?sp_atk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59&xptdk=533f4b97-0ce8-4eb0-8d9a-99fc000c4b59'
id=score_lib.get_shopee_id(test_url)
shop=id[0]
product=id[1]
d=score_lib.api_search_item(shop, product)
data=d['data']
# print(data)
with open('data.json', 'w') as f:
    json.dump(data, f)
category=score_lib.get_category_names(d)[0]
print(category)

df=process_data_lib.process_product_from_link(data, bucket, 'Bag_of_words/', category)
# print(df)
feats=file_read_lib.get_file_from_bucket(bucket, 'Forward_selection/', category)
f=file_read_lib.get_content_from_file(feats)
# print(f)
score=score_product_lib.get_score(df, f)
print(score[0])
# # feats=file_read_lib.get_list_from_text_file(category, 'library/fs')
# # # print(feats)
# # score=score_product_lib.get_score(df, feats)
# # print(score)



