class APIException(Exception):
    pass


class JSONRPC(APIException):
    code = None
    code_min = None
    code_max = None
    message = ""
    meaning = ""

    def __init__(self, data=None, raw_code=None, message=None):
        APIException.__init__(self)
        self.data = data
        self.raw_code = raw_code
        if message:
            self.message = "{} {}".format(self.message, message)

    def __str__(self):
        return "{message}({code}): {meaning}".format(
            message=self.message,
            code=self.code,
            meaning=self.meaning
        )

    def __repr__(self):
        return "{message}({code}): {meaning} {data}".format(
            message=self.message,
            code=self.code,
            meaning=self.meaning,
            data=repr(self.data)
        )


class InvalidParams(JSONRPC):
    code = -32602
    message = "Invalid params"
    meaning = "Invalid method parameter(s)."


class InternalError(JSONRPC):
    code = -32603
    message = "Internal error"
    meaning = "Internal JSON-RPC error."


class MethodNotFound(JSONRPC):
    code = -32601
    message = "Method not found"
    meaning = "The method does not exist / is not available."


class AuthenticationError(JSONRPC):
    code = -32604
    message = "Authentication error"
    meaning = "There was a problem with Authenticating your account"


class UnknownError(JSONRPC):
    code = None
    message = "Unknown error"
    meaning = "An unknown error occured"
