import os
import json
import math
import datetime

TOOL_REGISTRY = {}


def tool(name, description, parameters=None):
    def decorator(func):
        TOOL_REGISTRY[name] = {
            "function": func,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                    or {"type": "object", "properties": {}, "required": []},
                },
            },
        }
        return func

    return decorator


def get_tool_schemas(tool_names):
    return [TOOL_REGISTRY[n]["schema"] for n in tool_names if n in TOOL_REGISTRY]


def execute_tool(name, arguments):
    if name not in TOOL_REGISTRY:
        return json.dumps({"error": f"Tool '{name}' not found"})
    try:
        result = TOOL_REGISTRY[name]["function"](**arguments)
        return json.dumps(result) if not isinstance(result, str) else result
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Internal Tools ──────────────────────────────────────────────


@tool(
    "get_weather",
    "Get the current weather for a location including temperature, condition, humidity and wind",
    {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City or region name"}
        },
        "required": ["location"],
    },
)
def get_weather(location):
    data = {
        "san francisco": {
            "temp_f": 62,
            "condition": "foggy",
            "humidity": 85,
            "wind_mph": 12,
        },
        "new york": {
            "temp_f": 45,
            "condition": "rainy",
            "humidity": 78,
            "wind_mph": 18,
        },
        "tokyo": {"temp_f": 58, "condition": "cloudy", "humidity": 65, "wind_mph": 8},
        "london": {
            "temp_f": 50,
            "condition": "overcast",
            "humidity": 80,
            "wind_mph": 15,
        },
        "mumbai": {"temp_f": 88, "condition": "sunny", "humidity": 70, "wind_mph": 6},
    }
    info = data.get(
        location.lower(),
        {"temp_f": 72, "condition": "sunny", "humidity": 50, "wind_mph": 10},
    )
    return {"location": location, **info}


@tool(
    "list_files",
    "List files in a directory",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path", "default": "."}
        },
        "required": [],
    },
)
def list_files(path="."):
    try:
        return {"files": os.listdir(path)}
    except FileNotFoundError:
        return {"error": f"Directory '{path}' not found"}


@tool(
    "calculate",
    "Evaluate a math expression. Supports +, -, *, /, **, sqrt, sin, cos, tan, log, pi, e.",
    {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate, e.g. '(3 + 5) * 2' or 'sqrt(144)'",
            }
        },
        "required": ["expression"],
    },
)
def calculate(expression):
    allowed = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
        "pow": pow,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool(
    "get_time",
    "Get the current date and time, optionally for a specific timezone offset (hours from UTC)",
    {
        "type": "object",
        "properties": {
            "utc_offset": {
                "type": "number",
                "description": "Hours offset from UTC, e.g. -8 for PST, 5.5 for IST",
                "default": 0,
            }
        },
        "required": [],
    },
)
def get_time(utc_offset=0):
    tz = datetime.timezone(datetime.timedelta(hours=utc_offset))
    now = datetime.datetime.now(tz)
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": f"UTC{utc_offset:+g}",
    }


@tool(
    "search_knowledge",
    "Search an internal knowledge base by keyword. Returns matching articles.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {
                "type": "integer",
                "description": "Max results to return",
                "default": 3,
            },
        },
        "required": ["query"],
    },
)
def search_knowledge(query, max_results=3):
    kb = [
        {
            "id": 1,
            "title": "Python Best Practices",
            "summary": "PEP8, type hints, virtual environments, and testing strategies for Python projects.",
        },
        {
            "id": 2,
            "title": "Intro to Machine Learning",
            "summary": "Supervised vs unsupervised learning, common algorithms like linear regression, decision trees, and neural networks.",
        },
        {
            "id": 3,
            "title": "REST API Design",
            "summary": "HTTP methods, status codes, authentication patterns, pagination, and versioning for REST APIs.",
        },
        {
            "id": 4,
            "title": "Docker Fundamentals",
            "summary": "Containers vs VMs, Dockerfile syntax, docker-compose, and multi-stage builds.",
        },
        {
            "id": 5,
            "title": "Climate Change Overview",
            "summary": "Greenhouse gases, global temperature trends, renewable energy sources, and carbon capture technologies.",
        },
        {
            "id": 6,
            "title": "World History: Industrial Revolution",
            "summary": "Key inventions, social changes, urbanization, and the shift from agrarian to industrial economies.",
        },
        {
            "id": 7,
            "title": "Nutrition and Diet",
            "summary": "Macronutrients, micronutrients, caloric needs, and evidence-based dietary guidelines.",
        },
    ]
    q = query.lower()
    matches = [a for a in kb if q in a["title"].lower() or q in a["summary"].lower()]
    return {"query": query, "results": matches[:max_results]}


@tool(
    "convert_units",
    "Convert between common units: temperature (C/F/K), distance (km/mi), weight (kg/lb)",
    {
        "type": "object",
        "properties": {
            "value": {"type": "number", "description": "Numeric value to convert"},
            "from_unit": {
                "type": "string",
                "description": "Source unit (C, F, K, km, mi, kg, lb)",
            },
            "to_unit": {
                "type": "string",
                "description": "Target unit (C, F, K, km, mi, kg, lb)",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
)
def convert_units(value, from_unit, to_unit):
    conversions = {
        ("C", "F"): lambda v: v * 9 / 5 + 32,
        ("F", "C"): lambda v: (v - 32) * 5 / 9,
        ("C", "K"): lambda v: v + 273.15,
        ("K", "C"): lambda v: v - 273.15,
        ("F", "K"): lambda v: (v - 32) * 5 / 9 + 273.15,
        ("K", "F"): lambda v: (v - 273.15) * 9 / 5 + 32,
        ("KM", "MI"): lambda v: v * 0.621371,
        ("MI", "KM"): lambda v: v / 0.621371,
        ("KG", "LB"): lambda v: v * 2.20462,
        ("LB", "KG"): lambda v: v / 2.20462,
    }
    key = (
        from_unit.upper() if len(from_unit) <= 2 else from_unit,
        to_unit.upper() if len(to_unit) <= 2 else to_unit,
    )
    fn = conversions.get(key)
    if not fn:
        return {"error": f"Cannot convert from '{from_unit}' to '{to_unit}'"}
    return {
        "value": value,
        "from": from_unit,
        "to": to_unit,
        "result": round(fn(value), 2),
    }
