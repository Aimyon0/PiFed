# Raspberry Pi Federated Learning Platform

A lightweight federated learning platform built on Raspberry Pi, supporting distributed model training, centralized aggregation, real-time device monitoring, and a web-based management dashboard.

---

## Features

- Federated Averaging (FedAvg)
- Distributed training on multiple Raspberry Pi nodes
- Automatic client reconnection
- Real-time CPU, memory and temperature monitoring
- Web dashboard based on Streamlit
- Flask RESTful backend
- Training control (Start / Pause / Resume)
- Dynamic training round extension
- CSV export of training metrics
- Heterogeneous client support
  - NumPy implementation
  - PyTorch implementation

---

## System Architecture

```
                +----------------------+
                |  Streamlit Dashboard |
                +----------+-----------+
                           |
                     REST API
                           |
                    +------+------+
                    | Flask Server |
                    +------+------+
                           |
                 Federated Learning Server
                           |
          +----------------+----------------+
          |                                 |
   Raspberry Pi 1                    Raspberry Pi 2
  (NumPy Client)                  (PyTorch Client)
          |                                 |
   Local Training                     Local Training
          +---------------+-----------------+
                          |
                   Federated Averaging
```

---

## Project Structure

```
.
├── server.py              # Federated learning server
├── dashboard.py           # Streamlit dashboard
├── protocol.py            # Communication protocol
├── client_pi1.py          # NumPy client
├── client_pi2.py          # PyTorch client
├── mnist_data/
│   ├── X_train.npy
│   └── y_train.npy
└── README.md
```

---

## Requirements

Python 3.10+

Install dependencies

```bash
pip install flask
pip install streamlit
pip install numpy
pip install pandas
pip install matplotlib
pip install torch
pip install psutil
```

---

## Run

### Start the server

```bash
python server.py
```

---

### Launch the dashboard

```bash
streamlit run dashboard.py
```

---

### Raspberry Pi Client 1

```bash
python client_pi1.py
```

---

### Raspberry Pi Client 2

```bash
python client_pi2.py
```

---

## Dashboard

The dashboard provides

- Device connection status
- CPU utilization
- Memory utilization
- CPU temperature
- Current training round
- Global loss
- Global accuracy
- Training control
- CSV export

---

## Federated Learning Workflow

1. Clients connect to the server.
2. The server distributes the global model.
3. Clients perform local training.
4. Local parameters are uploaded.
5. The server performs FedAvg aggregation.
6. Updated global parameters are broadcast.
7. Repeat until the specified number of rounds is completed.

---

## Technologies

- Python
- Flask
- Streamlit
- NumPy
- PyTorch
- Socket Programming
- Multithreading
- Federated Learning (FedAvg)
- Raspberry Pi

---

## Future Work

- Secure Aggregation
- Differential Privacy
- Asynchronous Federated Learning
- Client Selection
- CNN / Transformer models
- MQTT communication
- Docker deployment

---

## License

MIT License
