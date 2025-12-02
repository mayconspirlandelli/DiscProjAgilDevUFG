
# Esse codigo funcionou, porém o Instagram bloqueia o acesso via web scraping depois de duas extrações seguidas.

import instaloader
from urllib.parse import urlparse

def get_shortcode_from_url(url: str) -> str:
    """
    Extrai o shortcode da URL de um post do Instagram.
    Ex.: https://www.instagram.com/p/SHORTCODE/ -> SHORTCODE
    """
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    # Geralmente: ['p', 'SHORTCODE'] ou ['reel', 'SHORTCODE']
    return parts[1] if len(parts) > 1 else None

def get_instagram_post_data(url: str):
    L = instaloader.Instaloader()

    shortcode = get_shortcode_from_url(url)
    if not shortcode:
        raise ValueError("URL de post inválida.")

    post = instaloader.Post.from_shortcode(L.context, shortcode)

    data = {
        "shortcode": shortcode,
        "caption": post.caption,
        "image_url": post.url,                 # thumbnail/primeira imagem
        "is_video": post.is_video,
        "likes": post.likes,
        "views": post.video_view_count if post.is_video else None,
        "date_utc": post.date_utc.isoformat()
    }
    return data

if __name__ == "__main__":
    #post_url = "https://www.instagram.com/p/XXXXXXXXXXX/"
    #post_url = "https://www.instagram.com/p/DRaKiYFDig3/?igsh=cDU0ODhjZnRjYmk0"
    #post_url = "https://www.instagram.com/p/DRaYqKWjwTm"
    post_url = "https://www.instagram.com/agencia.brasil/p/DRZ9blqgEZu/"
    info = get_instagram_post_data(post_url)
    print(info)


# $ python extrator/scraper_instagram-py
# JSON Query to graphal/query: 403 Forbidden when accessing https://www.instagram.com/graphql/query [retrying; skip with ^C] {'shortcode':
# 'DRaKiYFDig3',
# 'caption': 'PRISÃO DE BOLSONARO | Durante a audiência de custódia, realizada na tarde deste domingo (23), o ex-presidente Jair: Bolsonaro confirmou que tentou violar a tornozeleira eletrônica.Ele alegou que teve
# "certa paranoia" , na ocasião,em razão de medicamentos que tem tomado, como Pregabalina e Sertralina. In\nBolsonaro ainda afirmou que estava com "alucinação" de que tinha alguma escuta na tornozeleira e, por isso, 
# tentou abrir a tampa do equipmento. In\nApós constatar que não houve "qualquer abuso ou irregularidade" durante a prisão do ex-presidente, a juíza auxiliar Luciana Sol rrentino, que (STF) conduziu a audiência, homologou o cumprimento do mandado de prisão. \n\nNesta
# segunda-feira (24), a Primeira Turma do Supremo Tribunal Federal se reunirá para decidir sobre a questão.'
# image_url': https://scontent-iad3-1.cdninstagram.com/v/t51.2885-15/589186569_18541446991054381_1808963080068149287_n. jpg?stp=dst-jpg_e15_fr_p1080x1080_
# tt6&_nc_ht=scontent-iad3-1.cdninstagram. com&_nc_cat=1&_nc_ос=06cZ2QEcST7gu5UyPva-ek1B_gi™ZLcUclEGSOV0y2CoHG
# EoRolOWRJQdo7v_vHuZ01FwJ4&_nc_ohc=CjTdlI0eVGoQ7kNvwHV7Crx&_nc_gid=Hj5xrFawk6uZEa8V5YQI0Q&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_Afg4yWA-ReqLZzrVzRnPQIfiueqsrpsWOUR
# THeXvhrVMsw&oe=69296946&_nc_sid=d885a2',
# 'is_video': False,
# "likes': 798,
# 'views': None,
# 'date_utc': 2025-11-23T18:20:43'}



#    post_url = "https://www.instagram.com/p/DRaYD_DjwCc"

#resutlado
# $ python extrator/scraper_instagram-py
# JSON Query to graphal/query:
# 403 Forbidden when accessing https://www.instagram.com/graphql/query [retrying; skip with ^C]
# 'DRaYD_DjwCc'.
# "ASSINATURA|O presidente Lula afirmou, neste domingo (23), que o acordo comércio entre o Mercosul e a Un em 20 de dezembro. Neste semestre, o Brasil está na presidência do bloco sul-americano e Lula colocou do acordo com os europeus. In\n"É um acordo que envolve praticamente 722 milhões de habitantes e US$ 22 trilhões de Produto Interno Bruto (PIB). coisa extremamente importante, possivelmente seja o maior acordo comercial , destacou.
# In\nA União Europeia e o bloco formado pela Argentina,Paraguai e Uruguai completaram as negociações sobre o acordo em dezembro passado, cerca de 25 anos após o início das conversações. Serão firmados d
# textos: o primeiro de natureza econômica-comercial, que é de vigência provisória, e um acordo completo. \n\nA União Europeia submeteu o documento ao parl lamento europeu e aos estados-membros do bloco. Os países do Mercosul precisam fazer a mesma coisa, mas a entrada em vigor é
# ou seja, não é pre ciso esperar a aprovação dos parlamentos dos quatro estados-membros.\n\nEntenda na matéria da Agência Brasil e fique bem informado.\n\n] Foto iveira/Agência Senado Int] Foto 2: Reuters/Yves Herman', 
# image_url': https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/587809043_18405318601137423_5
# 050280717828929669_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=103&_nc_
# s7LJpfLc0A1B0TpW_aNcxmkmpkqdDS00NC0kxc&_nc_ohc=_
# _oc=Q6cZ2QFmzn7jTz_s35IAMfy03Wm4hZ4kz
# iDgP-u0P0Q7kNvwEBghbC&_nc_gid=Cx_70P_qEqIH-U3TEhLUcQ&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AfiLr-d60231G_yosW20gd
# 11NyxIYTJofh0Yi08JTye7GQ&oe=69295420&_nc_sid=d885a2',
# 'is_video':
# "likes': 347,
# "views': None,
# '2025-11-23T20:18:54' }

