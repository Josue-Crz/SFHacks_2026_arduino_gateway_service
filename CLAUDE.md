# CLAUDE.md - GreenSense Backend

## Project Overview

GreenSense is a hackathon MVP — a real-time environmental dashboard that reads indoor sensor data from an Arduino, fetches outdoor weather + AI insights from backboard.io, stores readings in Supabase (PostgreSQL), and serves everything to a React frontend via a Flask API.

**This is read-only, no authentication.** The frontend just displays data.

---

## Stack

- **Flask** — API server
- **Supabase** — hosted PostgreSQL for sensor readings
- **backboard-sdk** — AI insights AND structured outdoor weather data (JSON) via backboard.io
- **pyserial** — reads Arduino sensor data over USB serial
- **ngrok** — tunnels Flask to a public HTTPS URL for the deployed frontend

---

## Architecture

```
Arduino (USB serial) → Flask → Supabase (PostgreSQL)
                         ↕
                    backboard.io (weather + AI)
                         ↓
                    React Frontend (GET /latest, GET /analysis, POST /chat)
```

- Arduino sends temperature + humidity over serial
- Flask reads serial, stores in Supabase, serves to frontend
- Flask calls backboard.io for outdoor weather data and AI analysis
- Frontend never calls AI or backboard.io directly

---

## Dev Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors psycopg2-binary python-dotenv backboard-sdk pyserial

# Run
python app.py

# Tunnel (separate terminal)
ngrok http 5000
```

After starting ngrok, give the frontend team the HTTPS URL to set as `VITE_API_BASE_URL`.

---

## Environment Variables

All secrets go in `.env` (must be in `.gitignore`). Load with `python-dotenv`. Never hardcode or expose secrets in API responses.

```env
# Supabase (PostgreSQL)
SUPABASE_DB_URL=postgresql://postgres:<password>@<host>:5432/postgres

# backboard.io
BACKBOARD_API_KEY=your_backboard_api_key

# Serial port (Arduino)
SERIAL_PORT=/dev/cu.usbmodem14201
SERIAL_BAUD=9600

# Flask
FLASK_PORT=5000
FLASK_DEBUG=true

# Rate limiting
MAX_AI_CALLS_PER_HOUR=10
MAX_AI_CALLS_PER_DAY=50
```

---

## Supabase Schema

```sql
CREATE TABLE readings (
  id BIGSERIAL PRIMARY KEY,
  temperature NUMERIC(5,2) NOT NULL,
  humidity NUMERIC(5,2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Only indoor sensor data is stored. Outdoor weather is cached in-memory from backboard.io, not persisted.

---

## API Contract (CRITICAL — Frontend depends on these exact shapes)

### GET /latest

Returns the most recent sensor reading + outdoor weather.

```json
{
  "temperature": 72.5,
  "humidity": 45,
  "greenScore": 85,
  "timestamp": "2026-02-14T12:30:00Z",
  "outdoor": {
    "temperature": 68.2,
    "humidity": 55,
    "feelsLike": 67.1,
    "condition": "Clear",
    "city": "San Francisco"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `temperature` | number | Indoor temp in °F (from Arduino) |
| `humidity` | number | Indoor humidity % (from Arduino) |
| `greenScore` | number | 0–100, calculated environmental quality score |
| `timestamp` | string | ISO 8601 timestamp of the reading |
| `outdoor.temperature` | number | Outdoor temp in °F (from backboard.io) |
| `outdoor.humidity` | number | Outdoor humidity % |
| `outdoor.feelsLike` | number | Feels-like temp in °F |
| `outdoor.condition` | string | e.g. "Clear", "Clouds", "Rain" |
| `outdoor.city` | string | Location name |

**greenScore calculation:** Derive from indoor conditions — e.g. penalize extreme temps, high humidity, large indoor/outdoor delta. Keep the formula simple. Higher = better.

**Frontend polls this every 30 seconds.**

---

### GET /analysis

Returns AI-generated environmental analysis.

```json
{
  "recommendation": "Outdoor temp is 68°F — close to your indoor 72°F. Consider opening windows instead of running AC.",
  "environmentalRisk": "Low",
  "sustainabilityImpact": "Opening windows could save ~$2/day in cooling costs.",
  "acStatus": "likely_unnecessary",
  "tempDelta": 4.3
}
```

| Field | Type | Values / Description |
|-------|------|----------------------|
| `recommendation` | string | Actionable advice text |
| `environmentalRisk` | string | One of: `"Low"`, `"Medium"`, `"High"` |
| `sustainabilityImpact` | string | Explanation of environmental impact |
| `acStatus` | string | One of: `"likely_unnecessary"`, `"justified"`, `"recommended"` |
| `tempDelta` | number | Absolute difference between indoor and outdoor temp (°F) |

**Frontend polls this every 5 minutes.** Cache aggressively — don't call backboard.io AI on every request.

---

### POST /chat

Receives a user question with sensor context, returns an AI reply.

**Request:**
```json
{
  "message": "Should I open my windows?",
  "context": {
    "indoor": {
      "temperature": 72.5,
      "humidity": 45
    },
    "outdoor": {
      "temperature": 68.2,
      "humidity": 55,
      "feelsLike": 67.1,
      "condition": "Clear",
      "city": "San Francisco"
    }
  }
}
```

**Response:**
```json
{
  "reply": "It's 68°F outside and 72°F inside — only a 4°F difference. Opening windows would save energy."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | User's question |
| `context` | object (optional) | Current sensor data for AI context |
| `reply` | string | AI-generated response |

Send `message` + `context` to backboard.io as a prompt. The AI should answer as a sustainability-focused environmental advisor.

---

### Storing Sensor Data (Internal)

`store_reading(temperature, humidity)` is an internal Python function called by the serial reader thread — **not** an HTTP endpoint. It inserts a row into the `readings` table and updates the in-memory latest reading cache.

---

## Serial Integration (Arduino)

- Arduino sends `temperature,humidity\n` over USB serial (e.g. `72.5,45.2`)
- Use `pyserial` to read from `SERIAL_PORT` at `SERIAL_BAUD` (default 9600)
- Run in a **background thread** so it doesn't block Flask
- On each line: parse, call `store_reading()`, update in-memory latest reading
- If serial port is unavailable: log a warning and serve the last known reading (don't crash)

---

## backboard.io Integration

`pip install backboard-sdk` — the SDK is **async**, so Flask routes need `asyncio.run()` or a sync wrapper.

### SDK Pattern

```python
from backboard import BackboardClient
import asyncio, json

client = BackboardClient(api_key=os.getenv('BACKBOARD_API_KEY'))

# 1. Create an assistant with the weather tool
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]

assistant = await client.create_assistant(
    name="GreenSense Advisor",
    system_prompt="You are a sustainability-focused environmental advisor...",
    tools=tools
)

# 2. Create a thread and send a message
thread = await client.create_thread(assistant.assistant_id)
response = await client.add_message(
    thread_id=thread.thread_id,
    content="Analyze indoor 72°F/45% vs outdoor conditions in San Francisco",
    stream=False
)

# 3. Handle tool calls (REQUIRES_ACTION)
if response.status == "REQUIRES_ACTION" and response.tool_calls:
    tool_outputs = []
    for tc in response.tool_calls:
        if tc.function.name == "get_current_weather":
            location = tc.function.parsed_arguments["location"]
            # Fetch real weather data and return as JSON
            weather = {"temperature": "68°F", "humidity": "55%", "condition": "Clear"}
            tool_outputs.append({
                "tool_call_id": tc.id,
                "output": json.dumps(weather)
            })

    # Submit outputs to get the final AI response
    final = await client.submit_tool_outputs(
        thread_id=thread.thread_id,
        run_id=response.run_id,
        tool_outputs=tool_outputs
    )
    print(final.content)  # AI recommendation text
```

### How This Maps to Endpoints

- **`/latest` → outdoor weather:** The `get_current_weather` tool call returns structured weather JSON. Cache this for 10–15 min and serve in the `outdoor` field.
- **`/analysis`:** Send a prompt with indoor sensor data. The assistant calls the weather tool, gets outdoor data, then generates a recommendation. Parse `final.content` to extract `recommendation`, `environmentalRisk`, `acStatus`, `sustainabilityImpact`.
- **`/chat`:** Create a thread, send the user's message with sensor context in the prompt. Return `final.content` as the reply.

### Assistant Lifecycle

Create the assistant **once** on app startup. Create a new thread for each `/analysis` or `/chat` request. Reuse the assistant ID across all threads.

---

## AI Usage Controls (Rate Limiting)

Prevent burning through AI tokens during the hackathon:

| Rule | Value |
|------|-------|
| Max AI calls per hour | 10 |
| Max AI calls per day | 50 |
| Min interval between `/analysis` AI calls | 10 minutes |
| Trigger new analysis if | temp delta > 3°F OR humidity delta > 5% |
| If limit exceeded | Return cached last response |
| Cache `/analysis` result | In memory + optionally in Supabase |

**Chat (`/chat`) also counts against rate limits.** If limits are hit, return a friendly message like "I've reached my analysis limit. Please try again in a few minutes."

---

## Data Flow & Caching

| Data | Source | Cache TTL | Notes |
|------|--------|-----------|-------|
| Indoor sensors | Arduino serial | Real-time (in-memory) | Update on every serial read |
| Outdoor weather | backboard.io | 10–15 min | Don't refetch on every `/latest` call |
| AI analysis | backboard.io | 10 min or until delta threshold | See rate limiting rules above |
| Chat replies | backboard.io | No cache | Each chat is unique |
| greenScore | Calculated | Recalculate on each `/latest` | Derived from indoor + outdoor data |

---

## Error Handling

- If Arduino is disconnected: serve last known reading, set a flag, don't crash
- If backboard.io is down: return cached analysis, return `null` for outdoor weather
- If Supabase is down: serve from in-memory cache, log error
- All endpoints should return proper HTTP status codes (200, 500, etc.)
- Never expose stack traces or secrets in error responses

---

## CORS Configuration

The frontend runs on a different port/domain. Enable CORS:

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

Allow all origins for the hackathon. In production you'd restrict this.

---

## Sustainability Framing

GreenSense encourages:
- Passive cooling (open windows instead of AC when outdoor temp is close)
- Reducing HVAC waste
- Detecting mold risk (high humidity alerts)
- Improving indoor energy efficiency

All AI prompts should frame recommendations around sustainability and energy savings.

