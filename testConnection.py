"""
Run this script FIRST to diagnose MongoDB issues.

Usage:
    python test_connection.py

It will tell you exactly what's working and what's not.
"""

import asyncio
import sys

# ── Load .env manually ──
try:
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                import os
                os.environ[key.strip()] = val.strip()
except FileNotFoundError:
    print("⚠ No .env file found! Create one from .env.example")
    sys.exit(1)

from motor.motor_asyncio import AsyncIOMotorClient


async def test():
    uri = None
    db_name = None
    col_name = None

    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGO_URI="):
                    uri = line.split("=", 1)[1]
                elif line.startswith("MONGO_DB="):
                    db_name = line.split("=", 1)[1]
                elif line.startswith("MONGO_COLLECTION="):
                    col_name = line.split("=", 1)[1]
    except:
        pass

    import os
    uri = os.environ.get("MONGO_URI", uri)
    db_name = os.environ.get("MONGO_DB", db_name or "test")
    col_name = os.environ.get("MONGO_COLLECTION", col_name or "customerChats")

    print("=" * 60)
    print("  LEAD API — CONNECTION DIAGNOSTIC")
    print("=" * 60)

    # Mask URI for display
    masked = uri[:30] + "..." if uri and len(uri) > 30 else uri
    print(f"\n📍 URI: {masked}")
    print(f"📍 Database: {db_name}")
    print(f"📍 Collection: {col_name}")

    # ── Step 1: Connect ──
    print(f"\n{'─' * 40}")
    print("STEP 1: Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        print("  ✅ Connection successful!")
    except Exception as e:
        print(f"  ❌ Connection FAILED: {e}")
        print("\n  Possible fixes:")
        print("    - Check your MONGO_URI in .env")
        print("    - Make sure your IP is whitelisted in Atlas Network Access")
        print("    - Try 0.0.0.0/0 in Atlas to allow all IPs (for testing)")
        return

    # ── Step 2: List databases ──
    print(f"\n{'─' * 40}")
    print("STEP 2: Listing databases...")
    try:
        dbs = await client.list_database_names()
        print(f"  ✅ Available databases: {dbs}")
        if db_name not in dbs:
            print(f"  ⚠️  WARNING: '{db_name}' NOT in database list!")
            print(f"     Your .env says MONGO_DB={db_name}")
            print(f"     Available: {dbs}")
            print(f"     → Fix MONGO_DB in your .env file")
    except Exception as e:
        print(f"  ❌ Cannot list databases: {e}")

    # ── Step 3: List collections ──
    print(f"\n{'─' * 40}")
    print(f"STEP 3: Checking database '{db_name}'...")
    db = client[db_name]
    try:
        cols = await db.list_collection_names()
        print(f"  ✅ Collections in '{db_name}': {cols}")
        if col_name not in cols:
            print(f"  ⚠️  WARNING: '{col_name}' NOT found!")
            print(f"     Your .env says MONGO_COLLECTION={col_name}")
            print(f"     Available: {cols}")
            print(f"     → Fix MONGO_COLLECTION in your .env file")
            return
    except Exception as e:
        print(f"  ❌ Cannot list collections: {e}")
        return

    # ── Step 4: Count documents ──
    print(f"\n{'─' * 40}")
    print(f"STEP 4: Counting documents in '{col_name}'...")
    col = db[col_name]
    try:
        total = await col.count_documents({})
        print(f"  ✅ Total documents: {total}")
        if total == 0:
            print("  ⚠️  Collection is EMPTY — no data to fetch!")
            return
    except Exception as e:
        print(f"  ❌ Count failed: {e}")
        return

    # ── Step 5: Inspect first document ──
    print(f"\n{'─' * 40}")
    print("STEP 5: Inspecting first document...")
    doc = await col.find_one({})
    if doc:
        doc.pop("_id", None)
        keys = list(doc.keys())
        print(f"  ✅ Document keys: {keys}")

        # Check sessionId
        sid = doc.get("sessionId")
        print(f"  📱 sessionId: {sid} (type: {type(sid).__name__})")

        # Check leadAnalysed
        la = doc.get("leadAnalysed")
        print(f"  📋 leadAnalysed: {la} (type: {type(la).__name__})")

        # Check messageLength
        ml = doc.get("messageLength")
        print(f"  💬 messageLength: {ml}")

        # Check analysedAt
        aa = doc.get("analysedAt")
        print(f"  🕐 analysedAt: {aa}")

        # Check output (THE KEY FIELD)
        output = doc.get("output")
        print(f"\n  📦 output type: {type(output).__name__}")
        if isinstance(output, dict):
            print(f"  📦 output keys: {list(output.keys())}")
            print(f"  📦 output.intent: {output.get('intent')}")
            print(f"  📦 output.qualified: {output.get('qualified')}")
            print(f"  📦 output.confidence: {output.get('confidence')}")
            print(f"  📦 output.signals: {output.get('signals')}")
            print(f"  📦 output.summary: {output.get('summary')}")
        elif isinstance(output, list):
            print(f"  📦 output is a list with {len(output)} items")
            if len(output) == 0:
                print("  📦 output is [] (empty) — this doc has no analysis yet")
        else:
            print(f"  📦 output value: {output}")

        # Check messages structure
        msgs = doc.get("messages", [])
        print(f"\n  💬 messages count: {len(msgs)}")
        if len(msgs) > 0:
            first_msg = msgs[0]
            print(f"  💬 first message type: {first_msg.get('type')}")
            data = first_msg.get("data", {})
            if isinstance(data, dict):
                print(f"  💬 first message data.content: {str(data.get('content', ''))[:80]}...")
    else:
        print("  ❌ No documents found!")

    # ── Step 6: Count analyzed docs ──
    print(f"\n{'─' * 40}")
    print("STEP 6: Checking analyzed documents...")

    analyzed = await col.count_documents({"leadAnalysed": True})
    print(f"  leadAnalysed=True: {analyzed} documents")

    analyzed_str = await col.count_documents({"leadAnalysed": "true"})
    if analyzed_str > 0:
        print(f"  ⚠️  leadAnalysed='true' (string): {analyzed_str} documents")
        print("     → Your leadAnalysed field is stored as STRING not BOOLEAN!")

    # Count docs with output as object
    with_output = 0
    without_output = 0
    cursor = col.find({}).limit(200)
    async for d in cursor:
        o = d.get("output")
        if isinstance(o, dict) and len(o) > 0:
            with_output += 1
        else:
            without_output += 1

    print(f"  With analysis output (dict): {with_output}")
    print(f"  Without output (empty/list): {without_output}")

    # ── Summary ──
    print(f"\n{'=' * 60}")
    if with_output > 0:
        print("  ✅ EVERYTHING LOOKS GOOD!")
        print(f"     {with_output} leads ready to display.")
        print(f"     Start the API: uvicorn main:app --reload")
    elif analyzed > 0:
        print("  ⚠️  Documents are analyzed but output field is empty.")
        print("     Check your n8n workflow — the output might not be saving.")
    else:
        print("  ⚠️  No analyzed documents found.")
        print("     Run your n8n workflow first to analyze some chats.")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    asyncio.run(test())