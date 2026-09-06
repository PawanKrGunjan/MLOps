># Requests per second (RPS) an API handle while maintaining an acceptable response time and error rate

## 1. First understand the concepts

There are several different numbers you should measure.

### RPS / Throughput

**Requests Per Second (RPS)** = how many requests the API successfully processes per second.

For example:

```text
100 requests/sec
```

means your API processed approximately 100 POST requests every second.

---

### Concurrent users / connections

Suppose we have:

```text
100 concurrent users
```

It does **not** mean 100 requests/sec.

If each request takes 100 ms, theoretically:

```text
100 concurrent requests / 0.1 sec
≈ 1000 requests/sec
```

This is why **concurrency and RPS are different concepts**.

---

### Latency

Latency is how long one request takes.

For example:

```text
Average: 8 ms
p50:      6 ms
p95:     15 ms
p99:     40 ms
```

The percentiles are particularly important.

**p95 = 95% of requests completed within that time.**

---

### Error rate

Example:

```text
10,000 requests
9,950 successful
50 failed

Error rate = 0.5%
```

For a production API, you normally don't want to define capacity based only on throughput. You also need an acceptable error rate and latency.

---

## 2. API

The endpoint is:

```text
POST /calculate
```

with:

```json
{
  "num1": 20,
  "symbol": "+",
  "num2": 30
}
```

and should return:

```json
{
  "result": 50
}
```

The FastAPI application is currently started with:

```python
uvicorn.run(
    "Ganesh:app",
    host="127.0.0.1",
    port=8000,
    reload=True
)
```

according to the uploaded file. 

There is one **very important point** here:

### Don't benchmark with `reload=True`

`reload=True` is a development feature and should not be used for a meaningful performance benchmark.

Change your development/test server to:

```bash
uvicorn Ganesh:app --host 127.0.0.1 --port 8000
```

or:

```python
uvicorn.run(
    "Ganesh:app",
    host="127.0.0.1",
    port=8000
)
```

---

# 3. Recommended approach

I recommend using **Locust** for this.

The progression should be:

```text
API
 ↓
Baseline test
 ↓
Small load
 ↓
Increase load
 ↓
Find saturation point
 ↓
Measure latency
 ↓
Measure errors
 ↓
Find maximum sustainable RPS
 ↓
Test with multiple workers
 ↓
Determine production capacity
```

---

# 4. Install Locust

Create/activate your virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Then:

```bash
pip install locust
```

Verify:

```bash
locust --version
```

---

# 5. Create a load-test script

Create:

```text
locustfile.py
```

Put this in it:

```python
from locust import HttpUser, task, between


class CalculatorUser(HttpUser):

    wait_time = between(0.01, 0.05)

    @task
    def calculate(self):
        self.client.post(
            "/calculate",
            json={
                "num1": 20,
                "symbol": "+",
                "num2": 30
            }
        )
```

The important part is:

```python
self.client.post(
    "/calculate",
    json={
        "num1": 20,
        "symbol": "+",
        "num2": 30
    }
)
```

This is essentially automating your curl request.

---

# 6. Start your API

Terminal 1:

```bash
uvicorn Ganesh:app --host 127.0.0.1 --port 8000
```

Test manually:

```bash
curl -X POST \
  'http://127.0.0.1:8000/calculate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "num1": 20,
    "symbol": "+",
    "num2": 30
  }'
```

Expected:

```json
{"result":50}
```

---

# 7. Start Locust

Terminal 2:

```bash
locust -f locustfile.py --host http://127.0.0.1:8000
```

Then open:

```text
http://127.0.0.1:8089
```

You will get the Locust UI.

---

# 8. Start with a small load

Don't immediately throw 10,000 users at it.

Start with:

```text
Users:       10
Spawn rate:  2 users/sec
```

Run for approximately:

```text
1-2 minutes
```

Observe:

```text
Requests
Failures
RPS
Average latency
p95
p99
```

You might see something like:

```text
Users       RPS       Avg      p95       Errors
------------------------------------------------
10          500       18 ms    30 ms     0%
```

Those numbers are just examples — **do not treat them as your API's actual performance**.

---

# 9. Increase the load gradually

Now run:

### Test 1

```text
10 users
```

### Test 2

```text
25 users
```

### Test 3

```text
50 users
```

### Test 4

```text
100 users
```

### Test 5

```text
200 users
```

### Test 6

```text
500 users
```

Continue until performance starts degrading.

Create a table like:

| Concurrent users | RPS | Avg latency | p95 | p99 | Errors |
| ---------------: | --: | ----------: | --: | --: | -----: |
|               10 |   ? |           ? |   ? |   ? |      ? |
|               25 |   ? |           ? |   ? |   ? |      ? |
|               50 |   ? |           ? |   ? |   ? |      ? |
|              100 |   ? |           ? |   ? |   ? |      ? |
|              200 |   ? |           ? |   ? |   ? |      ? |
|              500 |   ? |           ? |   ? |   ? |      ? |

This table becomes your **capacity profile**.

---

# 10. What are you actually looking for?

Imagine you get:

```text
10 users     → 1,000 RPS
50 users     → 4,500 RPS
100 users    → 6,500 RPS
200 users    → 7,000 RPS
500 users    → 7,100 RPS
```

You might initially think:

> Maximum = 7,100 RPS

Not necessarily.

Now look at latency:

```text
Users       RPS       p95
--------------------------------
10          1,000     5 ms
50          4,500     8 ms
100         6,500     15 ms
200         7,000     80 ms
500         7,100     900 ms
```

The API has technically achieved 7,100 RPS, but it's becoming extremely slow.

So the **useful capacity** may be around:

```text
6,000-6,500 RPS
```

depending on your latency requirement.

---

# 11. Define an SLA/SLO before declaring "maximum"

This is extremely important.

For example, you could define:

```text
Success rate >= 99.9%
p95 latency <= 100 ms
p99 latency <= 200 ms
```

Then your definition becomes:

> Maximum sustainable capacity = highest RPS at which error rate and latency remain within the defined limits.

For example:

```text
                 Sustainable
                      ↓
RPS →  1000  2000  3000  4000  5000  6000  7000
       |     |     |     |     |     |     |
p95 →  5ms   6ms   8ms   12ms  20ms  60ms  500ms
Errors→ 0     0     0     0     0     .01%  2%
```

Your capacity might therefore be:

```text
~6,000 RPS
```

rather than 7,000.

---

# 12. Understand the "knee point"

A very useful concept in load testing is the **knee point**.

Initially:

```text
Load ↑
Latency → remains relatively flat
```

Eventually:

```text
Load ↑
Latency ↑ rapidly
```

That point is where your system begins approaching saturation.

Conceptually:

```text
Latency
   │
   │                         /
   │                       /
   │                    __/
   │                 __/
   │____________ ____/
   │
   └────────────────────────── Load
                     ↑
                  knee point
```

You generally don't want production traffic operating right at this point.

---

# 13. Monitor the machine while testing

This is just as important as Locust.

While running the test, monitor:

```bash
top
```

or:

```bash
htop
```

Look at:

```text
CPU
Memory
Load average
```

You can also use:

```bash
free -h
```

and:

```bash
uptime
```

For your particular calculator API, I would expect CPU/server overhead to become much more interesting than the actual calculation itself, because the calculation is extremely cheap.

Your actual calculation is basically:

```python
return self.num1 + self.num2
```

for addition. 

So this test is largely testing:

```text
HTTP
↓
Uvicorn
↓
FastAPI
↓
Pydantic validation
↓
Python function
↓
JSON serialization
↓
HTTP response
```

rather than mathematical computation.

---

# 14. Very important: localhost testing has a limitation

You're currently testing:

```text
Client
   ↓
127.0.0.1
   ↓
FastAPI
```

If Locust and FastAPI are running on the **same machine**, they compete for CPU.

So you are partly measuring:

```text
FastAPI performance
+
Locust performance
+
OS/network overhead
```

This is okay for initial testing.

But for a serious benchmark, use:

```text
Load generator machine
        ↓
     Network
        ↓
API server
```

For example:

```text
Machine A
Locust
10.0.0.10
     │
     │ HTTP
     ▼
Machine B
FastAPI
10.0.0.20
```

This gives you a much cleaner result.

---

# 15. Then test Uvicorn workers

Your current setup effectively has one worker.

Once you understand single-worker performance, test multiple workers.

For example:

```bash
uvicorn Ganesh:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4
```

Then repeat exactly the same test.

Compare:

```text
                    1 worker       4 workers
------------------------------------------------
RPS                   ?               ?
p95                   ?               ?
p99                   ?               ?
CPU                   ?               ?
Errors                ?               ?
```

This is particularly useful because FastAPI itself doesn't magically make Python code execute across all CPU cores in one worker.

Multiple worker processes allow the application to utilize multiple CPU cores.

---

# 16. Don't just do a "maximum blast"

There are actually several useful types of load tests.

### A. Baseline test

Very small load.

Purpose:

```text
What is the normal latency?
```

---

### B. Load test

Expected production load.

Example:

```text
500 RPS
```

Purpose:

> Does the API comfortably handle normal traffic?

---

### C. Stress test

Gradually increase load.

Example:

```text
100
200
500
1000
2000
5000
...
```

Purpose:

> Where does performance start degrading?

---

### D. Spike test

Suddenly jump:

```text
100 RPS
       ↓
     5000 RPS
```

Purpose:

> How does the API behave during a sudden traffic spike?

---

### E. Soak/endurance test

Run a realistic load for a long time:

```text
1 hour
```

or:

```text
4 hours
```

Purpose:

> Does performance degrade over time?

This can reveal:

* memory leaks
* resource exhaustion
* connection problems
* gradual performance degradation

---

# 17. A good test plan for your API

I would use this exact progression.

### Phase 1 — Baseline

```text
10 users
2 minutes
```

Record:

```text
RPS
avg
p95
p99
errors
CPU
memory
```

---

### Phase 2 — Capacity discovery

Run:

```text
10
25
50
100
200
500
1000
2000
```

until you see significant degradation.

---

### Phase 3 — Narrow down

Suppose degradation begins somewhere between:

```text
500
```

and:

```text
1000
```

Test:

```text
600
700
800
900
1000
```

This gives you a much more accurate maximum.

---

### Phase 4 — Find sustainable limit

Suppose:

```text
800 users → 5,500 RPS → p95 50ms → 0% errors

900 users → 6,000 RPS → p95 80ms → 0% errors

1000 users → 6,100 RPS → p95 250ms → 0.5% errors
```

If your target is:

```text
p95 < 100ms
error < 0.1%
```

then:

```text
~6,000 RPS
```

is your approximate sustainable capacity.

---

# 18. One more important distinction: maximum vs safe maximum

Suppose your absolute maximum is:

```text
6,000 RPS
```

You probably shouldn't configure your production system to operate permanently at:

```text
6,000 RPS
```

because there is no headroom.

You might choose:

```text
Maximum measured:     6,000 RPS
Safe operating limit: 4,500 RPS
```

giving you:

```text
25% headroom
```

or whatever margin your architecture requires.

---

# 19. For your specific calculator API

Because your `/calculate` endpoint has essentially no I/O, this test will primarily tell you the capacity of:

```text
FastAPI + Uvicorn + Python + Pydantic + JSON
```

It **will not tell you** how many requests your eventual application can handle if you later add things like:

```text
Database
Redis
External API
LLM
File processing
Stock market API
Complex calculations
```

For example:

```text
POST /calculate
       ↓
   5,000 RPS
```

doesn't imply:

```text
POST /portfolio-analysis
       ↓
   5,000 RPS
```

Those are completely different workloads.

---

# 20. The final result you want

At the end, don't report:

> "My API can handle 10,000 requests."

Instead report something like:

> **On a machine with X CPU cores and Y GB RAM, using 4 Uvicorn workers, the `/calculate` endpoint sustained approximately 6,000 RPS with p95 latency below 100 ms and an error rate below 0.1%. Performance degraded significantly beyond approximately 6,500 RPS.**

That is a meaningful load-test result.

---

## Recommended architecture for your experiment

```text
                 ┌──────────────────┐
                 │     Locust       │
                 │  Load Generator  │
                 └────────┬─────────┘
                          │
                          │ HTTP POST
                          │ /calculate
                          ▼
                 ┌──────────────────┐
                 │     Uvicorn      │
                 │                  │
                 │   Worker 1       │
                 │   Worker 2       │
                 │   Worker 3       │
                 │   Worker 4       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     FastAPI      │
                 │                  │
                 │  Pydantic        │
                 │  Calculator      │
                 │  JSON Response   │
                 └──────────────────┘

       Monitor:
       ├── RPS
       ├── p50
       ├── p95
       ├── p99
       ├── Error %
       ├── CPU %
       └── Memory
```