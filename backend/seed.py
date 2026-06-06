import asyncio
from datetime import date, timedelta
from sqlalchemy import select
from app.database import async_session
from app.models.content import Gallery, GalleryImage, Event

async def seed():
    async with async_session() as session:
        # Check if test gallery exists
        g_stmt = select(Gallery).where(Gallery.slug == 'aliaga-yaz-senlikleri')
        g_result = await session.execute(g_stmt)
        g = g_result.scalars().first()

        cover_url = 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80'

        if g:
            g.cover_image_url = cover_url
            print('Mevcut galeri güncellendi.')
        else:
            g = Gallery(
                title='Aliağa Yaz Şenlikleri (Test)', 
                slug='aliaga-yaz-senlikleri', 
                cover_image_url=cover_url,
                source_url='https://www.aliaga.bel.tr', 
                publish_date=date.today()
            )
            session.add(g)
            await session.flush()
            print('Yeni test galerisi eklendi.')
        
        # Sync gallery images
        # Clear existing images for this gallery to avoid duplication
        del_stmt = select(GalleryImage).where(GalleryImage.gallery_id == g.id)
        del_result = await session.execute(del_stmt)
        for img in del_result.scalars().all():
            await session.delete(img)
        await session.flush()

        gi1 = GalleryImage(
            gallery_id=g.id, 
            image_url='https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80', 
            description='Sahil Görünümü'
        )
        gi2 = GalleryImage(
            gallery_id=g.id, 
            image_url='https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=600&q=80', 
            description='Ağapark Plajı'
        )
        session.add(gi1)
        session.add(gi2)
        
        # Event
        e_stmt = select(Event).where(Event.title == 'Aliağa Açık Hava Konseri')
        e_result = await session.execute(e_stmt)
        e = e_result.scalars().first()

        event_data = {
            'title': 'Aliağa Açık Hava Konseri', 
            'description': 'Belediyemizin düzenlediği yaz konserine tüm halkımız davetlidir.', 
            'event_date': date.today() + timedelta(days=2), 
            'location': 'Avcı Ramadan Çocuk Oyun ve Rekreasyon Alanı', 
            'category': 'Konser',
            'image_url': 'https://images.unsplash.com/photo-1470229722913-7c092dbbba3a?auto=format&fit=crop&w=600&q=80'
        }

        if e:
            for k, v in event_data.items():
                setattr(e, k, v)
            print('Mevcut etkinlik güncellendi.')
        else:
            e = Event(**event_data)
            session.add(e)
            print('Yeni test etkinliği eklendi.')
        
        await session.commit()
        print('Veritabanına test verileri senkronize edildi.')

if __name__ == '__main__':
    asyncio.run(seed())

