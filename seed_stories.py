
import asyncio
from uuid import uuid4
from sqlalchemy import select
from backend.app.database import AsyncSessionLocal
from backend.app.models.story import Story, Slide

async def seed_stories():
    async with AsyncSessionLocal() as db:
        # Check if stories already exist
        result = await db.execute(select(Story))
        if result.scalars().first():
            print("Stories already exist, skipping seed.")
            return

        print("Seeding interesting stories...")

        # Story 1: Customs Savings
        story1 = Story(
            id=uuid4(),
            title={"ru": "Выгода до $2000", "uz": "$2000 gacha foyda", "en": "Save up to $2000"},
            preview_image="http://localhost:8000/uploads/stories/customs.png",
            order=1,
            is_active=True
        )
        db.add(story1)
        
        slide1_1 = Slide(
            story_id=story1.id,
            title={"ru": "Экономьте на таможне", "uz": "Божхонада тежанг", "en": "Save on Customs"},
            content={"ru": "Мы знаем как привезти авто с максимальной выгодой.", "uz": "Биз машинани максимал фойда билан олиб келишни биламиз.", "en": "We know how to bring a car with maximum benefit."},
            image_url="http://localhost:8000/uploads/stories/customs.png",
            button_text={"ru": "Рассчитать", "uz": "Ҳисоблаш", "en": "Calculate"},
            button_link="stlapp://calculator",
            order=1
        )
        db.add(slide1_1)

        # Story 2: BYD Electric
        story2 = Story(
            id=uuid4(),
            title={"ru": "Новинки BYD", "uz": "BYD янгиликлари", "en": "BYD New Arrivals"},
            preview_image="http://localhost:8000/uploads/stories/byd.png",
            order=2,
            is_active=True
        )
        db.add(story2)
        
        slide2_1 = Slide(
            story_id=story2.id,
            title={"ru": "Электрическое будущее", "uz": "Электр келажаги", "en": "Electric Future"},
            content={"ru": "Новые модели BYD уже доступны к заказу.", "uz": "Янги BYD моделлари буюртма учун мавжуд.", "en": "New BYD models are available for order."},
            image_url="http://localhost:8000/uploads/stories/byd.png",
            button_text={"ru": "В каталог", "uz": "Каталогга", "en": "To Catalog"},
            button_link="stlapp://catalog?brand=BYD",
            order=1
        )
        db.add(slide2_1)

        # Story 3: How to order
        story3 = Story(
            id=uuid4(),
            title={"ru": "Как заказать?", "uz": "Қандай буюртма бериш керак?", "en": "How to order?"},
            preview_image="http://localhost:8000/uploads/stories/order.png",
            order=3,
            is_active=True
        )
        db.add(story3)
        
        slide3_1 = Slide(
            story_id=story3.id,
            title={"ru": "Простой выбор", "uz": "Оддий танлов", "en": "Simple Choice"},
            content={"ru": "Выберите авто, оставьте заявку, а остальное мы возьмем на себя.", "uz": "Машинани танланг, ариза қолдиринг, қолганини биз ҳал қиламиз.", "en": "Choose a car, leave an application, and we will take care of the rest."},
            image_url="http://localhost:8000/uploads/stories/order.png",
            button_text={"ru": "Инструкция", "uz": "Йўриқнома", "en": "Instructions"},
            button_link="stlapp://help/order",
            order=1
        )
        db.add(slide3_1)

        await db.commit()
        print("Success! Stories seeded.")

if __name__ == "__main__":
    import sys
    import os
    # Add project root to sys.path for imports
    sys.path.append(os.getcwd())
    asyncio.run(seed_stories())
