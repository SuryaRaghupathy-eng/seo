#!/usr/bin/env python3

import sys
import json
import time
import requests
import csv
from io import BytesIO
from pathlib import Path
from PIL import Image


def load_model():
    from transformers import BlipProcessor, BlipForConditionalGeneration
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model     = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    print("Model ready!\n")
    return processor, model


# ── Image fetching ─────────────────────────────────────────────────────────────

def fetch_image(source: str) -> Image.Image:
    if source.startswith("http://") or source.startswith("https://"):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "/".join(source.split("/")[:3]) + "/",
        }
        session = requests.Session()
        response = session.get(source, headers=headers, timeout=15)

        if response.status_code == 403:
            raise Exception(
                "403 Forbidden – the website is blocking downloads.\n"
                "Download manually and use local path."
            )

        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    else:
        return Image.open(source).convert("RGB")


# ── Alt text generation ────────────────────────────────────────────────────────

def generate_alt_text(image: Image.Image, processor, model) -> str:
    inputs = processor(image, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=100)
    return processor.decode(output[0], skip_special_tokens=True).strip()


# ── Bulk processing ────────────────────────────────────────────────────────────

def process_sources(sources: list[str], processor, model) -> dict[str, str]:
    results = {}
    total = len(sources)

    for i, source in enumerate(sources, 1):
        print(f"[{i}/{total}] {source[:80]}")
        try:
            image    = fetch_image(source)
            alt_text = generate_alt_text(image, processor, model)
            results[source] = alt_text
            print(f"         → {alt_text}\n")
        except Exception as e:
            results[source] = f"ERROR: {e}"
            print(f"         ✗ Failed: {e}\n")

    return results


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    DEFAULT_URL = (
        "https://www.thepropertyfranchisegroup.co.uk"
        "/wp-content/uploads/2025/09/aldershot-franchsie-owners.jpg"
    )

    if len(sys.argv) == 1:
        sources = [
          "https://www.belvoir.co.uk/wp-content/uploads/2026/01/wednesbury-1.webp",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Haywards-Heath-1.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/belvoirmiltkeynes.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/peterborough_office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/luton.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Tompy.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/AD_4nXclSKiND9Rp27dUAfWZngtfKLBhxQWyuThDk1oyecGxuFkXR0fjyC4u0M5Kuqeiw-bzBpSxTqtA34mBbDvU7FILDOjQ3La1BzPx-BrYU7XFCjlwuysPgar0KOpln-XIps-vOnDJ.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/wednesbury-1.webp",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/IMG_2776-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Mumbles-1-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tilehurst-office-image-revised-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/warrington.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-10.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/meltonmowbray-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-Image.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/2lpsBcSRFssSG2rMP3rJLEHsrET53nY-8OP3hUj3I7kE4p7VRa2xUOuNFUnCZQKM7xNyXNIDx9CsvVRHXIOW88S2P3gSteh-hu_Qar7T4yfTcoUr9mQ-jjopUT4qiytpxjq58gg0YSY_mQYQiA.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leedss-scaled-1.jpg",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.0.1&permmsgid=msg-f:1784006993910086361&th=18c210e8acd2bad9&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ9Vf_BrVvutKznkqFgop9etkbIoESf11ZXt61135lci0lY7vq4GnGdUmmdXdt_95_g9O_hMdlm5T-YmPtFfuV68yHX0Q6FYo5dCfpyNZhItbj490vqBUUQsvj4&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Kingston_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Aberdeen.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Biggleswade.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/cannock.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/ChrisBerry.jpeg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/clogged-sink-clipart-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Bangor-resized.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Coventry_office_2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/edinburgh-1541103_1920.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-5.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/orig_1298087_large.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/mp4s5iI1HOgjc21hDVv175Uo2FpUXe_BhinofG6IKEYlG-8NbbY28s_Ps019MkCaBKjn5zooYgpr5hvqH2nyQ5CsqgVHx013gjPlA8W0I5GMuTV4x8GnnEmBH1J5-VIjdxAV_vwECGvEeUM3A.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Bournemouth.jpg",
"https://www.pyranet.co.uk/wp-content/uploads/2018/10/daily-traffic.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-4.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-11.jpg",
"https://www.belvoir.co.uk/birmingham-central-estate-agents/wp-content/uploads/sites/14/2021/11/Belvoir-Birmingham-Central_BRONZE_LAL-236x300.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leedss-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Aldershot.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20230523_132322-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/user_edited_photo-3da716d8_user-edited-f74e8906-48-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/cannock.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Shrewsbury-e1768227536647.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Front-Shot.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/belv1-copy-5-e1643905437757.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Liverpool-w_derby.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/sutton-coldfield-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/2lpsBcSRFssSG2rMP3rJLEHsrET53nY-8OP3hUj3I7kE4p7VRa2xUOuNFUnCZQKM7xNyXNIDx9CsvVRHXIOW88S2P3gSteh-hu_Qar7T4yfTcoUr9mQ-jjopUT4qiytpxjq58gg0YSY_mQYQiA.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/mp4s5iI1HOgjc21hDVv175Uo2FpUXe_BhinofG6IKEYlG-8NbbY28s_Ps019MkCaBKjn5zooYgpr5hvqH2nyQ5CsqgVHx013gjPlA8W0I5GMuTV4x8GnnEmBH1J5-VIjdxAV_vwECGvEeUM3A.png",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/placeholder_logo.png",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.1&permmsgid=msg-f:1748579592629409873&th=184433e0082c5851&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ_IP8os5RyjruIw46WAkyfEfBWCe_7Ok26n4igIDvPs4N855E8nwVydSK6iBwPFuQppJLeRVi_40iEzEVtAbL8gqO6c7-krEGg7nhHlz6nfk-VrLfcWoeQ0WDM&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Gastech.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/1149.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Swindon_Office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Manchester_Hero_resized.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20230523_132322-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/sutton-coldfield-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/IMG_2776-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tadley-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/dunstable.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tadley-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/VWOM5YKJ45iJCQA8AgOBCjMp5kXGw_ybmQeKTz2Ug5enuofTvYV33hDILZ1dG8fMMNVP6XAsWIJhZwYr2WCbzsfMMbtenVDAdAHdumryIdSfLNQX4_VNxD2dAeEBzbA499JcmMhas0.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/watford-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/Belvoir-New-Logo.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/yGLjAGRTQlM-8kzXHa2s8daWnaav-3MZ4B5bmD8QgODrssbVFE_eR3AVaE9eatnYzzEOWQKyz0vgE9mwGrE_QsZpMO_KWM22stePlbpy9YhSJA5JJrDX_sPmgP2myuZxCAL2LBijdmc1QjsrBw.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Romford_Office-1.jpg",
"https://www.belvoir.co.uk/sidcup-estate-agents/wp-content/uploads/sites/125/2024/11/Artboard-1-copy@4x-300x118.png",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.1&permmsgid=msg-f:1779281513314923353&th=18b1471bfc8e3359&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ8LkceiPCoNy54l0AzcZwW2F88CCmKX7TpIujxdknq0Y2j7O52gGNNETSrffvzfzF6h7lPu-P9h7GUHHPQLy6X14fhyAIFnMFSFX8SF7gVcIGD_rHkrCji9hYw&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/stafford_office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Shrewsbury-e1768227536647.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leeds-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/office-image-resized.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/new_office_image-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tilehurst-office-image-revised-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/falkirk-scaled-1.jpg",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.2&permmsgid=msg-f:1779281513314923353&th=18b1471bfc8e3359&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ95LNIbXGJe3tqk5vLTCiyYEjW15c4zjuPvrLND3KtSBbGUWk5DznaDPKGAHDfIJjjlXwwSXvE2PTaecvGiTOU5QwNKXSjxAUnqb3GP75LE9lUakddwOUgCrvY&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Mumbles-1-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leedss-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-9.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-image-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/stamford_and_bourne-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-1-10.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Shrewsbury-e1768227536647.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/york-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tadley-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/breather-187923-unsplash.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/stirling-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20210506-IMG_3157-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-image-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/ipswich_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-15.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/stafford_office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/UHFR8301_1.jpg",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.2&permmsgid=msg-f:1755900281541459646&th=185e3600be497ebe&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ_dWvvhhf3HrVvw0njsrEF0_fwZQmheHRRVxW1MiS8SDtNP_ADaiEOp60sG9R9sjrBNuSpRK7Bpy2gDDIyq1QWdcJYIitGlrLQGK3fbv-vYRFlMASlRTDlGAo8&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/VWOM5YKJ45iJCQA8AgOBCjMp5kXGw_ybmQeKTz2Ug5enuofTvYV33hDILZ1dG8fMMNVP6XAsWIJhZwYr2WCbzsfMMbtenVDAdAHdumryIdSfLNQX4_VNxD2dAeEBzbA499JcmMhas0.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/mp4s5iI1HOgjc21hDVv175Uo2FpUXe_BhinofG6IKEYlG-8NbbY28s_Ps019MkCaBKjn5zooYgpr5hvqH2nyQ5CsqgVHx013gjPlA8W0I5GMuTV4x8GnnEmBH1J5-VIjdxAV_vwECGvEeUM3A.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/user_edited_photo-3da716d8_user-edited-f74e8906-48-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tadley-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20210506-IMG_3157-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Bingham.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/P1180852-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/VWOM5YKJ45iJCQA8AgOBCjMp5kXGw_ybmQeKTz2Ug5enuofTvYV33hDILZ1dG8fMMNVP6XAsWIJhZwYr2WCbzsfMMbtenVDAdAHdumryIdSfLNQX4_VNxD2dAeEBzbA499JcmMhas0.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Bedford-scaled-1.jpg",
"https://www.belvoir.co.uk/stoke-on-trent-estate-agents/wp-content/uploads/sites/138/2024/03/All-Agents-2023-300x300.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Homepage_card_book_appraisal.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leedss-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/EED8A6FC-5122-4E32-A5FB-7DFB9033010E.jpeg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/warrington.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-9.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/derby-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-8.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Andover-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Walsall-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-12.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/John26Conor.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/placeholder_logo.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/nuneaton-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Mumbles-1-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wolverhampton-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-image-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/Belvoir-Chelmsford-Branch-Photo.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wolverhampton-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Guildford_homepage-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tilehurst-office-image-revised-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/mancs_chorl-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-8.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/sunderland-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/mp4s5iI1HOgjc21hDVv175Uo2FpUXe_BhinofG6IKEYlG-8NbbY28s_Ps019MkCaBKjn5zooYgpr5hvqH2nyQ5CsqgVHx013gjPlA8W0I5GMuTV4x8GnnEmBH1J5-VIjdxAV_vwECGvEeUM3A.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/IMG_2776-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tadley-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/huntingdon-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/crewe.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Mumbles-1-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tumbridge-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tamworth_offive-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wigan_Office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wolverhampton-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20230523_132322-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/warrington.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Let-office-finder.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/4.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/west-bridgeford-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leedss-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/sleaford-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/AD_4nXcUeaQRX5n3r96lXcjo4bEF4g6CuzLFxIAxGCnkRWFqbNcNlqarChgctEB-qLOLgaFjj0CSHUj6cnhxVhc-81JlyoMuifqXVnQamZXic1JWbVROuFEwQstZKppeS9oHTz9ILYaQ_g.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/KRT_A9azF_1klI02NHQgCjuJcXUSKwQhiTZSfDYSUuRU9CHPJj9rm8ZlGr67llRWm0HLX_kGcOiRX_Kz3DfCEb9VcvJUkWr9kffrqyz4wmsHZOcPsKwTimUeDpOFQ9F-szQPaz2-.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wigan_Office-1.jpg",
"https://www.belvoir.co.uk/bingham-estate-agents/wp-content/uploads/sites/13/2024/03/team-300x257.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Liverpool_South_-_Shop_Front-scaled-1.jpg",
"https://www.belvoir.co.uk/sidcup-estate-agents/wp-content/uploads/sites/125/2023/11/Artboard-1-copy@3x-300x118.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/sheffield-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/Best-Yet.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/B_Northampton-Hero-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20230523_132322-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Shrewsbury-e1768227536647.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/SUA.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-7.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Burton_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/Belvoir-Chelmsford-Branch-Photo.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Stone-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tamworth_offive-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/keys.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/maidenhead.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-14.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Tynedale-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tamworth_offive-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20210506-IMG_3157-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Ralph.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/EoX3XX421LG9P5u6I2NvmFAf6lHhcX0eCuT38lwhL4Ud0UV7no1IhBj28QBrnlGq592hKpKDq8GwZ3oTpCkDxKUEYtlcYVDIouphHTgNqUKSYhkopy7rcF2Ugihv27XlEW80XMjS.png",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.0.2&permmsgid=msg-f:1784006993910086361&th=18c210e8acd2bad9&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ82E6sCvXY3OMhC1BRXUlkVWvmPY3ktpVwG4Dl-IS3plKX9H-i-lRHQmB0kMxJZyn7Dwo7ya_zcol9-RkgJCrYICu2WIMWd1SaJ7WS4lP7Nwv9hB13Q8wrPWVw&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tmYmDkZROi9c6o-_rFFRy5sM499Gy2Om3GQe2xChzhOtPy5-yofyAN7eD9hBaAYs0NjVeKjhDgELjf11sqOzaA088qg0lx6635NLo0hPpn_-iqoCIZ059RvGCoF7RE60jJo9fnad.png",
"https://www.belvoir.co.uk/stoke-on-trent-estate-agents/wp-content/uploads/sites/138/2022/10/Ramona-Award-Property-Mark-2022-226x300.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/2.jpg",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.1&permmsgid=msg-f:1755900281541459646&th=185e3600be497ebe&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ-90eVNT7QKW7N0fh8j3tW8wEqHIkUp0h-_oQq743qyjEGD3K9Mc0t_TXuy1G0LC-VUvfKtGN4OBeqCG3E3DZN9bMWjHphJWiyirUVzcBUqRrRtXe_lG-Hd7fg&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Shrewsbury-e1768227536647.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/boston.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/user_edited_photo-3da716d8_user-edited-f74e8906-48-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/wednesbury-1.webp",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-13.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-Image.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leeds-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/TachbrookRdfrontshot.jpg",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.2&permmsgid=msg-f:1748579592629409873&th=184433e0082c5851&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ_kvgGw6cVVxZZ7sOwkCn8OrtNgOLp04V_2eLLL4rmRw-dBCw5Q93etDnoa_d3_6it15sFyl574tflkX_5GaLyv8eVSAdhAEMCAG2RdDXlu1aLqnk3Syt-wKJA&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leeds-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/liverpoolcentral_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tumbridge-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/470234591_1097987198665012_7299219586427778159_n.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wigan_Office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Harrogate_officepic-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tamworth_offive-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/PVtZRDvnhjWOvL3qxiC8RqXHWg002GlUChRWq29ZY7CXzUnNGiCdr0bGx8GP6lZfMfIAa9TYL5_dwHkvdlyAtnVk3O9-qWm4_BQ1n8BDK4v7WngFfwdzUeoauvyTMhvPlj-9MnFHStmVlnyL5Vr5iYA.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/hitchin_2-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/uxbridge-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-image-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tamworth_offive-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Cambridge-2-scaled-e1680253832587.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-Image.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/ipswich_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/orig_1298087_large.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tadley-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Sold-let-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/wednesbury-1.webp",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/long-eaton.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/yGLjAGRTQlM-8kzXHa2s8daWnaav-3MZ4B5bmD8QgODrssbVFE_eR3AVaE9eatnYzzEOWQKyz0vgE9mwGrE_QsZpMO_KWM22stePlbpy9YhSJA5JJrDX_sPmgP2myuZxCAL2LBijdmc1QjsrBw.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/2lpsBcSRFssSG2rMP3rJLEHsrET53nY-8OP3hUj3I7kE4p7VRa2xUOuNFUnCZQKM7xNyXNIDx9CsvVRHXIOW88S2P3gSteh-hu_Qar7T4yfTcoUr9mQ-jjopUT4qiytpxjq58gg0YSY_mQYQiA.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Mumbles-1-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-New-Logo.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/chester_office.jpg",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.1&permmsgid=msg-f:1746930711043882673&th=183e5839defdbeb1&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ8BOrBPYh2tcWtUVXDQkJ2Fml94X5p5ouBB795l2dSD3Wv9cEqI3eSRRngt9XKxgO8YdTYbW3EX21Yglqu_l2re_mwktPpLosdiH_17VloGfbJRQItBL4isL0o&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/stafford_office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Walsall-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/corby.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-5.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20230523_132322-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-Image.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/rochester-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tumbridge-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Sold-let-4-scaled-3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/2lpsBcSRFssSG2rMP3rJLEHsrET53nY-8OP3hUj3I7kE4p7VRa2xUOuNFUnCZQKM7xNyXNIDx9CsvVRHXIOW88S2P3gSteh-hu_Qar7T4yfTcoUr9mQ-jjopUT4qiytpxjq58gg0YSY_mQYQiA.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tilehurst-office-image-revised-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/nottwest-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Plymouth_Hero-scaled-3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Norfolk_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Mumbles-1-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tadley-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/warrington.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-4.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-3.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leeds-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-6.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leeds-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Walsall-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/cheltenham-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/4O4A9548-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/placeholder_logo.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/devizs.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wolverhampton-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leedss-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-pic.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Norfolk_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/user_edited_photo-3da716d8_user-edited-f74e8906-48-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-13.jpg",
"https://mail.google.com/mail/u/0?ui=2&ik=4dd4a0dc2c&attid=0.2&permmsgid=msg-f:1746930711043882673&th=183e5839defdbeb1&view=fimg&fur=ip&sz=s0-l75-ft&attbid=ANGjdJ_SJI0Eadpbk2DkPJyhdE8WbohLRQomdCTPY9Fo5sx99giTzDSTywW5ZuVfl1suQiu-5VgSawKpP0oTEW2UzRQOUupURDzL0ZkZbASRPO-SLbQeyw5x52rv194&disp=emb",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Coventry_office_2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/cannock.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Colchester.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/yGLjAGRTQlM-8kzXHa2s8daWnaav-3MZ4B5bmD8QgODrssbVFE_eR3AVaE9eatnYzzEOWQKyz0vgE9mwGrE_QsZpMO_KWM22stePlbpy9YhSJA5JJrDX_sPmgP2myuZxCAL2LBijdmc1QjsrBw.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-11.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/portsmouth-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-7.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-6.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Mumbles-1-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/IMG_2776-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Stone-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/VWOM5YKJ45iJCQA8AgOBCjMp5kXGw_ybmQeKTz2Ug5enuofTvYV33hDILZ1dG8fMMNVP6XAsWIJhZwYr2WCbzsfMMbtenVDAdAHdumryIdSfLNQX4_VNxD2dAeEBzbA499JcmMhas0.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/IMG_2776-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/ipswich_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/liverpool.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/IMG_2776-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-image-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/333.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-Image.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Basingstoke.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Ku6qs1rDiB-sliFYAc0op6eaf1xXUFH1ilRFAcI6b6Xf9hUXR9mjhP4EPb1xNVRG_EVPQFCAIbhS6layRjfY0HiJGBxyAG3djU1vkPifHhbu3ybAmJy4vqsE3q68XevzSJR9FhaZ.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/derby-west.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/yGLjAGRTQlM-8kzXHa2s8daWnaav-3MZ4B5bmD8QgODrssbVFE_eR3AVaE9eatnYzzEOWQKyz0vgE9mwGrE_QsZpMO_KWM22stePlbpy9YhSJA5JJrDX_sPmgP2myuZxCAL2LBijdmc1QjsrBw.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/NewSue2800229.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Bolton-hero-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Cheadle_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-4.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/closed.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/cannock.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Welwyn_Office_Pic_2021-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wigan_Office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tilehurst-office-image-revised-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/wednesbury-1.webp",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Page_03_Belvoir_Grantham_shop_outside_cropped_-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/HNY.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wolverhampton-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/rugby-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Kettering_office_2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/IMG_7414-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Present_Chaos.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/user_edited_photo-3da716d8_user-edited-f74e8906-48-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tumbridge-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-image-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office_Image.bmp.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-Image.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/Belvoir-Chelmsford-Branch-Photo.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-14.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/leeds-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/AD_4nXeME62wteY0yJo_e8nalFnV7yS5fOgbfpX6_72U0sFHG_DO8yByS3_yrvc4DFjYWxx57QxQjzMO0Ee-kwEGacgFozyamKXZ3BATfjKN_qpoMeqGiL0guZsPJJWfACwL7VlQE74ZeA.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Wigan_Office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir_Doncaster.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Cambridge-2-scaled-e1680253832587.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/lisburn.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Newark_office_new.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/NewcastleUL_office.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/20210506-IMG_3157-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/lincoln-scaled-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/SkiptonOffice-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/AD_4nXe_w3WfcG23kkBnNvkvTt0NXzmg-ndfjHpXK2FWTYZ87uCoh0rswlaXK4uOLdhaa4B2AyoGq-7vctRg_gXNwuswmDyAfzHKIwnD1P-lB9HR31d5LThNnsqhIWgBnSN-IPzBKicpLQ.png",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Perth_office-1.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/nottinhham.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Office-Image.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/Belvoir-Chelmsford-Branch-Photo.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-4.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Belvoir-Let-Board-Image-1-4.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2025/10/Belvoir-Chelmsford-Branch-Photo.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/tilehurst-office-image-revised-scaled-2.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/cannock.jpg",
"https://www.belvoir.co.uk/wp-content/uploads/2026/01/Coventry_office_2.jpg"
        ]

    elif sys.argv[1].endswith(".txt"):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(sources)} URLs from {sys.argv[1]}\n")

    else:
        sources = [sys.argv[1]]

    print("=" * 60)
    print("  FREE Alt Text Generator  –  Powered by BLIP (local)")
    print(f"  {len(sources)} image(s) to process")
    print("=" * 60 + "\n")

    processor, model = load_model()

    start = time.time()
    results = process_sources(sources, processor, model)
    elapsed = time.time() - start

    # ── Save results ────────────────────────────────────────────────────────
    if len(sources) > 1:

        # JSON (unchanged - saves in current folder)
        output_file = "alt_texts.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nAll results saved to → {output_file}")

        # ✅ YOUR CSV PATH
        csv_file = r"C:\Users\SuryaRaghupathy\OneDrive - Nurtur Limited\Desktop\Git code import\image_alt_texts.csv"

        # ensure folder exists
        Path(csv_file).parent.mkdir(parents=True, exist_ok=True)

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["image_url", "alt_text"])
            for url, alt in results.items():
                writer.writerow([url, alt])

        print(f"CSV saved to → {csv_file}")

    # ── Summary ─────────────────────────────────────────────────────────────
    succeeded = sum(1 for v in results.values() if not v.startswith("ERROR"))
    failed    = len(results) - succeeded

    print("\n" + "=" * 60)
    print(f"  Done in {elapsed:.1f}s  |  ✅ {succeeded} succeeded  |  ❌ {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()