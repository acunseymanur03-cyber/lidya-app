from sqlalchemy.orm import Session
from database import SessionLocal, SentimentRecord, User

# MCP Standardına Uygun Veritabanı ve Model Araçları (Tools)
class LidyaMCPTools:
    
    @staticmethod
    def list_recent_sentiments(limit: int = 5) -> list:
        """Veritabanındaki son duygu analizi kayıtlarını listeler (MCP Tool)."""
        db: Session = SessionLocal()
        try:
            records = db.query(SentimentRecord).order_by(SentimentRecord.id.desc()).limit(limit).all()
            return [{"id": r.id, "text": r.text, "sentiment": r.sentiment, "date": str(r.created_at)} for r in records]
        finally:
            db.close()

    @staticmethod
    def get_system_stats() -> dict:
        """Sistemdeki toplam analiz ve kullanıcı istatistiklerini getirir (MCP Tool)."""
        db: Session = SessionLocal()
        try:
            total_sentiments = db.query(SentimentRecord).count()
            total_users = db.query(User).count()
            return {
                "total_sentiments": total_sentiments,
                "total_users": total_users,
                "status": "healthy"
            }
        finally:
            db.close()
