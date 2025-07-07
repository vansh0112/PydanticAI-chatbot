import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

def setup_pinecone():
    """Setup and test Pinecone configuration"""
    print("🔧 Setting up Pinecone...")
    
    # Check environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    if not environment:
        raise ValueError("PINECONE_ENVIRONMENT must be set in your .env file")
    index_name = os.getenv("PINECONE_INDEX_NAME", "langchain-docs")
    
    if not api_key:
        print("❌ PINECONE_API_KEY not found in .env file")
        print("Please add your Pinecone API key to the .env file")
        return False
    
    print(f"✅ Found Pinecone configuration:")
    print(f"   Environment: {environment}")
    print(f"   Index Name: {index_name}")
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        print("✅ Pinecone initialized successfully")
        
        # List existing indexes
        indexes = pc.list_indexes().names()
        print(f"📋 Existing indexes: {indexes}")
        
        # Check if our index exists
        if index_name in indexes:
            print(f"✅ Index '{index_name}' already exists")
            
            # Get index stats
            stats = pc.describe_index(index_name)
            print(f"📊 Index stats: {stats}")
            
        else:
            print(f"⚠️  Index '{index_name}' does not exist yet")
            print("It will be created when you run the vector store setup")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Pinecone: {e}")
        return False

def create_test_index():
    """Create a test index to verify Pinecone setup"""
    print("\n🧪 Creating test index...")
    
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    if not environment:
        raise ValueError("PINECONE_ENVIRONMENT must be set in your .env file")
    index_name = os.getenv("PINECONE_INDEX_NAME", "langchain-docs")
    
    try:
        pc = Pinecone(api_key=api_key)
        
        # Create index if it doesn't exist
        if index_name not in pc.list_indexes().names():
            print(f"Creating index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",  # or "gcp"
                    region=environment  # e.g., "us-east-1"
                )
            )
            print(f"✅ Index '{index_name}' created successfully")
        else:
            print(f"✅ Index '{index_name}' already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Pinecone Setup for LangChain Documentation Chatbot")
    print("=" * 60)
    
    # Setup Pinecone
    if setup_pinecone():
        print("\n✅ Pinecone setup completed successfully!")
        
        # Ask if user wants to create test index
        response = input("\nDo you want to create the index now? (y/n): ").lower()
        if response == 'y':
            if create_test_index():
                print("\n🎉 Pinecone is ready to use!")
                print("\nNext steps:")
                print("1. Run: python scraper.py")
                print("2. Run: python vector_store.py")
                print("3. Run: python rag_chatbot.py")
            else:
                print("\n❌ Failed to create index")
        else:
            print("\n📝 Index will be created automatically when needed")
    else:
        print("\n❌ Pinecone setup failed")
        print("\nPlease check your .env file and try again")

if __name__ == "__main__":
    main() 