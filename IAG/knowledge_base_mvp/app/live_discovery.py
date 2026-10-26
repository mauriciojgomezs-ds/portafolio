import re
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Documentation-Research-MVP/0.7 (+local testing)"


def normalize_url(url: str) -> str:
    if not url:
        return url
    url = url.strip()
    parsed = urlparse(url)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        if "uddg" in qs:
            url = unquote(qs["uddg"][0])
    return url.split("#", 1)[0]


def source_domain_and_path(base_url: str, include: str = "") -> tuple[str, str]:
    parsed = urlparse(base_url if base_url.endswith("/") else base_url + "/")
    domain = parsed.netloc
    path = include or parsed.path or "/"
    if path == "/":
        path = ""
    return domain, path


def build_discovery_queries(question: str, base_url: str, include: str = "", tag: str = "docs") -> list[str]:
    q = question.lower()
    domain, path = source_domain_and_path(base_url, include)
    site = f"site:{domain}{path}"
    queries: list[str] = []

    if tag in {"aws", "awsdocs", "amazon"} or domain == "docs.aws.amazon.com":
        if any(x in q for x in ["lambda", "aws lambda"]) and any(x in q for x in ["python", "crear", "create", "funcion", "función"]):
            queries.extend([
                f'{site} "AWS Lambda" "Python" "create function"',
                f'{site} "Lambda" "Python" "handler"',
                f'{site} "Lambda" "Python" "deployment package"',
                f'{site} "Lambda" "getting started" "Python"',
            ])

    elif tag in {"mslearn", "microsoft", "learn"}:
        # Microsoft Learn funciona mejor con consultas explícitas en inglés.
        if any(x in q for x in ["azure function", "azure functions", "function app", "función de azure", "funcion de azure"]):
            queries.extend([
                f'{site} "Azure Functions" "Python" "create"',
                f'{site} "Create your first function" "Python" "Azure Functions"',
                f'{site} "Azure Functions Python developer guide"',
                f'{site} "Azure Functions Core Tools" "Python"',
            ])
        elif any(x in q for x in ["databricks", "data bricks"]) and any(x in q for x in ["cluster", "compute", "clúster"]):
            queries.extend([
                f'{site} "Azure Databricks" "create compute"',
                f'{site} "Azure Databricks" "clusters" "compute"',
                f'{site} "Azure Databricks" "compute configuration"',
                f'{site} "Azure Databricks" "cluster policy"',
            ])

    cleaned = " ".join(re.findall(r"[\wáéíóúñÁÉÍÓÚÑ]+", question))
    # Consulta genérica para cualquier origen documental/tag.
    queries.append(f"{site} {cleaned}")
    return queries


def search_microsoft_learn_api(question: str, limit: int = 8, locale: str = "en-us") -> list[str]:
    """Busca en el endpoint público de Microsoft Learn.

    No reemplaza el crawler: solo ayuda a encontrar URLs semilla cuando el
    origen registrado es learn.microsoft.com y la KB local está vacía.
    """
    cleaned = " ".join(re.findall(r"[\wáéíóúñÁÉÍÓÚÑ]+", question))
    if not cleaned:
        return []
    url = "https://learn.microsoft.com/api/search"
    params = {"search": cleaned, "locale": locale, "$top": str(limit)}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    rows = data.get("results") or data.get("documents") or []
    urls: list[str] = []
    q = question.lower()
    wants_examples = any(x in q for x in ["sample", "samples", "ejemplo", "ejemplos", "flask"])
    blocked = [
        "/answers/", "/users/", "/legal/", "/principles-for-ai-generated-content",
        "/previous-versions/", "/lifecycle/", "/contribute", "/training/"
    ]
    weighted: list[tuple[int, str]] = []
    for row in rows:
        candidate = row.get("url") or row.get("href")
        if not candidate:
            continue
        candidate = normalize_url(candidate)
        if candidate.startswith("/"):
            candidate = "https://learn.microsoft.com" + candidate
        parsed = urlparse(candidate)
        if parsed.netloc != "learn.microsoft.com":
            continue
        path = parsed.path.lower()
        if any(b in path for b in blocked):
            continue
        if "/samples/" in path and not wants_examples:
            continue
        score = 0
        if any(x in q for x in ["azure function", "azure functions", "function app", "función de azure", "funcion de azure"]):
            if "/en-us/azure/azure-functions/" in path:
                score += 20
            if "functions-create-first-function-python" in path:
                score += 40
            if any(x in path for x in ["functions-reference-python", "functions-develop-local", "functions-run-local", "functions-bindings-http-webhook-trigger"]):
                score += 25
            if "python" in path:
                score += 10
        elif any(x in q for x in ["databricks", "data bricks"]) and any(x in q for x in ["cluster", "compute", "clúster"]):
            if "/en-us/azure/databricks/" in path:
                score += 25
            if any(x in path for x in ["/compute", "cluster", "clusters"]):
                score += 25
            if any(x in path for x in ["policy", "policies", "runtime", "workspace"]):
                score += 8
            if any(x in path for x in ["security/network", "vnet", "certifications", "study-guides"]):
                score -= 20
        else:
            # Regla genérica: priorizar documentación de producto y paths cuyos tokens aparecen en la pregunta.
            tokens = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) > 3]
            for t in tokens:
                if t in path:
                    score += 5
            if "/en-us/azure/" in path:
                score += 5
        weighted.append((score, candidate))
    for _score, candidate in sorted(weighted, reverse=True):
        if candidate not in urls:
            urls.append(candidate)
        if len(urls) >= limit:
            break
    return urls

def fallback_urls(question: str, tag: str = "docs") -> list[str]:
    q = question.lower()
    if tag in {"aws", "awsdocs", "amazon"}:
        if any(x in q for x in ["lambda", "aws lambda"]) and any(x in q for x in ["python", "crear", "create", "funcion", "función"]):
            return [
                "https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html",
                "https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html",
                "https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-awscli.html",
                "https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common.html",
                "https://docs.aws.amazon.com/lambda/latest/dg/python-package.html",
                "https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html",
            ]
        return []
    if tag in {"mslearn", "microsoft", "learn"}:
        if any(x in q for x in ["azure function", "azure functions", "function app", "función de azure", "funcion de azure"]):
            return [
                "https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-python",
                "https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python",
                "https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-local",
                "https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local",
                "https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger",
            ]
        if any(x in q for x in ["databricks", "data bricks"]) and any(x in q for x in ["cluster", "compute", "clúster"]):
            return [
                "https://learn.microsoft.com/en-us/azure/databricks/compute/",
                "https://learn.microsoft.com/en-us/azure/databricks/compute/configure",
                "https://learn.microsoft.com/en-us/azure/databricks/compute/policies",
                "https://learn.microsoft.com/en-us/azure/databricks/getting-started/concepts",
            ]
        return []

    return []


def search_duckduckgo(query: str, allowed_domain: str, include: str = "", limit: int = 5, timeout: int = 15) -> list[str]:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get("https://duckduckgo.com/html/", params={"q": query}, headers=headers, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    urls: list[str] = []
    for a in soup.select("a.result__a"):
        href = normalize_url(a.get("href", ""))
        parsed = urlparse(href)
        if parsed.netloc == allowed_domain and (not include or include in href) and href not in urls:
            urls.append(href)
        if len(urls) >= limit:
            break
    return urls


def discover_candidate_urls(question: str, base_url: str, limit: int = 6, include: str = "", tag: str = "docs") -> list[str]:
    domain, _ = source_domain_and_path(base_url, include)
    results: list[str] = []

    # Primero agregar URLs semilla confiables del conector cuando existan.
    # En Microsoft Learn esto evita que /answers/ o /samples/ dominen una consulta vacía.
    for url in fallback_urls(question, tag=tag):
        if (not include or include in url) and url not in results:
            results.append(url)
        if len(results) >= limit:
            break

    # Conector específico: Microsoft Learn tiene API pública de búsqueda.
    # Esto evita depender solo de DuckDuckGo cuando la KB está vacía.
    if len(results) < limit and (tag in {"mslearn", "microsoft", "learn"} or domain == "learn.microsoft.com"):
        try:
            for url in search_microsoft_learn_api(question, limit=limit):
                if (not include or include in url) and url not in results:
                    results.append(url)
                if len(results) >= limit:
                    break
        except Exception:
            pass

    for query in build_discovery_queries(question, base_url=base_url, include=include, tag=tag):
        try:
            for url in search_duckduckgo(query, allowed_domain=domain, include=include, limit=limit):
                if url not in results:
                    results.append(url)
                if len(results) >= limit:
                    break
        except Exception:
            pass
        if len(results) >= limit:
            break

    for url in fallback_urls(question, tag=tag):
        if (not include or include in url) and url not in results:
            results.append(url)
        if len(results) >= limit:
            break
    return results


def required_urls_for_question(question: str, tag: str = "docs") -> list[str]:
    """Referencias complementarias disponibles para conectores específicos."""
    return fallback_urls(question, tag=tag)


def score_related_link(question: str, url: str, title: str = "") -> float:
    q = question.lower()
    hay = f"{url} {title}".lower()
    score = 0.0
    tokens = set(re.findall(r"[\wáéíóúñ]+", q))
    for t in tokens:
        if len(t) > 3 and t in hay:
            score += 1.0

    if any(x in q for x in ["databricks", "data bricks"]) and any(x in q for x in ["cluster", "compute", "clúster"]):
        for term in ["databricks", "compute", "cluster", "clusters", "runtime", "policy", "policies", "workspace", "node", "nodes", "autoscaling", "job"]:
            if term in hay:
                score += 3.0
        for bad in ["azure-functions", "functions", "core-tools", "answers", "legal", "certifications", "study-guides", "network", "vnet"]:
            if bad in hay:
                score -= 5.0

    if any(x in q for x in ["seguimiento web", "web tracking", "regla de acción", "reglas de acción", "regla de accion", "reglas de accion", "action rule", "action rules", "mapa de accion", "mapas de accion", "mapa de acción", "mapas de acción", "action map"]):
        for term in ["action-map", "action-maps", "web-tracking", "visitor-tracking", "messaging", "deployment", "tracking", "snippet", "sdk", "commands", "record", "trigger", "triggers", "segment", "outcome", "web-messaging", "web-chat", "content-offer", "workflow", "queue", "webpages"]:
            if term in hay:
                score += 3.0
        for bad in ["outbound", "dialing", "campaign", "contact-list", "telephony"]:
            if bad in hay:
                score -= 5.0

    if any(x in q for x in ["azure function", "azure functions", "function app", "función de azure", "funcion de azure"]):
        for term in ["azure-functions", "functions", "python", "core-tools", "function-app", "http-trigger", "bindings", "local"]:
            if term in hay:
                score += 2.0

    if any(x in q for x in ["lambda", "aws lambda"]) and any(x in q for x in ["python", "crear", "create", "funcion", "función"]):
        for term in ["lambda", "python", "handler", "runtime", "deployment-package", "gettingstarted", "awscli", "configuration", "function-url", "cloudwatch"]:
            if term in hay:
                score += 3.0
        for bad in ["ec2", "ecs", "eks", "cloudformation", "java", "nodejs", "ruby", "dotnet", "go", "legal", "pricing"]:
            if bad in hay:
                score -= 4.0

    return score

