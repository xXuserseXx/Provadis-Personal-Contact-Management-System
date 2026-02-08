from datetime import datetime
import functools


def make_logger(filename = "contacts.log"):
  
  #Returns a log(message) function
  #This closure is used to remember the filename, default log file is named "contacts.log"
  
  def log(message: str, level = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level = str(level).upper()
    # logging Format looks like "[LOGGINGLEVEL] [TIMESTAMPOFLOG]: LOGGEDMESSAGE"
    line = f"[{level}] [{timestamp}] : {message}\n" 
    with open(filename , "a", encoding="utf-8") as f:
      f.write(line)
      
  return log

def log_calls(log):
  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      try:
        result = func(*args, **kwargs)
        log(f"{func.__name__}: FUNCTION CALL SUCCESFULL")
        return result
      except Exception as e:
        log(f"{func.__name__}: ERROR WHILE CALLING FUNCTION ({type(e).__name__}: {e})", level="ERROR")
        raise
    return wrapper
  return decorator