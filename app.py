import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="联邦学习分布式高级控制台", layout="wide")
BACKEND_URL = "http://127.0.0.1:5000/api"

st.title("🌐 工业级树莓派联邦学习中央控制中心")
st.markdown("---")

def fetch_data():
    try:
        response = requests.get(f"{BACKEND_URL}/status")
        if response.status_code == 200: return response.json()
    except:
        st.error("无法连接到后端联邦服务器，请检查 server.py 是否正常启动！")
    return None

data = fetch_data()

if data:
    status_mapping = {
        "IDLE": "⚪ 未开始 (集群待命)",
        "RUNNING": "🟢 正在训练 (正在双向同步)",
        "PAUSED": "🟡 已暂停 (两台树莓派已挂起)",
        "FINISHED": "🏁 阶段任务完成 (等待追加或结束)"
    }
    
    # 顶部基础指标状态看板
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("系统当前状态", status_mapping.get(data["status"], "未知"))
    with col2:
        st.metric("训练进度 (Rounds)", f"{data['current_round']} / {data['max_rounds']}")
    with col3:
        st.metric("在线设备数量", f"{data['client_count']} 台")

    if data["client_count"] > 0:
        st.caption(f"当前连入的客户端 ID: {', '.join(data['connected_clients'])}")
    else:
        st.caption("⚠️ 暂无树莓派节点连接，请启动树莓派客户端...")

    st.markdown("---")

    # ================= 🌟 树莓派集群资源监控卡片区 =================
    st.subheader("🛠️ 边缘计算资源与健康度监视器")
    monitors = data.get("pi_monitors", {})
    
    if data["client_count"] > 0 and monitors:
        # 根据当前连接设备数，自适应动态分栏展示
        pi_cols = st.columns(len(monitors))
        
        for idx, (cid, info) in enumerate(monitors.items()):
            with pi_cols[idx]:
                with st.container(border=True):
                    st.markdown(f"### 📱 节点设备: `{cid}`")
                    st.markdown(f"⏱️ **最后活跃时间:** `{info.get('last_seen', 'N/A')}`")
                    
                    # 提起监控核心参数
                    cpu_val = info.get("cpu", 0.0)
                    mem_val = info.get("mem", 0.0)
                    temp_val = info.get("temp", 0.0)
                    
                    # 1. CPU 使用率监控
                    st.write(f"💻 **CPU 使用率:** {cpu_val}%")
                    st.progress(min(max(int(cpu_val), 0), 100) / 100.0)
                    
                    # 2. 内存 占用率监控
                    st.write(f"💾 **内存 占用率:** {mem_val}%")
                    st.progress(min(max(int(mem_val), 0), 100) / 100.0)
                    
                    # 3. CPU 核心温度安全状态反馈 (联动功耗状态展示)
                    if temp_val > 75.0:
                        st.error(f"🔥 **核心温度:** {temp_val} °C (处于极端高热负荷，请注意散热!)")
                    elif temp_val > 60.0:
                        st.warning(f"⚠️ **核心温度:** {temp_val} °C (处于训练发热区间，温控偏高)")
                    elif temp_val == 0.0:
                        st.info(f"❄️ **核心温度:** {temp_val} °C (处于模拟测试环境)")
                    else:
                        st.success(f"❄️ **核心温度:** {temp_val} °C (温控稳定，运行状态良好)")
    else:
        st.info("💡 暂时无状态数据上报。当树莓派建立连接并触发本地计算后，这里将实时更新设备的功耗健康度指标。")

    st.markdown("---")

    # 控制按钮区
    st.subheader("🕹️ 联邦集群控制")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("🚀 开始训练", use_container_width=True, disabled=(data["status"] != "IDLE")):
            requests.post(f"{BACKEND_URL}/control", json={"action": "start"})
            st.rerun()
    with btn_col2:
        if st.button("⏸️ 暂停训练", use_container_width=True, disabled=(data["status"] != "RUNNING")):
            requests.post(f"{BACKEND_URL}/control", json={"action": "pause"})
            st.rerun()
    with btn_col3:
        if st.button("▶️ 继续训练", use_container_width=True, disabled=(data["status"] != "PAUSED")):
            requests.post(f"{BACKEND_URL}/control", json={"action": "resume"})
            st.rerun()

    # 无缝追加训练轮数
    if data["status"] == "FINISHED":
        st.success("🎉 前20轮指标已收敛！您可以在下方无缝追加训练轮数：")
        extend_col1, extend_col2 = st.columns([1, 4])
        with extend_col1:
            add_rounds = st.number_input("追加轮数", min_value=5, max_value=100, value=10, step=5)
        with extend_col2:
            st.write("") 
            st.write("") 
            if st.button("⚡ 确认追加训练并恢复通知", type="primary"):
                requests.post(f"{BACKEND_URL}/control", json={"action": "extend", "additional_rounds": add_rounds})
                st.rerun()

    st.markdown("---")

    # 数据图表与下载区
    st.subheader("📈 实时收敛指标曲线")
    if len(data["history_rounds"]) > 0:
        df = pd.DataFrame({
            "Round": data["history_rounds"],
            "Loss": data["history_loss"],
            "Accuracy": data["history_acc"]
        }).set_index("Round")
        
        c1, c2 = st.columns(2)
        with c1: st.line_chart(df["Loss"], color="#ff4d4d")
        with c2: st.line_chart(df["Accuracy"], color="#1e90ff")
        
        st.markdown("### 💾 实验数据归档")
        try:
            csv_res = requests.get(f"{BACKEND_URL}/export")
            if csv_res.status_code == 200:
                st.download_button(
                    label="📥 导出完整实验指标为 CSV 文件",
                    data=csv_res.content,
                    file_name=f"FL_Metrics_Report_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except:
            st.warning("数据导出生成中...")
    else:
        st.info("暂无数据。")

    # 💡 核心修改点：移除旧代码的状态过滤拦截。
    # 任何状态下（包含待命、完成），控制台都将保持 1 秒的间隔进行全局刷新，从而保证监控条的持续跳动。
    time.sleep(1.0)
    st.rerun()