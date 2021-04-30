import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    import os
    print(os.path.abspath(os.path.join(os.path.dirname( __file__ ))))
    a,b,c = next(os.walk(os.path.abspath(os.path.join(os.path.dirname(".."),"wheelhouse"))))
    print(a,b,c)
    #a,b,c = next(os.walk(os.path.abspath(os.path.join(os.path.dirname("/home/app")))))

    return func.HttpResponse(
                f"asdasd {a,b,c} {os.path.dirname( __file__ )}",
                status_code=200
            )