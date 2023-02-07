class COM_Error(Exception):
    def __init__(self, message = "An error occured parsing this command to Studio. Please consult the log and help files."):
        super().__init__(message)

class ApplicationError(Exception):
    def __init__(self, message = "No valid Studio installation was found"):
        super().__init__(message)