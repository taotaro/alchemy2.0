import requests
import pandas as pd
import time
import logging
import traceback
import time
import random
from jsonmerge import merge
import constants
import json

time_str = time.strftime("%Y-%m-%d")


class Product:
    def __init__(self, path, cat_name_or_keyword):
        # '''
        # Init function
        # Parameters:
        # - path: directory where everything is saved
        # - cat_name_or_keyword: input for creating names of folders/files
        # '''

        # self.products_csv is product listing file, other are paths/names how to save files
        self.path = path
        self.sub_cat_name_or_keyword = cat_name_or_keyword
        self.products_csv = pd.read_csv(
            f"{path}/{time_str}-{cat_name_or_keyword}-{constants.PRODUCT_LIST_FILE_TEMPLATE}.csv"
        )
        self.specification_file_name = f"{path}/{time_str}-{cat_name_or_keyword}-{constants.PRODUCT_SPECIFICATION_FILE_TEMPLATE}.csv"
        self.shop_data_name = f"{path}/{time_str}-{cat_name_or_keyword}-{constants.PRODUCT_SHOP_INFORMATION_FILE_TEMPLATE}.csv"
        self.comment_file_name = f"{path}/{time_str}-{cat_name_or_keyword}-{constants.PRODUCT_COMMENT_LIST_FILE}"

        # lists of itemId and shopId from self.products_csv/prodcut listing file
        self.item_id = self.products_csv["item_basic.itemid"]
        self.shop_id = self.products_csv["item_basic.shopid"]

        specification_time = time.time()
        logging.info("Getting Product Specification information: start...")
        self.product_specification()
        logging.info("Getting Product Specification information: done")
        logging.info(
            "--- %s seconds for specification---" % (time.time() - specification_time)
        )

        shop_time = time.time()
        logging.debug("Getting shop information: start...")
        self.shop_data()
        logging.info("Getting shop information: done!")
        logging.info("--- %s seconds for shop---" % (time.time() - shop_time))

        comment_time = time.time()
        logging.info("Getting Product Specification information: start...")
        self.comment()
        logging.info("Getting Product Comments: done")
        logging.info("--- %s seconds for shop---" % (time.time() - comment_time))

        merge_time = time.time()
        self.merge()
        logging.info("--- %s seconds for merge---" % (time.time() - merge_time))

    def specification_api(self, itemId, shopId):
        # '''
        # This function calls the shopee API to get information about product's specification
        # Parameters:
        # - itemId: id of desired product
        # - shopId: Id of shop that sells desired product
        # '''
        url = f"https://shopee.sg/api/v4/item/get?itemid={itemId}&shopid={shopId}"
        payload = {}
        headers = {
            "Cookie": "REC_T_ID=1eebbf57-fb70-11ec-aa39-e642a9121c0f; SPC_F=d2l0o7UqUeWsiM7TOmg6XfWVrmvEOK0u; "
            "SPC_R_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A"
            "+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY"
            "+A9gL52U=; SPC_R_T_IV=TXpMYnhvb1A3TWZEN3hKSw==; "
            "SPC_SI=agC8YgAAAAB4UzJPU2VxZvtu8gAAAAAAd1JNM0xmUkY=; "
            "SPC_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A"
            "+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY"
            "+A9gL52U=; SPC_T_IV=TXpMYnhvb1A3TWZEN3hKSw== "
        }

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
        except Exception as e:
            logging.info(traceback.format_exc())
            logging.info("Problem with response of specification API")

        return response

    def product_specification(self):
        # '''
        # This function supposed to get specification of product and save it in .csv file
        # '''
        product_specification_final = pd.DataFrame()
        # no_need is list of key names in JSON file from API that are not necessary
        no_need = [
            "overall_purchase_limit",
            "label_ids",
            "bundle_deal_info",
            "wholesale_tier_list",
            "tier_variations",
            "video_info_list",
            "coin_info",
            "models",
            "spl_info",
            "fe_categories",
            "shop_vouchers",
            "sorted_variation_image_index_list",
        ]
        # iteration through each product (length of self.shop_id is same with number products)
        for i in range(len(self.shop_id)):
            logging.info(f"product number = {i}")
            print(f"product number = {i}")
            # using try catch to avoid blocking of API
            try:
                # sleep too decrease numbers of blockings
                time.sleep(random.uniform(0.0, 2.0))
                # call API to get specification
                response = self.specification_api(self.item_id[i], self.shop_id[i])
                collected_data = response.json()
                # collected_data['data'] is None == blocking, therefore raise error
                if collected_data["data"] is None:
                    raise Exception("Exception: website blocked request")
            except Exception as e:
                # sleep for 80 seconds to remove the block from the site
                time.sleep(80)
                # call again API to get specification
                response = self.specification_api(self.item_id[i], self.shop_id[i])
                collected_data = response.json()
                logging.info(traceback.format_exc())
                print(traceback.format_exc())
                logging.info("Got specification but with problems")
            # IMPORTANT: sometimes, even sleep for 80 seconds does not help,this needs to be fixed (remove after fixing)

            temp_dic = {}
            # iteration through each key in collected data from API
            for key in collected_data["data"]:
                if key in no_need:
                    continue
                elif key == "categories":
                    # getting categories of product
                    cat_name = ""
                    for j in collected_data["data"][key]:
                        cat_name += " " + str(j["display_name"])
                    temp_dic[key] = [cat_name]

                elif key == "images":
                    # getting list of product images
                    imgs_list = []
                    for j in collected_data["data"][key]:
                        imgs_list.append(j)
                    temp_dic[key] = [imgs_list]

                elif key == "attributes":
                    # getting additional specifications of product (additional because each product has different attributes)
                    temp_dic[key] = [collected_data["data"][key]]
                elif collected_data["data"][key] is None or isinstance(
                    collected_data["data"][key], list
                ):
                    continue
                else:
                    # getting other data related to the product from API
                    temp_dic[key] = [collected_data["data"][key]]

            # creating dataframe for product's data that has been scraped
            product_specif_info = pd.DataFrame(temp_dic, dtype=object)
            # if there is already another dataframe product_specification_final, merge product_specif_info with it,
            # otherwise product_specification_final = product_specif_info
            if not product_specification_final.empty:
                previous_page = product_specification_final
                product_specification_final = pd.concat(
                    [previous_page, product_specif_info], join="outer"
                )
            else:
                product_specification_final = product_specif_info
        # saving result file product_specification_final as csv file
        product_specification_final.to_csv(f"{self.specification_file_name}")

    def shop_api(self, shopId):
        # '''
        # This function calls the shopee API to get information about product's shop/seller
        # Parameters:
        # - shopId: Id of shop that sells desired product
        # '''

        url = f"https://shopee.sg/api/v4/product/get_shop_info?shopid={shopId}"
        print(url)
        payload = {}
        headers = {
            "Cookie": "REC_T_ID=1eebbf57-fb70-11ec-aa39-e642a9121c0f; SPC_F=d2l0o7UqUeWsiM7TOmg6XfWVrmvEOK0u; SPC_R_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_R_T_IV=TXpMYnhvb1A3TWZEN3hKSw==; SPC_SI=agC8YgAAAAB4UzJPU2VxZvtu8gAAAAAAd1JNM0xmUkY=; SPC_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_T_IV=TXpMYnhvb1A3TWZEN3hKSw=="
        }
        try:
            response = requests.request(
                "GET", url, headers=headers, data=payload, timeout=30
            )
        except Exception as e:
            logging.info(traceback.format_exc())
            logging.info("Problem with response of shop API")
        return response

    def shop_data(self):
        # '''
        # This function supposed to get information about shops of products
        # '''
        shop_data = pd.DataFrame()
        # iteration through each shop that present in column "shopid" from self.products_csv (product listing file)
        for i in range(len(self.shop_id)):
            logging.info(f"shop number {i}")
            print(f"Total {len(self.shop_id)}|shop number {i}")
            # using try catch to avoid blocking of API
            try:
                # sleep too decrease numbers of blockings
                time.sleep(random.uniform(0.0, 2.0))
                response = self.shop_api(int(self.shop_id[i]))
                shop_collected_data = response.json()
                # shop_collected_data['data'] is None == blocking, therefore raise error
                if shop_collected_data["data"] is None:
                    raise Exception("Exception: website blocked request")
            except Exception as e:
                # sleep for 80 seconds to remove the block from the site
                time.sleep(80)
                # call again API for shop information
                response = self.shop_api(int(self.shop_id[i]))
                shop_collected_data = response.json()
                logging.info(traceback.format_exc())
                print(traceback.format_exc())
                logging.info("Got Shop Information but with problems")
            # IMPORTANT: sometimes, even sleep for 80 seconds does not help,this needs to be fixed (remove after fixing)

            temp_dic = {}
            # looping through each key in shop_collected_data['data']
            for key in shop_collected_data["data"]:
                # getting username of shop and status of user
                if key == "account":
                    username = []
                    status = []
                    username.append(shop_collected_data["data"][key]["username"])
                    status.append(shop_collected_data["data"][key]["status"])
                    temp_dic[key] = [[username, status]]
                # skipping 'empty' keys
                elif shop_collected_data["data"][key] is None or isinstance(
                    shop_collected_data["data"][key], list
                ):
                    continue
                else:
                    # getting other related data
                    temp_dic[key] = [shop_collected_data["data"][key]]

            # creating dataframe for shop's data that has been scraped
            shop_information = pd.DataFrame(temp_dic, dtype=object)

            # if there is already another dataframe shop_data, merge shop_information with it,
            # otherwise shop_data = shop_information
            if not shop_data.empty:
                previous = shop_data
                shop_data = pd.concat([previous, shop_information], join="outer")
            else:
                shop_data = shop_information
            print(f"Current len = {len(shop_data['shopid'])}")

        # saving all collected data as .csv file
        shop_data.to_csv(f"{self.shop_data_name}")

    def merge(self):
        try:
            logging.info("Final step...")
            # reading finished .csv files
            shop_data = pd.read_csv(self.shop_data_name)
            specification = pd.read_csv(self.specification_file_name)
            # merging .csv files into one .csv file and saving them
            result = pd.concat([self.products_csv, shop_data, specification], axis=1)
            result.to_csv(
                f"{self.path}/{self.sub_cat_name_or_keyword}_{constants.PRODUCT_LIST_FILE_CLEAR}.csv"
            )

            # saving json files
            shop_json = shop_data.to_json()
            specification_json = specification.to_json()
            general_json = self.products_csv.to_json()
            raw_json = merge(general_json, shop_json)
            raw_json = merge(raw_json, specification_json)
            path_name = self.path

            with open(
                f"{path_name}/{self.sub_cat_name_or_keyword}_RAW.json", "w"
            ) as raw_output:
                raw_output.write(raw_json)
            logging.info("Finished")

        except:
            logging.info(traceback.format_exc())
            logging.info("Can not merge")
            return

    def comment_api(self, item_id, shop_id, limit=59, offset=0):
        # '''
        # This function calls the shopee API to get comments of the product
        # Parameters:
        # - item_id: Id of the product which comments are desired
        # - shop_id: Id of product's shop
        # - limit: number of comments per page (maximum is 59)
        # - offset: comment number to start from (to show)
        # '''
        url = f"https://shopee.sg/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit={limit}&offset={offset}&shopid={shop_id}&type=0"
        print(url)
        payload = {}
        headers = {
            "Cookie": "REC_T_ID=1eebbf57-fb70-11ec-aa39-e642a9121c0f; SPC_F=d2l0o7UqUeWsiM7TOmg6XfWVrmvEOK0u; SPC_R_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_R_T_IV=TXpMYnhvb1A3TWZEN3hKSw==; SPC_SI=agC8YgAAAABNZjlaSEZFTDn4RQIAAAAAajZFYms3b1A=; SPC_T_ID=BOoN7lckySNuyWvnjuWgVxB24aHhrbECNT3qHWQ9zMsVGC706kY2zSUgjGj93XjBZcsT2x+gJ2A+gHLRRhLBqJeyicAaRA2JEudV2FNTj1Dbwr/xRpg9wkBPnT7C85sHC6Lz7UZhoPtNu01ZNkYs3YbGD3UpsDGeIOY+A9gL52U=; SPC_T_IV=TXpMYnhvb1A3TWZEN3hKSw=="
        }

        try:
            response = requests.request(
                "GET", url, headers=headers, data=payload, timeout=20
            )

        except Exception as e:
            logging.info(traceback.format_exc())
            logging.info("Problem with response of comment API")
        return response

    def comment(self):
        # '''
        # This function calls the shopee API to get comments of the product
        # '''
        product_comment = pd.DataFrame()
        comment_dic = {}
        comments_json = {}
        for i in range(len(self.shop_id)):
            comments_json[f"{self.item_id[i]}"] = []
            offset = 59
            print(f"Items {len(self.shop_id)} - Number {i}")
            logging.info(f"number = {i}")

            try:
                time.sleep(random.uniform(0.0, 2.0))
                # Getting number of comment pages of each item
                response = self.comment_api(self.item_id[i], self.shop_id[i])
                collected_data = response.json()
            except Exception as e:
                # sleep for 80 seconds to remove the block from the site
                time.sleep(80)
                # call again API for shop information
                response = self.comment_api(self.item_id[i], self.shop_id[i])
                collected_data = response.json()
                logging.info(traceback.format_exc())
                print(traceback.format_exc())
                logging.info("Got comment, but with problems")
            # IMPORTANT: sometimes, even sleep for 80 seconds does not help,this needs to be fixed (remove after fixing)

            comment_list_per_product = []
            if collected_data["data"] is None:
                print("NO DATA")
                continue
            # skip product if its' "rcount_with_context"(comments) is 0
            total_comments = int(
                collected_data["data"]["item_rating_summary"]["rcount_with_context"]
            )
            if total_comments == 0 or total_comments is None:
                print("Total is ZERO")
                continue

            print(f"Total numberof comments = {total_comments}")

            page_number = int(total_comments / 59)
            # if there is less than 59 comments, there is onlu 1 page of comments
            if total_comments < 59:
                page_number = 1
                offset = total_comments

            # looping through each page and call API to get comments of that page
            for page in range(page_number):
                time.sleep(random.uniform(0.0, 2.0))
                response = self.comment_api(
                    self.item_id[i], self.shop_id[i], offset=offset * page
                )
                if response is None:
                    continue
                collected_data = response.json()
                if collected_data["data"] is None:
                    continue
                try:
                    for rating in collected_data["data"]["ratings"]:
                        comments_json[f"{self.item_id[i]}"].append(
                            [rating["comment"], rating["rating_star"]]
                        )
                except:
                    continue
            # saving
            with open(f"{self.comment_file_name}.json", "w") as product_comment:
                json.dump(comments_json, product_comment)
        # final saving
        with open(f"{self.comment_file_name}.json", "w") as product_comment:
            json.dump(comments_json, product_comment)
