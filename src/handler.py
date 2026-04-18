from mangum import Mangum
from src.app.main import app

handler = Mangum(app)
