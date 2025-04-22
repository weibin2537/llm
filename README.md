chatbox/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── NOTES.txt
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── model/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── istio/
│   │   ├── gateway.yaml
│   │   └── virtualservice.yaml
│   └── monitoring/
│       ├── servicemonitor.yaml
│       └── prometheusrule.yaml
└── charts/
    └── dependencies if needed

    系统架构
