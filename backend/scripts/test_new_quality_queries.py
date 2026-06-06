import asyncio
import sys

# Set utf-8 output encoding for windows command prompt
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from app.database import async_session
from app.services.agent.service import AgenticRAGService

async def run_tests():
    agent = AgenticRAGService()
    
    test_queries = [
        "aliağay alaşımı nasıl sağlıcam",
        "aliağanın tarihini anlatırmısın bana",
        "aliağada gezilecek nereler var"
    ]
    
    async with async_session() as session:
        for idx, q in enumerate(test_queries, 1):
            print(f"\n========================================")
            print(f"TEST {idx}: {q}")
            print(f"========================================")
            try:
                resp = await agent.run(session=session, user_message=q)
                print(f"INTENT: {resp.intent}")
                print(f"METHOD: {resp.search_method}")
                print(f"SOURCES: {[s.title for s in resp.sources]}")
                print(f"ANSWER:\n{resp.answer}")
            except Exception as e:
                print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
