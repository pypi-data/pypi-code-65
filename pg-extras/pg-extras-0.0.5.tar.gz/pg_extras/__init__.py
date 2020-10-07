from sqlalchemy import text

class PGExtras:
  x = 6
  def query(db, query_name)
      result = db.engine.execute(text(q))
      return result
