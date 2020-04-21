from konlpy.tag import Kkma
from konlpy.utils import pprint
from konlpy.tag import Okt
kkma = Kkma()
okt = Okt()
p = okt.nouns(u'페퍼로니피자')

print(p)