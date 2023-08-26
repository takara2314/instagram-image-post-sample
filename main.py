# Instagramに画像を投稿するサンプル
# APIリファレンス: https://developers.facebook.com/docs/instagram-api/guides/content-publishing

import requests

# 次の認証情報を取得する方法は、以下の記事を参照してください。
#   認証情報の取得
#   https://di-acc2.com/system/rpa/19280/
#   アクセストークンの延長
#   https://taak.biz/archives/3901

# アプリID
APP_ID = "XXXXXXXXXXXXXXX"
# アプリシークレット
APP_SECRET = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# アクセストークン
ACCESS_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# InstagramビジネスアカウントID
INSTAGRAM_BUSINESS_ACCOUNT_ID = "XXXXXXXXXXXXXXXXX"
# グラフバージョン
GRAPH_VERSION = "v17.0"


# Facebook Graph API にPOSTリクエストを送信
def post_graph_api(endpoint: str, params: dict):
    params["access_token"] = ACCESS_TOKEN

    if endpoint == "":
        endpoint = "/"

    res = requests.post(
        f"https://graph.facebook.com/{GRAPH_VERSION}{endpoint}",
        params=params
    )

    return res


# 画像メディアを登録
def create_item_container(image_url: str, is_carousel_item: bool = False, caption: str = None) -> str:
    params = {}
    params["image_url"] = image_url

    if is_carousel_item:
        params["is_carousel_item"] = "true"
    if caption is not None:
        params["caption"] = caption

    res = post_graph_api(
        f"/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media",
        params
    )

    if res.status_code != 200:
        raise Exception(res.text)

    return res.json()["id"]


# 複数の登録された画像メディアを一つのコンテナにまとめる
def create_carousel_container(caption: str, item_containers: list) -> str:
    res = post_graph_api(
        f"/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media",
        {
            "caption": caption,
            "media_type": "CAROUSEL",
            "children": ",".join(item_containers)
        }
    )

    if res.status_code != 200:
        raise Exception(res.text)

    return res.json()["id"]


# コンテナにまとめられた画像メディアを投稿
def publish_media(creation_id: str) -> str:
    res = post_graph_api(
        f"/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish",
        {
            "creation_id": creation_id
        }
    )

    if res.status_code != 200:
        raise Exception(res.text)

    return res.json()["id"]


# 単一画像を投稿 (Single Media Posts)
def publish_single_media_post(caption: str, image_url: str) -> str:
    creation_id = create_item_container(image_url, caption=caption)

    return publish_media(creation_id)


# 複数画像を投稿 (Carousel Posts)
def publish_carousel_post(caption: str, image_urls: list) -> str:
    if len(image_urls) == 0:
        raise Exception("image_urls must not be empty")
    if len(image_urls) == 1:
        raise Exception("image_urls must be more than 1")
    if len(image_urls) > 10:
        raise Exception("image_urls must not be more than 10")

    item_container_ids = []

    for image_url in image_urls:
        item_container_ids.append(
            create_item_container(image_url, is_carousel_item=True)
        )

    creation_id = create_carousel_container(caption, item_container_ids)

    return publish_media(creation_id)


if __name__ == "__main__":
    # 文章と画像URLを指定して、Instagramに投稿する
    publish_single_media_post(
        "初めての投稿だぜ！\n#初めての投稿 #NotFound",
        "https://http.cat/404"
    )
