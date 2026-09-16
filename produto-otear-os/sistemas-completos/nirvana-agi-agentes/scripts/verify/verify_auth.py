
import httpx
import asyncio
import os

async def verify():
    url = "http://localhost:8000/api/chat"
    payload = {"message": "hi"}
    
    print("1. Testing WITHOUT password...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            print(f"   Status: {resp.status_code} (Expected 403)")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Testing WITH WRONG password...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers={"x-admin-password": "wrong"})
            print(f"   Status: {resp.status_code} (Expected 403)")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n3. Testing WITH CORRECT password...")
    try:
        async with httpx.AsyncClient() as client:
            # Assuming server needs restart or manual intervention to pick up .env, 
            # but we can try sending what we expect
            resp = await client.post(url, json=payload, headers={"x-admin-password": "change-me"})
            print(f"   Status: {resp.status_code} (Expected 200)")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
