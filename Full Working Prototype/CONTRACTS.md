\# AURA — Data Contracts



Shared JSON schemas between layers. Do not change field names without notifying the whole team.



\## 1. Vision Output (Shruti → Backend)

```json

{

&#x20; "timestamp": "2026-08-26T10:15:30Z",

&#x20; "intersection\_id": "vadapalani\_junction",

&#x20; "zone": "north\_approach",

&#x20; "counts": {

&#x20;   "car": 12,

&#x20;   "bus": 2,

&#x20;   "truck": 1,

&#x20;   "motorcycle": 8,

&#x20;   "bicycle": 3,

&#x20;   "person": 15

&#x20; },

&#x20; "platoon\_detected": false,

&#x20; "ev\_detected": \[]

}

```



\## 2. TomTom Output (Shruti → Backend)

```json

{

&#x20; "timestamp": "2026-08-26T10:15:30Z",

&#x20; "segment\_id": "arcot\_road\_north",

&#x20; "current\_speed\_kmh": 18,

&#x20; "free\_flow\_speed\_kmh": 45,

&#x20; "congestion\_ratio": 0.6

}

```



\## 3. Engine Output (Tharanesh → Backend)

```json

{

&#x20; "timestamp": "2026-08-26T10:15:30Z",

&#x20; "intersection\_id": "vadapalani\_junction",

&#x20; "phase\_durations": {

&#x20;   "north\_south\_green": 32,

&#x20;   "east\_west\_green": 28,

&#x20;   "pedestrian\_crossing\_green": 15

&#x20; },

&#x20; "priority\_mode": "normal",

&#x20; "vui\_score": 42

}

```

`priority\_mode` is one of: `normal | vulnerable\_user | emergency\_vehicle`



\## 4. EV Conflict Event (Shruti/Tharanesh → Backend)

```json

{

&#x20; "timestamp": "2026-08-26T10:15:30Z",

&#x20; "ev\_id": "ev\_1",

&#x20; "distance\_to\_stopline\_m": 120,

&#x20; "velocity\_kmh": 40,

&#x20; "tti\_seconds": 10.8,

&#x20; "priority\_rank": "EV-1"

}

```



\## Demo Intersection

\- Name: Vadapalani Junction, Chennai

\- Coordinates: 13.0505, 80.2121

