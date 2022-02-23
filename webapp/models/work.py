from django.db import models
from ..models.picture import Picture
from ..models.theme import Theme
from ..models.artist import Artist

# Create your models here.
class Work(models.Model):
    models.AutoField(primary_key=True)  # 작품 id
    title_kor = models.CharField(max_length=255, null=True)  # 작품 한글명
    title_eng = models.CharField(max_length=255, null=True)  # 작품 영문명
    artist_id = models.ForeignKey(Artist, on_delete=models.PROTECT, null=True)  # 작가 id
    make_year = models.CharField(max_length=255, null=True)  # 제작 연도
    edition_yn = models.BooleanField(null=True)  # 에디션 여부
    edtion_num = models.CharField(max_length=255, null=True)  # 에디션 넘버(스트링)
    material_kor = models.CharField(max_length=255, null=True)  # 재료 한글명
    material_eng = models.CharField(max_length=255, null=True)  # 재료 영문명
    kind = models.CharField(max_length=255, null=True)  # 작품 종류
    exhibition = models.CharField(max_length=255, null=True)  # 전시정보
    frame_yn = models.BooleanField(null=True)  # 액자 여부
    sign_yn = models.BooleanField(null=True)  # 싸인 여부
    status = models.CharField(max_length=255, null=True)  # 상태
    guarantee_yn = models.BooleanField(null=True)  # 보증서 유무
    img_url = models.CharField(max_length=255, null=True)  # 이미지 경로
    picture_id = models.ForeignKey(Picture, on_delete=models.PROTECT, null=True)  # 회화 코드
    theme_id = models.ForeignKey(Theme, on_delete=models.PROTECT, null=True)  # 주제 코드
    size_num = models.CharField(max_length=255, null=True)  # 호 수
