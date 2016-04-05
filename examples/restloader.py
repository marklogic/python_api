import logging
import os
from os import listdir
from os.path import isfile, join
from test.test_threadedtempfile import FILES_PER_THREAD

class RESTLoader():
    """
    This class will upload files using the REST API.
    """
    def __init__(self, conn, restPort, database, permissions):
        self.logger = logging.getLogger("marklogic.examples")
        self.conn = conn
        self.restPort = restPort
        self.database = database
        self.permissions = permissions
        pass
    
    def build_uri(self, targetUri):
        baseUri = self.conn.protocol + "://"+self.conn.host+":" + str(self.restPort) + "/LATEST/documents"
        uri = baseUri + "?uri=" + targetUri
        if (self.database is not None):
            uri += "&database=" + self.database
        if (self.permissions is not None):
            for perm in self.permissions.split(","):
                uri += "&perm:" + perm
        return uri

    def load_file(self, sourceFile, targetUri):
        self.logger.info("Loading {0} to {1}".format(sourceFile, targetUri))
        uri = self.build_uri(targetUri)
        print(uri)
        data = open(sourceFile, 'rb').read()
        response = self.conn.putFile(uri=uri, data=data, content_type="test/text")
        if (response.status_code == 201):
            print("CREATED: " + targetUri)
        elif (response.status_code == 204):
            print("UPDATED: " + targetUri)
        else:
            print("Unexpected Response:"+str(response.status_code))
        return response

    def load_directory(self, sourceDirectory, targetUri):
        self.logger.info("Loading {0} to {1}".format(sourceDirectory, targetUri))
        files = [f for f in listdir(sourceDirectory) if isfile(join(sourceDirectory, f))]
        for file in files:
            print(file)
            response = self.load_file(sourceDirectory+os.path.sep+file, targetUri+"/"+file)
        directories = [d for d in listdir(sourceDirectory) if os.path.isdir(sourceDirectory+os.path.sep+d)]
        for directory in directories:
            print(directory)
            response = self.load_directory(sourceDirectory+os.path.sep+directory, targetUri+"/"+directory)
            