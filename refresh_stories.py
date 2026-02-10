
import asyncio
from backend.app.database import AsyncSessionLocal
from backend.app.models.story import Story, Slide
from sqlalchemy import select, delete
import uuid

async def refresh_stories():
    async with AsyncSessionLocal() as db:
        # Get existing seeded stories and update them or clear and re-add
        # For simplicity, I'll clear and add the robust version
        result = await db.execute(select(Story))
        stories = result.scalars().all()
        for s in stories:
            if s.title.get("en") in ["0% Car Loan", "Weekly Arrivals", "Service & Support"]:
                await db.execute(delete(Slide).where(Slide.story_id == s.id))
                await db.delete(s)
        
        await db.commit()

        new_stories = [
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
                    },
                    {
                        "title": {"ru": "Минимум документов", "uz": "Minimal hujjatlar", "en": "Minimal Documents"},
                        "content": {"ru": "Только паспорт и водительское удостоверение.", "uz": "Faqat pasport va haydovchilik guvohnomasi.", "en": "Only passport and driver's license required."},
                        "image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1024&q=80",
                        "button_text": {"ru": "Подать заявку", "uz": "Ariza topshirish", "en": "Apply Now"}
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
                    },
                    {
                        "title": {"ru": "BMW iX Electric", "uz": "BMW iX Electric", "en": "BMW iX Electric"},
                        "content": {"ru": "Будущее наступило. Запас хода до 600 км.", "uz": "Kelajak keldi. 600 km gacha masofa.", "en": "The future is here. Up to 600km range."},
                        "image": "https://images.unsplash.com/photo-1617788131756-3475f3a04297?auto=format&fit=crop&w=1024&q=80",
                        "button_text": {"ru": "Тест-драйв", "uz": "Test-drayv", "en": "Test Drive"}
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
                    },
                    {
                        "title": {"ru": "Оригинальные запчасти", "uz": "Original ehtiyot qismlar", "en": "Genuine Parts"},
                        "content": {"ru": "Мы используем только сертифицированные детали.", "uz": "Biz faqat sertifikatlangan qismlardan foydalanamiz.", "en": "We use only certified parts for your safety."},
                        "image": "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?auto=format&fit=crop&w=1024&q=80"
                    }
                ]
            }
        ]
        
        for s_data in new_stories:
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
        print("Successfully refreshed and expanded stories to 3 slides each.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(refresh_stories())
