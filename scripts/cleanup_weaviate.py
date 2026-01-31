"""
Weaviate Database Cleanup Script (v4 Client)
Removes all existing collections/classes to start fresh
"""

import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc

# Weaviate configuration
WEAVIATE_URL = "wdrd8zyt4ewlcqwk0661w.c0.us-west3.gcp.weaviate.cloud"
WEAVIATE_API_KEY = "NlBmR0ZsWVNuV3VLUEFxd19sOFVZSm1tVTl5QnB4MUJRcUxhYlZYd1k5SmJyT3gwaFNaQW9KUGZicDAwPV92MjAw"

def cleanup_weaviate():
    """Delete all existing collections in Weaviate"""

    print("[*] Connecting to Weaviate cluster...")
    print(f"    URL: {WEAVIATE_URL}")

    client = None
    try:
        # Connect to Weaviate (v4 client) - skip initial metadata check
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
            skip_init_checks=True  # Skip meta endpoint check
        )

        print("[SUCCESS] Connected successfully!\n")

        # Get all existing collections
        collections = client.collections.list_all()

        if not collections:
            print("[SUCCESS] Database is already clean - no collections found")
            return True

        print(f"[INFO] Found {len(collections)} existing collections:")
        for collection_name in collections.keys():
            print(f"       - {collection_name}")

        print("\n[*] Deleting all collections...")

        # Delete each collection
        for collection_name in collections.keys():
            try:
                client.collections.delete(collection_name)
                print(f"       [SUCCESS] Deleted: {collection_name}")
            except Exception as e:
                print(f"       [ERROR] Failed to delete {collection_name}: {str(e)}")

        print("\n[SUCCESS] Weaviate database cleanup complete!")
        print("          Database is now empty and ready for fresh setup\n")

        return True

    except Exception as e:
        print(f"\n[ERROR] Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  WEAVIATE DATABASE CLEANUP")
    print("=" * 60)
    print()

    success = cleanup_weaviate()

    if success:
        print("\n" + "=" * 60)
        print("  [SUCCESS] CLEANUP SUCCESSFUL")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  [ERROR] CLEANUP FAILED")
        print("=" * 60)
