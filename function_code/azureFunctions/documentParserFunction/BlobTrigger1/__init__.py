import logging

import azure.functions as func


def main(myblob: func.InputStream,
    outputblob: func.Out[func.InputStream]) -> None:
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    print(type(myblob))
    print(f"Python blob trigger function processed blob \n"
                f"Name: {myblob.name}\n"
                f"Blob Size: {myblob.length} bytes")

    blob_source_raw_name = myblob.name
    print(blob_source_raw_name)
    print(type(blob_source_raw_name))
    #print(myblob.read())
    #local_file_name_thumb = blob_source_raw_name.replace(".htm",".html")

    #local_file_name_thumb = str(blob_source_raw_name[:–4]) + ".xyz"
    #print(local_file_name_thumb)
    
    #with open(blob_source_raw_name,"w+b") as local_blob:
    #    local_blob.write(myblob.read())


    f = open('./file.htm', 'wb')

    print(myblob.read())
    f.write(myblob.read())

    r = open('./file.htm','r')
    
    o = r.read()

    fd = codecs.open("./file.htm", "r", "utf-8")

    outputblob.set(fd)



