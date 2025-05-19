from app import create_app
from app.config import TestConfig

app = create_app(TestConfig)

if __name__ == '__main__':
    app.run(debug=True)
