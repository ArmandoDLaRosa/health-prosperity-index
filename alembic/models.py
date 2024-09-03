from sqlalchemy import Column, Integer, String, Float, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

Base = declarative_base(metadata=metadata)

class IndexTable(Base):
    __tablename__ = 'index_table'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    index_value = Column(Float)

class CronJobLogs(Base):
    __tablename__ = 'cron_job_logs'
    id = Column(Integer, primary_key=True)
    run_time = Column(DateTime)
    status = Column(String(255))
    message = Column(String)
