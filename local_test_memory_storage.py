import os
from simple_memory import SimpleLumiMemory
import vertexai
from vertexai.preview.generative_models import GenerativeModel as VertexModel

# 設定資料庫連線字串
# 請確保這是您正確的 Railway 資料庫連線字串
DATABASE_URL = "postgres://postgres:eZR43clAm~RDR.0MPV_TAIfr8aVMTool@trolley.proxy.rlwy.net:34472/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

# 模擬的記憶資料
USER_ID = "local_test_user_001"
USER_MESSAGE = "這是一條來自本機的測試訊息。"
LUMI_RESPONSE = "好的，我已收到您的測試訊息。"
EMOTION_TAG = "neutral"

def test_local_memory_storage():
    print("嘗試初始化 Vertex AI 嵌入模型...")
    try:
        # 確保 GOOGLE_APPLICATION_CREDENTIALS 環境變數已設定
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            print("錯誤：GOOGLE_APPLICATION_CREDENTIALS 環境變數未設定。")
            print("請先設定您的服務帳號金鑰路徑，例如：export GOOGLE_APPLICATION_CREDENTIALS=\"YOUR_JSON_KEY_FILE_PATH\"")
            return

        # 初始化 Vertex AI
        vertexai.init(project=os.getenv('VERTEX_AI_PROJECT_ID', 'cool-ruler-419911'), location=os.getenv('VERTEX_AI_LOCATION', 'us-central1'))
        embedding_model = VertexModel('text-embedding-004')
        print("Vertex AI 嵌入模型初始化成功。")

        print("嘗試初始化記憶管理器...")
        memory_manager = SimpleLumiMemory(embedding_model)
        if memory_manager.conn:
            print("記憶管理器初始化成功，嘗試儲存記憶...")
            memory_manager.store_conversation_memory(USER_ID, USER_MESSAGE, LUMI_RESPONSE, EMOTION_TAG)
            print("記憶儲存測試完成。請檢查您的資料庫確認資料是否已寫入。")
        else:
            print("記憶管理器初始化失敗，無法連線到資料庫。")
    except Exception as e:
        print(f"執行測試時發生錯誤: {e}")

if __name__ == "__main__":
    test_local_memory_storage()