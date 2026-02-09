
import asyncio
import os
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.story import Story, StorySlide

async def fix_images():
    async with AsyncSessionLocal() as db:
        print("🔍 Checking stories and slides...")
        
        # Get all stories
        result = await db.execute(select(Story))
        stories = result.scalars().all()
        
        # Get all slides
        result = await db.execute(select(StorySlide))
        slides = result.scalars().all()
        
        # Image filenames found in uploads/stories
        available_images = [
            "story_20260209175606_5b4728b2.jpeg",
            "story_20260209175908_460e31c7.jpeg",
            "story_20260209180107_ef2377b5.jpeg",
            "story_20260209180837_65abc010.jpeg"
        ]
        
        print(f"🖼 Found {len(available_images)} available images.")
        
        # Update Stories
        for i, story in enumerate(stories):
            if i < len(available_images):
                img_path = f"http://localhost:8000/uploads/stories/{available_images[i]}"
                print(f"📝 Updating story {story.id}: {story.preview_image} -> {img_path}")
                story.preview_image = img_path
        
        # Update Slides
        for i, slide in enumerate(slides):
            if i < len(available_images):
                img_path = f"http://localhost:8000/uploads/stories/{available_images[i]}"
                print(f"📝 Updating slide {slide.id}: {slide.image_url} -> {img_path}")
                slide.image_url = img_path
                
        await db.commit()
        print("✅ Database updated successfully!")

if __name__ == "__main__":
    asyncio.run(fix_images())
