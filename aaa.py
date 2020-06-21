from konlpy.tag import Kkma
from konlpy.utils import pprint
from konlpy.tag import Okt
kkma = Kkma()
okt = Okt()
inputD = '곤드레 간장게장정식'
p = okt.pos(inputD)
p2 = okt.nouns(inputD)
print('입력 문자 :',inputD)
print('형태소 분석  :',p)
print('명사구 추출  :',p2)