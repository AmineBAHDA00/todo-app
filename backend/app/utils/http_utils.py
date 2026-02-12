from typing import Any, Dict, Tuple, Optional


JsonDict = Dict[str, Any]
Response = Tuple[JsonDict, int]


def success_response(
    data: Optional[JsonDict] = None,
    status_code: int = 200,
) -> Response:
    """
    Construit une réponse "succès" standard.
    """
    body: JsonDict = data or {}
    body.setdefault("success", True)
    return body, status_code


def error_response(
    message: str,
    status_code: int = 400,
    code: Optional[str] = None,
) -> Response:
    """
    Construit une réponse d'erreur standardisée.
    """
    body: JsonDict = {
        "success": False,
        "error": message,
    }
    if code:
        body["code"] = code
    return body, status_code


def status_response(
    status: str,
    status_code: int = 200,
) -> Response:
    """
    Réponse simple avec un champ `status`.
    Utile pour les opérations de type DELETE / PUT.
    """
    return {"status": status}, status_code

