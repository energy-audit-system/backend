from app.db import db
from sqlalchemy.sql import func


class ReportFile(db.Model):
    __tablename__ = "files"
    __table_args__ = {"schema": "reports"}

    id = db.Column(db.BigInteger, primary_key=True)

    report_id = db.Column(
        db.BigInteger,
        db.ForeignKey("reports.reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_type = db.Column(db.Text, nullable=False)  # pdf/xlsx/archive
    cloud_path = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<ReportFile id={self.id} report_id={self.report_id} type={self.file_type}>"
