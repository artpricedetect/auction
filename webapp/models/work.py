from django.db import models

YES_NO_CHOICES = (("1", "YES"), ("2", "NO"))
# Create your models here.
class Picture(models.Model):
    models.AutoField(primary_key=True)  # 회화 id (유화, 조각, 수채화, 와인)
    picture_name = models.CharField(max_length=255, unique=True)


class Theme(models.Model):
    models.AutoField(primary_key=True)  # 인물, 풍경, 해경, 정방형
    theme_name = models.CharField(max_length=255, unique=True)


class Unit(models.Model):
    models.AutoField(primary_key=True)  # 단위 코드
    unit_name = models.CharField(max_length=255, unique=True)


class Work(models.Model):
    models.AutoField(primary_key=True)  # 작품 id
    title_kor = models.CharField(max_length=255, null=True)  # 작품 한글명
    title_eng = models.CharField(max_length=255, null=True)  # 작품 영문명
    artist_id = models.ForeignKey(Artist, on_delete=models.PROTECT, null=False)  # 작가 id
    make_year = models.CharField(max_length=255, null=True)  # 제작 연도
    edition_yn = models.BooleanField(null=True)  # 에디션 여부
    edtion_num = models.CharField(max_length=255, null=True)  # 에디션 넘버(스트링)
    material_kor = models.CharField(max_length=255, null=True)  # 재료 한글명
    material_eng = models.CharField(max_length=255, null=True)  # 재료 영문명
    kind = models.CharField(max_length=255, null=True)  # 작품 종류
    exhibition = models.CharField(max_length=255, null=True)  # 전시정보
    frame_yn = models.BooleanField(null=True)  # 액자 여부
    sign_yn = models.CharField(max_length=2, choices=YES_NO_CHOICES, null=True)  # 싸인 여부
    status = models.CharField(max_length=255, null=True)  # 상태
    guarantee_yn = models.BooleanField(null=True)  # 보증서 유무
    img_url = models.CharField(max_length=255, null=True)  # 이미지 경로
    picture_id = models.ForeignKey(
        Picture, on_delete=models.PROTECT, null=True
    )  # 회화 코드
    theme_id = models.ForeignKey(Theme, on_delete=models.PROTECT, null=True)  # 주제 코드
    size_num = models.CharField(max_length=255, null=True)  # 호 수


class WorkSize(models.Model):
    work_id = models.ForeignKey(
        Work, primary_key=True, on_delete=models.PROTECT, null=False
    )  # 작품 번호
    unit_id = models.ForeignKey(Unit, on_delete=models.PROTECT, null=False)  # 단위 id
    size1 = models.CharField(max_length=255, null=True)  # 크기1 (height)
    size2 = models.CharField(max_length=255, null=True)  # 크기2 (width)
    size3 = models.CharField(max_length=255, null=True)  # 크기3 (depth)
    canvas_yn = models.BooleanField(null=True)  # 캔버스 여부
    diam_yn = models.BooleanField(null=True)  # 지름 여부
    prefix = models.CharField(max_length=255, null=True)  # 접두어
    suffix = models.CharField(max_length=255, null=True)  # 접미어
    mix_code = models.CharField(max_length=255, null=True)  # 믹스 코드..? (height로 적혀있음)
    canvas_ext_yn = models.BooleanField(null=True)  # 캔버스 EXT 여부 
