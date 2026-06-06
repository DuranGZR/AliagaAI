import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.content import Gallery, GalleryImage

async def check():
    async with async_session() as session:
        galleries = (await session.execute(select(Gallery))).scalars().all()
        print(f"Total Galleries: {len(galleries)}")
        for g in galleries:
            images = (await session.execute(select(GalleryImage).where(GalleryImage.gallery_id == g.id))).scalars().all()
            print(f"Gallery ID={g.id}, Title='{g.title}', ImagesCount={len(images)}")
            for img in images:
                print(f"  Image URL: {img.image_url}")

if __name__ == '__main__':
    asyncio.run(check())
