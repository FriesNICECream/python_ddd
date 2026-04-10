class MediaIngestError(Exception):
    """媒体采集领域异常基类。"""


class InvalidCursorAdvanceError(MediaIngestError):
    """来源游标回退时抛出。"""


class EmptyCanonicalTitleError(MediaIngestError):
    """资源标题无法归一化时抛出。"""


class DuplicateCloudLinkError(MediaIngestError):
    """资源下出现重复网盘链接时抛出。"""
