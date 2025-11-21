"""
Custom exception classes
"""


class ViroAIException(Exception):
    """Base exception for Viro-AI"""
    pass


class MLModelError(ViroAIException):
    """Error in ML model execution"""
    pass


class FileProcessingError(ViroAIException):
    """Error in file processing"""
    pass


class ProjectProcessingError(ViroAIException):
    """Error in project processing"""
    pass

