import socket
import threading
import time
import json
import numpy as np
from flask import Flask, jsonify, request, send_file
import io
import pandas as pd
from protocol import pack_message, unpack_message

app = Flask(__name__)

# ================= CONFIG =================
HOST = "0.0.0.0"
PORT = 10000
EXPECTED_CLIENTS = 2
MAX_ROUNDS = 20

# ================= 全局系统状态 =================
system_status = "IDLE" # IDLE, RUNNING, PAUSED, FINISHED

lock = threading.Lock()
clients = {}         # cid -> conn
buffers = {}         # cid -> last data
pi_monitors = {}     # 维护各个在线树莓派的硬件运行状态字典 (cid -> dict)

round_id = 1
history_rounds = []
history_loss = []
history_acc = []
global_weights_cache = None 

# ================= SOCKET NETWORK LAYER =================
def handle_client(conn):
    global clients, buffers, pi_monitors
    cid = None
    try:
        while True:
            res = unpack_message(conn)
            if res is None: break
            if isinstance(res, tuple) and len(res) == 2:
                header, data = res
            else: continue

            if not header or "client_id" not in header: continue
            cid = header["client_id"]

            with lock:
                clients[cid] = conn
                
                # 💡 核心修改点：无论何种类型的消息，只要带有 status_info，都实时刷新监视器
                if "status_info" in header:
                    status_data = header["status_info"]
                    status_data["last_seen"] = time.strftime("%H:%M:%S", time.localtime())
                    pi_monitors[cid] = status_data
                elif cid not in pi_monitors:
                    pi_monitors[cid] = {"cpu": 0.0, "mem": 0.0, "temp": 0.0, "last_seen": "仅握手"}

                # ⚠️ 核心安全机制：只有显式声明为 DATA_REPORT 且包含权重时，才计入训练聚合缓冲区
                if header.get("type") == "DATA_REPORT" and data and "weights" in data:
                    buffers[cid] = (header, data)
                
    except Exception as e:
        print(f"[SERVER] 客户端 {cid} 断开连接: {e}")
    finally:
        with lock:
            clients.pop(cid, None)
            buffers.pop(cid, None)
            pi_monitors.pop(cid, None) # 掉线时一并清除监控缓存
        try: conn.close()
        except: pass

def check_ready():
    with lock:
        return len(buffers) >= EXPECTED_CLIENTS

def fedavg(all_data):
    total = sum(payload["data_size"] for _, payload in all_data)
    W, b = None, None
    loss, acc = 0, 0
    for header, payload in all_data:
        size = payload["data_size"]
        weights = payload["weights"]
        w = np.array(weights["W"], np.float32) * size / total
        bb = np.array(weights["b"], np.float32).flatten() * size / total
        W = w if W is None else W + w
        b = bb if b is None else b + bb
        loss += payload["loss"] * size / total
        acc += payload["acc"] * size / total
    return {"W": W.tolist(), "b": b.tolist()}, loss, acc

def broadcast_command(command_type, payload_data=None):
    header = {"round": round_id, "type": command_type}
    for cid, conn in list(clients.items()):
        try:
            conn.sendall(pack_message(header, payload_data))
            print(f"[SERVER] 已向客户端 {cid} 下发指令: {command_type}")
        except:
            with lock:
                clients.pop(cid, None)
                buffers.pop(cid, None)

# ================= FL CORE TRAINING LOOP =================
def training_loop():
    global round_id, buffers, system_status, history_rounds, history_loss, history_acc, global_weights_cache

    while True:
        time.sleep(0.1)
        if system_status in ["IDLE", "PAUSED", "FINISHED"]:
            continue
        if not check_ready():
            continue

        print(f"\n=================== GLOBAL ROUND {round_id} ===================")
        with lock:
            current_round_data = []
            for cid in list(clients.keys()):
                if cid in buffers:
                    current_round_data.append(buffers[cid])
                    del buffers[cid] 

        try:
            global_model, loss, acc = fedavg(current_round_data)
            global_weights_cache = global_model 
            
            with lock:
                history_rounds.append(round_id)
                history_loss.append(float(loss))
                history_acc.append(float(acc))

            round_id += 1
            if round_id > MAX_ROUNDS:
                system_status = "FINISHED"
                broadcast_command("SET_MODEL", global_model)
                print(f"[SERVER] 训练已满 {MAX_ROUNDS} 轮。已进入就绪等待状态。")
            else:
                broadcast_command("SET_MODEL", global_model)
            
        except Exception as e:
            print(f"[SERVER ERR] 聚合失败: {e}")
            continue

def socket_accept_server(sock):
    while True:
        try:
            conn, _ = sock.accept()
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
        except:
            pass

# ================= FLASK HTTP CONTROL INTERFACE =================
@app.route('/api/status', methods=['GET'])
def get_status():
    with lock:
        return jsonify({
            "status": system_status,
            "current_round": round_id - 1 if system_status == "FINISHED" else round_id,
            "max_rounds": MAX_ROUNDS,
            "connected_clients": list(clients.keys()), 
            "client_count": len(clients),
            "pi_monitors": pi_monitors, 
            "history_rounds": history_rounds,
            "history_loss": history_loss,
            "history_acc": history_acc
        })

@app.route('/api/control', methods=['POST'])
def control_server():
    global system_status, MAX_ROUNDS
    action = request.json.get("action")
    
    with lock:
        if action == "start" and system_status == "IDLE":
            if len(clients) < EXPECTED_CLIENTS:
                return jsonify({"success": False, "msg": f"启动失败：当前仅有 {len(clients)} 台设备在线。"})
            system_status = "RUNNING"
            broadcast_command("CMD_RESUME", global_weights_cache) 
        elif action == "pause" and system_status == "RUNNING":
            system_status = "PAUSED"
            broadcast_command("CMD_PAUSE") 
        elif action == "resume" and system_status == "PAUSED":
            system_status = "RUNNING"
            broadcast_command("CMD_RESUME") 
        elif action == "extend" and system_status == "FINISHED":
            additional_rounds = int(request.json.get("additional_rounds", 10))
            MAX_ROUNDS += additional_rounds
            system_status = "RUNNING"
            broadcast_command("CMD_RESUME", global_weights_cache)
        else:
            return jsonify({"success": False, "msg": "非法的状态转换"})
    return jsonify({"success": True, "current_status": system_status})

@app.route('/api/export', methods=['GET'])
def export_data():
    with lock:
        df = pd.DataFrame({
            "Round": history_rounds,
            "Global_Loss": history_loss,
            "Global_Accuracy": history_acc
        })
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name=f"FL_Report_{int(time.time())}.csv")

if __name__ == "__main__":
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(10)

    threading.Thread(target=socket_accept_server, args=(sock,), daemon=True).start()
    threading.Thread(target=training_loop, daemon=True).start()

    print("[SERVER] 带有双向集群控制与多维监控数据 API 已就绪")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)