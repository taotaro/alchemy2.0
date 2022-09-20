
import score_lib
import process_data_lib
import file_read_lib
import score_product_lib


test_url='https://shopee.sg/NEXGARD-SPECTRA.AUTHENTIC.%E3%80%8B-i.253386617.4334047211?sp_atk=e7f43f81-9fdf-418f-9c13-579cd981439e&xptdk=e7f43f81-9fdf-418f-9c13-579cd981439e'
id=score_lib.get_shopee_id(test_url)
shop=id[0]
product=id[1]
d=score_lib.api_search_item(shop, product)
data=d['data']
category=score_lib.get_category_names(d)[0]

df=process_data_lib.process_product_from_link(data, category, 'library/bog')
# print(df)
feats=file_read_lib.get_list_from_text_file(category, 'library/fs')
# print(feats)
score=score_product_lib.get_score(df, feats)
print(score)