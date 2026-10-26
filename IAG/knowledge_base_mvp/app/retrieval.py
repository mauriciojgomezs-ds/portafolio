import re
from collections import Counter
from sqlite3 import Connection


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\wáéíóúñÁÉÍÓÚÑ]+", text.lower())


def build_fts_query(question: str) -> str:
    tokens = tokenize(question)
    stop = {"como", "cómo", "se", "de", "la", "el", "y", "o", "una", "un", "para", "que", "en", "cloud"}
    tokens = [t for t in tokens if t not in stop and len(t) > 2]
    if not tokens:
        return question
    return " OR ".join(tokens[:12])


def intent_profile(question: str) -> dict:
    """Perfil simple de intención para mejorar ranking sin LLM.

    En un MVP local, esto reemplaza a un re-ranker semántico más avanzado.
    Se puede ampliar con reglas por dominio: seguimiento web, reglas de acción, campañas, colas y flujos.
    """
    q = question.lower()
    positive = set(tokenize(question))
    negative = set()

    is_action_rule = any(x in q for x in [
        "seguimiento web", "web tracking", "regla de acción", "reglas de acción", "regla de accion", "reglas de accion", "action rule", "action rules", "mapa de accion", "mapas de accion",
        "mapa de acción", "mapas de acción", "action map", "action maps"
    ])

    if is_action_rule:
        positive.update({
            "tracking", "activity", "interaction", "action", "map", "maps", "actionmap",
            "trigger", "triggers", "segment", "segments", "outcome", "outcomes",
            "visitor", "activity", "web", "messaging", "chat", "content", "offer",
            "workflow", "flow", "webpages", "queue", "schedule", "frequency", "priority",
            "messaging", "deployment", "deploy", "snippet", "tracking", "digital", "sdk",
            "record", "command", "commands", "javascript", "web messaging", "activity monitor",
            "action map", "action maps", "seguimiento web", "web tracking", "digital user tracking",
        })
        negative.update({
            "dialing", "dialer", "outbound dialing", "contact list", "telephony",
            "predictive dialing", "preview", "progressive", "power dialing", "agentless campaign",
        })
        return {"positive": positive, "negative": negative, "intent": "web_tracking_action_rules"}

    if any(x in q for x in ["azure function", "azure functions", "function app", "función de azure", "funcion de azure"]):
        positive.update({
            "azure", "functions", "function", "python", "create", "quickstart", "core tools",
            "func", "local", "http trigger", "trigger", "vscode", "visual studio code",
            "requirements", "function_app.py", "host.json", "deploy", "publish", "programming model"
        })
        negative.update({
            "answers", "sample", "samples", "flask", "search", "queue storage", "legal", "previous versions",
            "users", "q&a", "subscription creation", "sql bindings"
        })
        return {"positive": positive, "negative": negative, "intent": "azure_functions_python"}

    if any(x in q for x in ["databricks", "data bricks"]) and any(x in q for x in ["cluster", "compute", "clúster", "clusteres"]):
        positive.update({
            "databricks", "compute", "cluster", "clusters", "create", "configuration",
            "workspace", "runtime", "node", "nodes", "policy", "policies", "pool",
            "pools", "spark", "all-purpose", "job compute", "serverless", "classic compute"
        })
        negative.update({
            "azure functions", "function app", "core tools", "func", "http trigger",
            "certification", "study guide", "exam", "answers", "legal", "users"
        })
        return {"positive": positive, "negative": negative, "intent": "databricks_compute_cluster"}

    if any(x in q for x in ["lambda", "aws lambda"]) and any(x in q for x in ["python", "crear", "create", "funcion", "función"]):
        positive.update({
            "aws", "lambda", "python", "create", "function", "handler", "runtime",
            "deployment", "package", "zip", "role", "iam", "execution role",
            "test", "invoke", "cloudwatch", "aws cli", "console", "permissions",
            "environment variables", "configuration", "boto3"
        })
        negative.update({
            "ec2", "ecs", "eks", "java", "node.js", "nodejs", "ruby", "go", "dotnet", "pricing", "legal"
        })
        return {"positive": positive, "negative": negative, "intent": "aws_lambda_python"}

    if "outbound" in q or "campaña" in q or "campaign" in q:
        positive.update({
            "outbound", "campaign", "campaigns", "dialing", "dialer", "contact", "list",
            "queue", "script", "dnc", "rules", "rule", "schedule", "callable", "preview",
            "progressive", "predictive", "power", "agentless", "external", "mode", "modes",
            "campaign editor", "contact list", "dialing mode",
        })
        # Si la pregunta no menciona email, bajamos ese ruido.
        if "email" not in q and "correo" not in q:
            negative.update({"email", "smtp", "domain", "notification", "notifications", "inbound"})

    return {"positive": positive, "negative": negative, "intent": "generic"}

def score_document(row, profile: dict) -> float:
    text = f"{row['title'] or ''} {row['url'] or ''} {row['clean_text'][:3000]}".lower()
    title_url = f"{row['title'] or ''} {row['url'] or ''}".lower()

    score = 0.0
    for term in profile["positive"]:
        if not term:
            continue
        if term in title_url:
            score += 3.0
        elif term in text:
            score += 1.0

    for term in profile["negative"]:
        if term in title_url:
            score -= 6.0
        elif term in text:
            score -= 2.0

    # Preferir documentación central y bajar páginas auxiliares.
    url = (row["url"] or "").lower()
    if "/articles/" in url:
        score += 2.0
    if "/azure/azure-functions/" in url:
        score += 6.0
    if any(x in url for x in ["functions-create-first-function-python", "functions-reference-python", "functions-develop-local", "functions-run-local", "functions-bindings-http-webhook-trigger"]):
        score += 8.0
    if "/azure/databricks/" in url:
        score += 6.0
    if any(x in url for x in ["/azure/databricks/compute", "/azure/databricks/clusters", "compute/configure", "compute/create"]):
        score += 10.0
    if "docs.aws.amazon.com/lambda" in url:
        score += 8.0
    if any(x in url for x in ["lambda-python", "python-handler", "gettingstarted", "configuration-function-common", "python-package", "lambda-runtimes"]):
        score += 8.0
    if any(x in url for x in ["/answers/", "/users/", "/legal/", "/previous-versions/", "/lifecycle/", "/principles-for-ai-generated-content", "/credentials/certifications/"]):
        score -= 20.0
    if "/samples/" in url and "ejemplo" not in text and "sample" not in text:
        score -= 8.0
    if any(x in url for x in ["/release-notes/", "/announcements/", "/glossary/"]):
        score -= 2.0

    # bm25 de SQLite: menor es mejor. Lo convertimos en un pequeño ajuste.
    try:
        score += max(0, 5 - abs(float(row["score"]))) * 0.2
    except Exception:
        pass

    return score



def search_documents_by_urls(conn: Connection, question: str, urls: list[str], limit: int = 8):
    """Busca/rankea solo dentro de URLs recién descubiertas.

    Esto evita contaminación entre temas del mismo source/tag: por ejemplo, que
    documentos de Azure Functions aparezcan al preguntar por Databricks solo
    porque ambos viven en Microsoft Learn.
    """
    if not urls:
        return []
    placeholders = ",".join("?" for _ in urls)
    rows = conn.execute(
        f"""
        SELECT title, clean_text, url, document_id, version_id, 0 AS score
        FROM document_fts
        WHERE url IN ({placeholders})
        """,
        tuple(urls),
    ).fetchall()
    profile = intent_profile(question)
    ranked = sorted(rows, key=lambda r: score_document(r, profile), reverse=True)
    return ranked[:limit]

def search_documents(conn: Connection, question: str, limit: int = 5, pool_size: int = 20, tag: str | None = None):
    q = build_fts_query(question)
    if tag:
        rows = conn.execute(
            """
            SELECT f.title, f.clean_text, f.url, f.document_id, f.version_id, bm25(document_fts) AS score
            FROM document_fts f
            JOIN documents d ON d.id = f.document_id
            WHERE document_fts MATCH ? AND d.source_tag = ?
            ORDER BY score
            LIMIT ?
            """,
            (q, tag, max(limit, pool_size)),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT title, clean_text, url, document_id, version_id, bm25(document_fts) AS score
            FROM document_fts
            WHERE document_fts MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (q, max(limit, pool_size)),
        ).fetchall()

    profile = intent_profile(question)
    ranked = sorted(rows, key=lambda r: score_document(r, profile), reverse=True)
    return ranked[:limit]


def search_validated_qa(conn: Connection, question: str, limit: int = 3):
    q = build_fts_query(question)
    return conn.execute(
        """
        SELECT question, answer, sources, qa_id, bm25(validated_qa_fts) AS score
        FROM validated_qa_fts
        WHERE validated_qa_fts MATCH ?
        ORDER BY score
        LIMIT ?
        """,
        (q, limit),
    ).fetchall()


def search_error_cases(conn: Connection, question: str, limit: int = 3):
    q = build_fts_query(question)
    return conn.execute(
        """
        SELECT question, bad_answer, reason, better_query, error_id, bm25(error_cases_fts) AS score
        FROM error_cases_fts
        WHERE error_cases_fts MATCH ?
        ORDER BY score
        LIMIT ?
        """,
        (q, limit),
    ).fetchall()


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    # Separador simple para documentación técnica.
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 40]


def extract_relevant_sentences(question: str, docs, max_sentences: int = 14) -> list[str]:
    profile = intent_profile(question)
    positive = profile["positive"]
    negative = profile["negative"]
    candidates = []

    for d in docs:
        for sent in split_sentences(d["clean_text"][:6000]):
            s = sent.lower()
            score = 0
            for term in positive:
                if term and term in s:
                    score += 2
            for term in negative:
                if term and term in s:
                    score -= 4
            # Priorizar frases de pasos, requisitos y configuración.
            if any(x in s for x in ["required", "permission", "configure", "select", "choose", "campaign editor", "contact list", "queue", "script", "dnc", "dialing mode", "messaging", "deploy", "deployment", "snippet", "sdk", "command", "record", "tracking", "activity monitor", "core tools", "func init", "func new", "func start", "http trigger", "python", "visual studio code", "function app", "publish", "lambda", "handler", "runtime", "execution role", "deployment package", "invoke", "cloudwatch"]):
                score += 3
            if score > 1:
                candidates.append((score, sent))

    # Quitar duplicados conservando los mejores.
    seen = set()
    ordered = []
    for _score, sent in sorted(candidates, key=lambda x: x[0], reverse=True):
        key = re.sub(r"\W+", " ", sent.lower())[:120]
        if key in seen:
            continue
        seen.add(key)
        ordered.append(sent)
        if len(ordered) >= max_sentences:
            break
    return ordered




def technical_source_expectations(question: str, docs) -> list[tuple[str, str, bool]]:
    """Devuelve categorías de fuentes que deberían estar cubiertas.

    La idea del MVP es que `--discover` no solo responda, sino que muestre qué
    tipos de documentación técnica conviene revisar para no dejar vacíos.
    Para temas conocidos usa reglas específicas; para temas nuevos usa una
    checklist genérica que sirve para cualquier origen documental.
    """
    q = question.lower()
    profile = intent_profile(question)
    hay = "\n".join([f"{d['title'] or ''} {d['url'] or ''} {d['clean_text'][:2500]}" for d in docs]).lower()

    def found(*terms: str) -> bool:
        return any(t.lower() in hay for t in terms)

    if profile.get("intent") == "web_tracking_action_rules":
        return [
            ("Introducción al seguimiento web", "Describe el alcance de la captura de actividad y las acciones automáticas.", found("web tracking", "visitor tracking", "seguimiento web")),
            ("Configuración de mensajería y despliegue", "Explica la configuración del canal y su publicación.", found("messaging", "deployment", "mensajería", "despliegue")),
            ("Captura de eventos", "Explica cómo registrar visitas y eventos del sitio.", found("tracking snippet", "visitor activity", "event", "evento")),
            ("Reglas de acción", "Describe creación, prioridad y frecuencia de las acciones.", found("action rule", "action map", "regla", "acción")),
            ("Disparadores y segmentos", "Define las condiciones para activar una acción.", found("trigger", "segment", "condition", "condición")),
            ("Enrutamiento y horarios", "Describe destinos, colas y disponibilidad.", found("routing", "queue", "schedule", "cola", "horario")),
            ("SDK y eventos personalizados", "Referencia para integraciones programáticas.", found("sdk", "command", "event", "api")),
        ]

    if profile.get("intent") != "web_tracking_action_rules" and ("outbound" in q or "campaña" in q or "campaign" in q) and ("email" not in q and "correo" not in q):
        return [
            ("Creación de campaña", "Describe el flujo de creación y sus campos requeridos.", found("create campaign", "campaign editor", "campaña")),
            ("Canal y modalidad", "Define la forma de contactar y las opciones admitidas.", found("channel", "dialing mode", "modalidad", "canal")),
            ("Lista de contactos", "Describe datos requeridos y validación de destinatarios.", found("contact list", "contact", "contactos")),
            ("Destino y atención", "Explica colas, equipos o flujos de destino.", found("queue", "routing", "cola", "workflow")),
            ("Guion o formulario", "Describe la información utilizada durante la atención.", found("script", "form", "guion", "formulario")),
            ("Integración del canal", "Describe dependencias de infraestructura cuando correspondan.", found("integration", "telephony", "infrastructure", "integración")),
            ("Tratamiento de respuestas", "Explica cómo gestionar intentos y resultados de contacto.", found("response", "retry", "result", "respuesta")),
            ("Reglas, exclusiones y horarios", "Controla las condiciones operativas de contacto.", found("rule", "exclusion", "schedule", "horario", "regla")),
            ("Límites y validación", "Permite revisar capacidad y probar antes de activar.", found("limit", "test", "verify", "validación")),
            ("API o SDK opcional", "Referencia para automatizar la configuración.", found("api", "sdk", "developer")),
        ]

    if profile.get("intent") == "databricks_compute_cluster":
        return [
            ("Introducción a Azure Databricks/compute", "Permite entender la diferencia entre workspace, compute, clusters y jobs.", found("azure databricks", "compute", "cluster")),
            ("Prerequisitos y permisos", "Debe cubrir workspace, permisos para crear compute y políticas si existen.", found("permission", "workspace", "compute policy", "cluster policy", "entitlement")),
            ("Creación/configuración de compute", "Debe explicar los campos principales para crear el cluster/compute.", found("create compute", "cluster", "configure compute", "new compute")),
            ("Runtime y versión", "Debe explicar Databricks Runtime y selección de versión.", found("databricks runtime", "runtime version")),
            ("Tipo/tamaño de nodo y autoscaling", "Debe explicar nodos, workers, autoscaling o modo single node cuando aplique.", found("node type", "worker", "autoscale", "autoscaling", "single node")),
            ("Políticas, límites o costos", "Debe ayudar a controlar configuraciones permitidas, costos y restricciones.", found("policy", "policies", "limit", "cost", "pricing")),
            ("Prueba con notebook/job", "Sirve para validar que el cluster/compute quedó utilizable.", found("notebook", "job", "attach", "run")),
            ("CLI/API/SDK", "Necesario si se quiere automatizar la creación del compute.", found("cli", "api", "sdk", "databricks cli", "clusters api")),
        ]

    if profile.get("intent") == "aws_lambda_python":
        return [
            ("Guía oficial de Lambda con Python", "Debe explicar el runtime Python y el flujo base de una función Lambda.", found("lambda-python", "python", "aws lambda")),
            ("Handler", "Debe explicar el archivo y función handler que Lambda ejecuta.", found("python-handler", "handler", "lambda_handler")),
            ("Runtime y versión de Python", "Debe indicar versiones soportadas y cómo elegir runtime.", found("runtime", "python 3", "lambda-runtimes")),
            ("Rol IAM / execution role", "La función necesita permisos para escribir logs y acceder a servicios.", found("execution role", "iam role", "permissions", "role")),
            ("Creación por consola o AWS CLI", "Debe cubrir cómo crear la función desde consola o comandos.", found("create-function", "aws lambda create-function", "console", "aws cli")),
            ("Deployment package/dependencias", "Necesario si la función incluye librerías Python adicionales.", found("deployment package", "python-package", "requirements.txt", "zip")),
            ("Prueba e invocación", "Debe explicar cómo probar o invocar la función.", found("test", "invoke", "aws lambda invoke")),
            ("Logs/monitoreo", "Permite validar ejecución y errores con CloudWatch Logs.", found("cloudwatch", "logs", "monitor")),
        ]

    if profile.get("intent") == "azure_functions_python":
        return [
            ("Quickstart oficial de Azure Functions con Python", "Debe explicar cómo crear la primera función y el proyecto base.", found("functions-create-first-function-python", "create your first function", "quickstart")),
            ("Prerequisitos locales", "Debe indicar Python soportado, Azure Functions Core Tools y/o extensión de VS Code.", found("install python", "core tools", "visual studio code", "azure functions extension")),
            ("Comandos Core Tools", "Debe cubrir comandos como func init, func new, func start y publish cuando aplica.", found("func init", "func new", "func start", "func azure functionapp publish", "core tools")),
            ("Estructura del proyecto Python", "Debe cubrir function_app.py, host.json, local.settings.json y requirements.txt.", found("function_app.py", "host.json", "local.settings.json", "requirements.txt")),
            ("Trigger HTTP o tipo de trigger", "Para una primera función normalmente se usa HTTP trigger o se elige el trigger correspondiente.", found("http trigger", "httptrigger", "bindings", "trigger")),
            ("Ejecución y prueba local", "Debe explicar cómo ejecutar y probar localmente antes de publicar.", found("func start", "run locally", "develop locally", "test")),
            ("Publicación en Azure", "Debe explicar cómo crear/publicar la Function App en Azure o enlazar con portal/CLI.", found("publish", "function app in azure", "azure functionapp publish", "deploy")),
            ("Referencia Python", "Sirve para entender decoradores, modelo de programación y tipos del SDK azure-functions.", found("python developer reference", "azure-functions library", "programming model", "decorator")),
        ]

    # Checklist genérica para temas no cubiertos por reglas específicas.
    return [
        ("Overview/introducción", "Sirve para entender el alcance del tema antes de configurar algo.", found("overview", "about", "introduction", "getting started")),
        ("Prerequisitos/permisos/licencias", "Permite saber qué debe existir antes de implementar.", found("permission", "permissions", "license", "required", "prerequisite")),
        ("Configuración paso a paso", "Debe contener la ruta o acciones concretas de configuración.", found("configure", "create", "set up", "settings", "admin")),
        ("Componentes relacionados", "Ayuda a detectar dependencias que la pregunta no menciona explícitamente.", found("related", "see also", "queue", "flow", "script", "integration", "deployment")),
        ("Validación/pruebas", "Sirve para confirmar que la configuración funcionó.", found("test", "verify", "validate", "monitor", "report")),
        ("Troubleshooting/limitaciones", "Ayuda a detectar errores frecuentes, límites o restricciones.", found("troubleshoot", "error", "limit", "limitation", "best practice")),
        ("API/SDK/comandos", "Necesario si la solución requiere código, automatización o integración técnica.", found("api", "sdk", "command", "event", "developer", "code", "snippet")),
    ]


def render_technical_expectations(question: str, docs) -> list[str]:
    rows = technical_source_expectations(question, docs)
    lines = ["\nFuentes técnicas que deberían estar presentes para este tema:"]
    for name, why, ok in rows:
        status = "ENCONTRADA" if ok else "FALTA/NO CONFIRMADA"
        lines.append(f"- [{status}] {name}: {why}")
    return lines


def make_explained_answer(question: str, docs, validated, errors) -> str:
    if validated:
        sources = validated[0]["sources"] or ""
        return (
            "Encontré una respuesta validada similar en la KB local.\n\n"
            f"{validated[0]['answer']}\n\n"
            f"Fuentes validadas: {sources}".strip()
        )

    if not docs:
        return "No encontré documentos locales suficientes para responder. Carga URLs primero con `ingest-url`, `ingest-file` o `crawl`."

    relevant = extract_relevant_sentences(question, docs)

    q = question.lower()
    profile = intent_profile(question)
    outbound_campaign = profile.get("intent") != "web_tracking_action_rules" and ("outbound" in q or "campaña" in q or "campaign" in q) and ("email" not in q and "correo" not in q)
    action_rules = profile.get("intent") == "web_tracking_action_rules"
    azure_functions = profile.get("intent") == "azure_functions_python"
    aws_lambda = profile.get("intent") == "aws_lambda_python"

    lines = []
    lines.append("Respuesta basada en la KB local:\n")

    if action_rules:
        lines.append("Guía orientativa para seguimiento web y reglas de acción. Los nombres y ubicaciones de los componentes dependen del sistema documentado; valida cada paso con las fuentes:\n")
        steps = [
            "Revisar requisitos y permisos para capturar actividad y configurar acciones.",
            "Configurar el canal de mensajería o interacción cuando sea necesario.",
            "Publicar el componente de integración e instalar el código de seguimiento según la documentación.",
            "Comprobar que se reciben visitas y eventos en el monitor de actividad.",
            "Definir segmentos, objetivos y eventos que se utilizarán como condiciones.",
            "Crear reglas de acción y definir sus disparadores.",
            "Establecer páginas incluidas y excluidas, prioridad y límites de frecuencia.",
            "Configurar el destino, la cola o el flujo de atención y los horarios aplicables.",
            "Consultar la API o el SDK si se requieren eventos personalizados.",
            "Probar la captura de actividad, las condiciones y la acción de extremo a extremo.",
        ]
        for i, step in enumerate(steps, start=1):
            lines.append(f"{i}. {step}")

    elif outbound_campaign:
        lines.append("Guía orientativa para configurar una campaña de contacto. Confirma los componentes y requisitos en la documentación del sistema:\n")
        steps = [
            "Revisar permisos para administrar campañas y sus componentes asociados.",
            "Definir canal y modalidad de contacto según el objetivo de la campaña.",
            "Preparar la lista de contactos y verificar sus campos requeridos.",
            "Seleccionar el destino o la cola de atención cuando corresponda.",
            "Configurar el guion o formulario de atención si la operación lo necesita.",
            "Definir exclusiones, reglas de contacto, horarios y límites operativos.",
            "Guardar y probar la configuración antes de activar la campaña.",
        ]
        for i, step in enumerate(steps, start=1):
            lines.append(f"{i}. {step}")

    elif profile.get("intent") == "databricks_compute_cluster":
        lines.append("Para crear un cluster/compute en Azure Databricks, la KB recuperada sugiere este flujo general. Lo importante es trabajar dentro del workspace correcto y revisar si existen políticas de compute que limiten lo que puedes crear:\n")
        steps = [
            "Entrar al workspace de Azure Databricks y abrir la sección de Compute.",
            "Crear un nuevo compute/cluster. Según la interfaz actual, puede aparecer como Compute, New compute o Create compute.",
            "Definir el propósito: interactivo para notebooks, job compute para trabajos, o serverless si tu workspace y plan lo permiten.",
            "Elegir Databricks Runtime, por ejemplo una versión compatible con el lenguaje y librerías que usarás.",
            "Configurar tamaño y tipo de nodos, cantidad de workers y autoscaling si corresponde.",
            "Aplicar una compute policy si la organización usa políticas para limitar costos, tamaños o runtimes permitidos.",
            "Crear el compute y esperar a que quede en estado running/activo.",
            "Probarlo adjuntando un notebook o ejecutando un job simple.",
            "Si necesitas automatizarlo, revisar la documentación de Databricks CLI/API/SDK para crear o administrar compute desde código.",
        ]
        for i, step in enumerate(steps, start=1):
            lines.append(f"{i}. {step}")

    elif aws_lambda:
        lines.append("Para crear una función AWS Lambda en Python, la KB recuperada apunta a este flujo práctico. Puedes hacerlo desde la consola de AWS o automatizarlo con AWS CLI/IaC; para el MVP, estos son los pasos base:\n")
        steps = [
            "Definir qué hará la función y qué servicios de AWS necesitará usar.",
            "Crear o seleccionar un IAM execution role para Lambda. Como mínimo debe permitir escribir logs en CloudWatch; agrega permisos extra solo si la función accede a otros servicios.",
            "Crear la función Lambda con runtime Python compatible, por ejemplo Python 3.x, y definir el handler, normalmente con formato `archivo.funcion`, como `lambda_function.lambda_handler`.",
            "Escribir el código Python del handler. El handler recibe `event` y `context`, procesa la entrada y retorna una respuesta o resultado.",
            "Si solo usas librerías estándar o boto3 disponible en el runtime, puedes editar el código inline. Si necesitas dependencias externas, preparar un deployment package ZIP o usar layers/contendor image según corresponda.",
            "Configurar memoria, timeout, variables de entorno y concurrencia si aplica.",
            "Crear un evento de prueba o invocar la función para validar que responde correctamente.",
            "Revisar CloudWatch Logs para confirmar ejecución, errores, duración y mensajes de diagnóstico.",
            "Si la función se expondrá por HTTP o será disparada por otro servicio, configurar el trigger correspondiente, por ejemplo API Gateway, EventBridge, S3, SQS u otro origen de eventos.",
        ]
        for i, step in enumerate(steps, start=1):
            lines.append(f"{i}. {step}")
        lines.append("\nEjemplo mínimo de handler Python:")
        lines.append("```python")
        lines.append("def lambda_handler(event, context):")
        lines.append('    return {"statusCode": 200, "body": "Hola desde Lambda"}')
        lines.append("```")
        lines.append("\nComandos AWS CLI orientativos:")
        lines.append("```bash")
        lines.append("zip function.zip lambda_function.py")
        lines.append("aws lambda create-function --function-name mi-lambda-python --runtime python3.12 --role <arn_rol_iam> --handler lambda_function.lambda_handler --zip-file fileb://function.zip")
        lines.append("aws lambda invoke --function-name mi-lambda-python response.json")
        lines.append("```")
        lines.append("\nArchivos que deberías revisar:")
        lines.append("- `lambda_function.py`: código principal del handler.")
        lines.append("- `requirements.txt`: dependencias Python, si usas paquetes externos.")
        lines.append("- `function.zip`: paquete de despliegue si publicas por ZIP.")

    elif azure_functions:
        lines.append("Para crear una Azure Function en Python, la KB recuperada apunta a este flujo práctico. Puedes hacerlo desde VS Code o desde la línea de comandos con Azure Functions Core Tools:\n")
        steps = [
            "Instalar prerequisitos: Python soportado por Azure Functions, Azure Functions Core Tools v4 y, opcionalmente, la extensión Azure Functions para Visual Studio Code.",
            "Crear una carpeta de proyecto y abrirla en VS Code o en una terminal.",
            "Inicializar el proyecto Python con Core Tools: `func init <nombre_proyecto> --python`.",
            "Crear la función: `func new`, elegir el trigger que corresponda y, para una primera prueba, seleccionar `HTTP trigger`.",
            "Revisar la estructura generada: `function_app.py` contiene la función; `host.json` configura el runtime; `local.settings.json` guarda configuración local; `requirements.txt` lista dependencias Python.",
            "Ejecutar localmente con `func start` y probar la URL local que entrega la consola, normalmente sobre `http://localhost:7071/...`.",
            "Agregar lógica Python y dependencias en `requirements.txt`. Si usas bindings, revisar la documentación del trigger/binding correspondiente.",
            "Publicar en Azure cuando funcione localmente. Desde Core Tools normalmente se usa `func azure functionapp publish <nombre_function_app>`; desde VS Code se puede usar el flujo de deploy de la extensión.",
            "Validar en Azure Portal o Application Insights que la función quedó desplegada y responde correctamente.",
        ]
        for i, step in enumerate(steps, start=1):
            lines.append(f"{i}. {step}")
        lines.append("\nComandos base esperados:")
        lines.append("```bash")
        lines.append("func init MiFunctionApp --python")
        lines.append("cd MiFunctionApp")
        lines.append("func new")
        lines.append("func start")
        lines.append("func azure functionapp publish <nombre_function_app>")
        lines.append("```")
        lines.append("\nArchivos que deberías revisar:")
        lines.append("- `function_app.py`: código principal de la función en el modelo Python actual.")
        lines.append("- `host.json`: configuración global del host de Azure Functions.")
        lines.append("- `local.settings.json`: variables locales; no debería subirse con secretos.")
        lines.append("- `requirements.txt`: paquetes Python que se instalarán al ejecutar/publicar.")

    else:
        lines.append("Estos son los puntos principales encontrados:\n")
        for sent in relevant[:8]:
            lines.append(f"- {sent}")

    lines.extend(render_technical_expectations(question, docs))

    if relevant:
        lines.append("\nEvidencia encontrada en los documentos locales:")
        for sent in relevant[:6]:
            lines.append(f"- {sent}")

    if errors:
        lines.append("\nErrores conocidos que conviene evitar:")
        for e in errors:
            if e["reason"]:
                lines.append(f"- {e['reason']}")
            if e["better_query"]:
                lines.append(f"  Búsqueda sugerida: {e['better_query']}")

    lines.append("\nFuentes usadas:")
    for d in docs:
        lines.append(f"- {d['title'] or 'Sin título'}: {d['url']}")

    return "\n".join(lines)


# Se mantiene el nombre anterior para no romper main.py ni comandos existentes.
def make_simple_answer(question: str, docs, validated, errors) -> str:
    return make_explained_answer(question, docs, validated, errors)
