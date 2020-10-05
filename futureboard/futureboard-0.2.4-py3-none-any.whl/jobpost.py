import random
from pathlib import Path

from futureboard.thai import check_thai_sentence_length
from PIL import Image, ImageDraw, ImageFont


def draw_image(
    job_position: str,
    employer_name: str,
    province: str,
    salary_and_unit: str,
    *,
    special=False,
    horizon=True,
) -> Image:
    bg_selection = random.randint(0, 3)

    path = Path(__file__).parent.parent / Path("assets/")
    if horizon:
        path = path / "horizon"

    if special:
        path = path / "special.png"
    else:
        path = path / f"job{bg_selection}.png"

    bg_image = Image.open(path)
    draw = ImageDraw.Draw(bg_image)
    if not horizon:
        v1 = 75
        v2 = 55
        v3 = 50

        thredhold1 = 20
        JobPosition_length = check_thai_sentence_length(job_position)
        if JobPosition_length > thredhold1:
            job_position = job_position[0 : thredhold1 + 10] + "..."
            v1 = 50

        thredhold2 = 24
        EmployerName_length = check_thai_sentence_length(employer_name)
        if EmployerName_length > thredhold2:
            employer_name = employer_name[0 : thredhold2 + 15] + "..."
            v2 = 40

        font1 = ImageFont.truetype(
            str(Path(__file__).parent.parent / r"assets/SukhumvitSet-Bold.ttf"), v1
        )
        font2 = ImageFont.truetype(
            str(Path(__file__).parent.parent / r"assets/SukhumvitSet-Bold.ttf"), v2
        )
        font3 = ImageFont.truetype(
            str(Path(__file__).parent.parent / r"assets/SukhumvitSet-Light.ttf"), v3
        )

        if special:
            indentation = 40
        else:
            indentation = 20

        draw.text((indentation, 220), job_position, font=font1, fill=(64, 4, 14, 255))
        draw.text((indentation, 320), employer_name, font=font2, fill=(64, 4, 14, 255))
        draw.text(
            (indentation, 640),
            "สถานที่: " + province,
            font=font3,
            fill=(64, 4, 14, 255),
        )

        # salary_and_unit value proccess
        draw.text(
            (indentation, 700),
            f"รายได้ขั้นต้น: {salary_and_unit}",
            font=font3,
            fill=(64, 4, 14, 255),
        )
    else:
        v1 = 130
        v2 = 70
        v3 = 60

        font1 = ImageFont.truetype(
            str(Path(__file__).parent.parent / r"assets/SukhumvitSet-Bold.ttf"), v1
        )
        font2 = ImageFont.truetype(
            str(Path(__file__).parent.parent / r"assets/SukhumvitSet-Bold.ttf"), v2
        )
        font3 = ImageFont.truetype(
            str(Path(__file__).parent.parent / r"assets/SukhumvitSet-Light.ttf"), v3
        )

        thredhold1 = 15
        JobPosition_length = check_thai_sentence_length(job_position)
        if JobPosition_length > thredhold1:
            job_position = job_position[0 : thredhold1 + 10] + "..."
            v1 = 90

        thredhold2 = 20
        EmployerName_length = check_thai_sentence_length(employer_name)
        if EmployerName_length > thredhold2:
            employer_name = employer_name[0 : thredhold2 + 15] + "..."
            v2 = 50

        draw.text((20, 120), job_position, font=font1, fill=(64, 4, 14, 255))
        draw.text((20, 320), employer_name, font=font2, fill=(64, 4, 14, 255))
        draw.text(
            (20, 460),
            "สถานที่: " + province,
            font=font3,
            fill=(64, 4, 14, 255),
        )

        # salary value proccess
        draw.text(
            (20, 540),
            f"รายได้ขั้นต่ำ: {salary_and_unit}",
            font=font3,
            fill=(64, 4, 14, 255),
        )

    return bg_image
