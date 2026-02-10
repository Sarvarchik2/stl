
import asyncio
from backend.app.database import AsyncSessionLocal
from backend.app.models.car import Car
from backend.app.models.story import Story, Slide
from sqlalchemy import select, update, delete
import uuid

async def seed_extra_data():
    async with AsyncSessionLocal() as db:
        # 1. Update Cars with more photos
        # Interior and Detail placeholders from Unsplash (High quality)
        car_interior = "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1024&q=80"
        car_dash = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1024&q=80"
        car_wheel = "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1024&q=80"
        ev_charge = "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1024&q=80"
        
        result = await db.execute(select(Car))
        cars = result.scalars().all()
        
        for car in cars:
            if not car.photos or len(car.photos) < 3:
                # Add at least 3 photos
                current = car.photos or []
                if not current and car.image_url:
                    current = [car.image_url]
                
                # Append high quality placeholders if needed
                if len(current) < 2:
                    current.append(car_interior)
                if len(current) < 3:
                    current.append(car_dash if car.brand != "BYD" else ev_charge)
                
                car.photos = current
        
        # 2. Seed Stories
        # Clear existing stories to avoid duplicates in this seed
        # await db.execute(delete(Slide))
        # await db.execute(delete(Story))
        
        stories_data = [
            {
                "title": {"ru": "Автокредит 0%", "uz": "Avtokredit 0%", "en": "0% Car Loan"},
                "preview": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=800&q=80",
                "slides": [
                    {
                        "title": {"ru": "Мечта стала ближе", "uz": "Orzu yaqinlashdi", "en": "Your dream is closer"},
                        "content": {"ru": "Оформите кредит на выгодных условиях за 15 минут.", "uz": "Imtiyozli shartlarda 15 daqiqada kredit oling.", "en": "Get a loan on favorable terms in 15 minutes."},
                        "image": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1024&q=80",
                        "button_text": {"ru": "Узнать больше", "uz": "Batafsil", "en": "Learn more"},
                        "link": "/calculator"
                    },
                    {
                        "title": {"ru": "Без первоначального взноса", "uz": "Boshlang'ich to'lovsiz", "en": "No down payment"},
                        "content": {"ru": "Специальное предложение для моделей Chevrolet этого месяца.", "uz": "Shu oyda Chevrolet modellari uchun maxsus taklif.", "en": "Special offer for Chevrolet models this month."},
                        "image": "https://images.unsplash.com/photo-1553440569-bcc63803a83d?auto=format&fit=crop&w=1024&q=80",
                        "button_text": {"ru": "Рассчитать", "uz": "Hisoblash", "en": "Calculate"}
                    }
                ]
            },
            {
                "title": {"ru": "Новинки недели", "uz": "Hafta yangiliklari", "en": "Weekly Arrivals"},
                "preview": "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?auto=format&fit=crop&w=800&q=80",
                "slides": [
                    {
                        "title": {"ru": "Toyota Camry 2025", "uz": "Toyota Camry 2025", "en": "Toyota Camry 2025"},
                        "content": {"ru": "Новый дизайн и гибридная мощность уже в наличии.", "uz": "Yangi dizayn va gibrid quvvat allaqachon mavjud.", "en": "New design and hybrid power now in stock."},
                        "image": "http://127.0.0.1:8000/uploads/cars/camry_1.png",
                        "button_text": {"ru": "Смотреть", "uz": "Ko'rish", "en": "View"},
                        "link": "/cars"
                    },
                    {
                        "title": {"ru": "Chevrolet Tahoe", "uz": "Chevrolet Tahoe", "en": "Chevrolet Tahoe"},
                        "content": {"ru": "Мощь и комфорт для всей семьи.", "uz": "Butun oila uchun quvvat va qulaylik.", "en": "Power and comfort for the whole family."},
                        "image": "http://127.0.0.1:8000/uploads/cars/tahoe_1.png",
                        "button_text": {"ru": "Забронировать", "uz": "Band qilish", "en": "Reserve"}
                    }
                ]
            },
            {
                "title": {"ru": "Сервисное обслуживание", "uz": "Servis xizmati", "en": "Service & Support"},
                "preview": "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?auto=format&fit=crop&w=800&q=80",
                "slides": [
                    {
                        "title": {"ru": "Гарантия качества", "uz": "Sifat kafolati", "en": "Quality Assurance"},
                        "content": {"ru": "Ваш автомобиль в надежных руках наших мастеров.", "uz": "Avtomobilingiz ustalarimizning ishonchli qo'lida.", "en": "Your car is in safe hands with our masters."},
                        "image": "https://images.unsplash.com/photo-1530046339160-ce3e5b0c7a2f?auto=format&fit=crop&w=1024&q=80"
                    },
                    {
                        "title": {"ru": "Запись на ТО", "uz": "TX uchun yozilish", "en": "Book Service"},
                        "content": {"ru": "Запишитесь через приложение и получите скидку 10%.", "uz": "Ilova orqali yoziling va 10% chegirma oling.", "en": "Book via app and get 10% discount."},
                        "image": "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1024&q=80",
                        "button_text": {"ru": "Записаться", "uz": "Yozilish", "en": "Book Now"}
                    }
                ]
            }
        ]
        
        for s_data in stories_data:
            story = Story(
                title=s_data["title"],
                preview_image=s_data["preview"],
                order=0,
                is_active=True
            )
            db.add(story)
            await db.flush()
            
            for i, sl_data in enumerate(s_data["slides"]):
                slide = Slide(
                    story_id=story.id,
                    title=sl_data["title"],
                    content=sl_data["content"],
                    button_text=sl_data.get("button_text"),
                    button_link=sl_data.get("link"),
                    image_url=sl_data["image"],
                    order=i
                )
                db.add(slide)
        
        await db.commit()
        print("Successfully updated car photos and seeded stories.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(seed_extra_data())
