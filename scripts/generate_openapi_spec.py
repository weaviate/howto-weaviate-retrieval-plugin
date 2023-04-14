# thanks to https://github.com/tiangolo/fastapi/issues/1173#issuecomment-605664503
# paste output to https://www.json2yaml.com/

from fastapi.openapi.utils import get_openapi
from server.main import app
import json

if __name__ == "__main__":
    with open("openapi.json", "w") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
            ),
            f,
        )
