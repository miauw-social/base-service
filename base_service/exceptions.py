class ProblemJSON:
    """class representing the problem json standard as mentionned in [RFC 7807](https://datatracker.ietf.org/doc/html/rfc7807)"""

    @staticmethod
    def build(
        typ: str, title: str, detail: str, status: int, context: dict | None = None
    ) -> dict:
        """function to generate dict from parameters"""
        return {
            "type": typ,
            "title": title,
            "detail": detail,
            "status": status,
            "context": context if context else {},
        }