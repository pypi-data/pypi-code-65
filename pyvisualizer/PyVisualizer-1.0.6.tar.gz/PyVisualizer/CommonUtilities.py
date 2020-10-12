import gspread


class CommonUtilities:

    def connectAndAutorizeToServiceAccount(self, serviceAccountFilePath):
        """
        This method will connect to google service account which is configured in service_account.json file.
        If successfully connected the it will return client connection obj
        """
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        try:
            # creds = ServiceAccountCredentials.from_json_keyfile_name("new_cred.json", scope)
            # self.client = gspread.authorize(creds)
            # self.connectedClientObj = gspread.service_account("./service_account.json", scopes=scope)
            connectedClientObj = gspread.service_account(serviceAccountFilePath, scopes=scope)
            if type(connectedClientObj) is gspread.client.Client:
                print("Successfully Authorized and Connected to Google Service Account. :)")
                return connectedClientObj
            else:
                print("Failed to connect and authorize to service account.")
                return None
        except Exception as e:
            print("Exception caught in Connecting and Authorizing Google Service Account : ", e)
            return None

    def read_google_sheet(self, clientConnectionObject, sGoogleSheetFileName, sWorkSheetName):
        """
        This method is used to read the google sheet file and worksheet inside it
        :param clientConnectionObject: Accepts a connection object to google account
        :param sGoogleSheetFileName: Accepts Google sheet file name
        :param sWorkSheetName: Accepts what worksheet needs to accessed from the file
        :return: Read the specified sheet and Returns the object of that sheet, if any exception then return None
        """

        # An empty string counts as False, variable with a value in it count as True
        if sGoogleSheetFileName and sWorkSheetName:
            try:
                sheets = clientConnectionObject.open(sGoogleSheetFileName)
                return sheets.worksheet(sWorkSheetName)
            except:
                raise Exception("Exception caught in reading the GoogleSheetFile/Worksheet.")
                return None
        else:
            raise ValueError("Parameter value cannot be empty.")
            return None
