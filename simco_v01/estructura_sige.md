backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── jwt.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── solicitud.py
│   │   ├── respuesta.py
│   │   └── audit.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── solicitud.py
│   │   └── auth.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── solicitudes.py
│   │   │   └── respuestas.py
│   │   │
│   │   └── api.py
│   │
│   └── services/
│       ├── auth_service.py
│       ├── solicitud_service.py
│       └── respuesta_service.py
│
├── requirements.txt
└── .env
